import os
from pickle import dump
from pickle import load
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.text import Tokenizer
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
import string
from numpy import array
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.utils import plot_model
from keras.models import Model
from keras.layers import Input
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding
from keras.layers import Dropout
from keras.layers.merge import add
from keras.callbacks import ModelCheckpoint
from keras.layers import Flatten
import numpy as np
import os
os.environ["PATH"] += os.pathsep + 'path_to\Graphviz2.38/bin/'
from keras.layers.pooling import GlobalMaxPooling2D
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras.layers.merge import concatenate
from keras.layers import Flatten


# image_to_features
class images_to_features():
    def __init__(self,directory,path_to_save_features):
        self.model=VGG16()
        self.directory=directory
        self.path_to_save_features=path_to_save_features

    def extract_features(self):
        # removing softmax at the end
        self.model.layers.pop()
        model= Model(inputs=self.model.inputs,outputs=self.model.layers[-1].output)
        features=dict()
        for name in os.listdir(self.directory):
            filename=self.directory+'/'+name
            image=load_img(filename,target_size=(224,224))
            image=img_to_array(image)
            image=image.reshape((1,image.shape[0],image.shape[1],image.shape[2]))
            image=preprocess_input(image)
            feature=model.predict(image,verbose=0)
            image_id=name.split('.')[0]
            features[image_id]=feature
            dump(features,open(self.path_to_save_features),'wb')


# preprocess the descriptions removing puncuations and 's in from the descriptions and saving it locally
class preprocess_descriptions():
    def __init__(self,path_to_descriptions,path_to_save_descriptions):
        self.path=path_to_descriptions
        self.path_to_save_desc=path_to_save_descriptions

    def load_descriptions(self):
        with open(self.path) as file:
            captions_file=file.read()
        captions_list = captions_file.split('\n')
        descriptions=dict()
        desc=[]
        count=1
        number_images=set()
        for i in range(0, len(captions_list), 1):
            tokens = captions_list[i]
            image_id, image_desc = tokens.split()[0], tokens.split()[1:]
            image_id = image_id.split('.')[0]
            image_desc = " ".join(image_desc)
            number_images.add(image_id)
            if count == len(number_images):
                desc.append(str(image_desc))
            else:
                count += 1
                desc = []
                desc.append(str(image_desc))
            print(desc)
            if image_id not in descriptions:
                descriptions[image_id] = list()
            descriptions[image_id]=desc
        return descriptions

    def clean_descriptions(self):
        self.descriptions=self.load_descriptions()
        table=str.maketrans('','',string.punctuation)
        for key,desc_list in self.descriptions.items():
            for i in range(len(desc_list)):
                desc=desc_list[i]
                desc= desc.split()
                desc=[word.lower() for word in desc]
                desc=[w.translate(table) for w in desc]
                desc=[word for word in desc if len(word)>0]
                desc=[word for word in desc if word.isalpha()]
                desc_list[i]=' '.join(desc)

    def to_vocabulary(self):
        all_desc=set()
        for key in self.descriptions.keys():
            [all_desc.update(d.split()) for d in self.descriptions[key]]
        return all_desc

    def save_description(self):
        lines=list()
        for key,desc_list in self.descriptions.items():
            for desc in desc_list:
                print(desc)
                lines.append(key +" "+desc)
        data='\n'.join(lines)
        file=open(self.path_to_save_desc,'w')
        file.write(data)
        file.close()


class prepare_for_train_test():

    def __init__(self,captions_path,pickle_file_path):
        self.cleaned_captions_path=captions_path
        self.descriptions = dict()
        self.pickle_file_path=pickle_file_path
        self.all_descriptions=list()
        self.dataset=set()

    def identifiers(self):
        with open(self.cleaned_captions_path) as f:
            train_data_captions=f.read()
            for i in train_data_captions.split('\n'):
                identifier=i.split()[0]
                self.dataset.add(identifier)
            return self.dataset

    # load clean descriptions
    def load_descriptions(self):
        with open(self.cleaned_captions_path) as file:
            captions_file=file.read()
        captions_list = captions_file.split('\n')
        desc=[]
        count=1
        number_images=set()
        for i in range(0, len(captions_list), 1):
            tokens = captions_list[i]
            image_id, image_desc = tokens.split()[0], tokens.split()[1:]
            image_id = image_id.split('.')[0]
            image_desc = 'startseq '+ " ".join(image_desc)+' endseq'
            number_images.add(image_id)
            if count == len(number_images):
                desc.append(str(image_desc))
            else:
                count += 1
                desc = []
                desc.append(str(image_desc))
            if image_id not in self.descriptions:
                self.descriptions[image_id] = list()
            self.descriptions[image_id]= desc
        return self.descriptions

    #load photo features from saves pickle file
    def load_image_Features(self):
        features =load(open(self.pickle_file_path,'rb'))
        train_features={i:features[i] for i in self.dataset}
        return train_features

    #store all descriptions
    def store_descriptions(self):
        for i in self.descriptions.keys():
            [self.all_descriptions.append(j) for j in self.descriptions[i]]
        return self.all_descriptions

    def tokenzing_values(self):
        tokenize=Tokenizer()
        tokenize.fit_on_texts(self.all_descriptions)
        return tokenize

    def max_length_of_tokenzier(self):
        return max(len(d.split()) for d in self.all_descriptions)

def model_seq(tokenizer,max_length,descriptions,train_features,vocab_size):
    img_features_array,input_tok_seq,output_tok_seq=list(),list(),list()
    for key,desc_list in descriptions.items():
        for desc in desc_list:
            seq=tokenizer.texts_to_sequences([desc])[0]
            for i in range(1,len(seq)):
                in_seq,out_seq=seq[:i],seq[i]
                in_seq=pad_sequences([in_seq],maxlen=max_length)[0]
                out_seq=to_categorical([out_seq],num_classes=vocab_size)[0]
                img_features_array.append(train_features[key][0])
                input_tok_seq.append(in_seq)
                output_tok_seq.append(out_seq)
    return array(img_features_array),array(input_tok_seq),array(output_tok_seq)

def predict(imagearray):
    check=open(r'checkpoin file to model')
    check.run(r'path to inference graph')
    generated_text=check.test(imagearray)
    return generated_text


def LSTM_MODEL(vocab_size, max_length):
    # feature extractor (encoder)
    inputs1 = Input(shape=(4096,),name='image_layer')
    #fe1 = GlobalMaxPooling2D()(inputs1)
    fe2 = Dense(128, activation='relu')(inputs1)
    fe3 = RepeatVector(max_length)(fe2)
    # embedding
    inputs2 = Input(shape=(max_length,))
    emb2 = Embedding(vocab_size, 50, mask_zero=True)(inputs2)
    emb3 = LSTM(256, return_sequences=True)(emb2)
    emb4 = TimeDistributed(Dense(128, activation='relu'))(emb3)
    # merge inputs
    merged = concatenate([fe3, emb4])
    # language model (decoder)
    lm2 = LSTM(500)(merged)
    lm3 = Dense(500, activation='relu')(lm2)
    lm4=Flatten()(lm3)
    outputs = Dense(vocab_size, activation='softmax')(lm4)
    # tie it together [image, seq] [word]
    model = Model(inputs=[inputs1, inputs2], outputs=outputs)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    #plot_model(model, show_shapes=True, to_file='plot.png')
    return model


# training_ data set
prepare_for_train=prepare_for_train_test(r'path_to\train_caption_token.txt',
                                              r'path_to\image_features.pkl')
train_identifers=prepare_for_train.identifiers()
train_desc=prepare_for_train.load_descriptions()
train_image_features=prepare_for_train.load_image_Features()
prepare_for_train.store_descriptions()
train_tokenize=prepare_for_train.tokenzing_values()
train_vocab_size=len(train_tokenize.word_index)+1
train_max_length_cap=prepare_for_train.max_length_of_tokenzier()
X1train,X2train,ytrain=model_seq(train_tokenize,train_max_length_cap,train_desc,train_image_features,train_vocab_size)

# test data set
prepare_for_test=prepare_for_train_test(r'path_to\test_caption_token.txt',
                                              r'path_to\image_features.pkl')
test_identifers=prepare_for_test.identifiers()
test_desc=prepare_for_test.load_descriptions()
test_image_features=prepare_for_test.load_image_Features()
prepare_for_test.store_descriptions()
test_tokenize=prepare_for_test.tokenzing_values()
test_vocab_size=len(test_tokenize.word_index)+1
test_max_length_cap=prepare_for_test.max_length_of_tokenzier()
X1test,X2test,ytest=model_seq(test_tokenize,test_max_length_cap,test_desc,test_image_features,test_vocab_size)

#fit model
model=LSTM_MODEL(train_vocab_size,train_max_length_cap)
#store checkpoint
file=r'path_to\model-ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5'
checkpoint = ModelCheckpoint(file, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
#fit model
model.fit([X1train, X2train], ytrain, epochs=20, verbose=2, callbacks=[checkpoint], validation_data=([X1test, X2test], ytest))
