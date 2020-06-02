import sys
from model import google_vision_api_call
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error
import speech_recognition as sr
from io import BytesIO
import time
from PIL import Image
import pygame
from gtts import gTTS
from obj_detection import object_dectection
from datetime import date
from model import model

def listen_to_blind():
    mic=sr.Microphone()
    r=sr.Recognizer()
    with mic as source:
        time.sleep(1)
        send_the_message('speak now')
        r.adjust_for_ambient_noise(source)
        audio=r.listen(source)
    try:
        voice_text=r.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Google Speech Recognition couldn't recognize")
        retyed_voice=retry_listening()
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        sys.exit()

def retry_listening():
    mic=sr.Microphone()
    k=sr.Recognizer()
    with mic as source:
        time.sleep(1)
        send_the_message('can you speak again')
        k.adjust_for_ambient_noise(source)
        audio=k.listen(source)
    try:
        voice_text=k.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        print("Sorry, Google speech Recognition could not understand audio")
        send_the_message("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None

def ask_the_request(request):
    with BytesIO() as f:
        gTTS(request, lang='en-UK').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    voice_text=listen_to_blind()
    if voice_text is not None:
        return voice_text
    else:
        sys.exit()

def send_the_message(request):
    with BytesIO() as f:
        gTTS(request, lang='en').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

def byte_array_to_image(byte_image):
    file = BytesIO()
    file.write(byte_image)
    file.seek(0)
    img = Image.open(file)
    return img

def preprocess(text,check):
    text=text.lower()
    if str(check) in str(text):
        return True

def extract_chapter_id(text):
    chapter_id=None
    text=text.lower()
    if bool(text.strip())==False:
        chapter_id=None
    elif "chapter" in text:
        text_list=text.lower().split('chapter')
        for i in range(1,len(text_list)):
            for j in range(0,len(text_list[i].split())):
                try:
                    chapter_id=int(text_list[i].split()[j].strip())
                except ValueError:
                    pass
    elif len(text)<3 and bool(text.strip())!=False:
        chapter_id=text.strip()
    return chapter_id

def generate_objects(obj_lis):
    objects=''
    obj_dict=obj_lis[0]
    for keys,val in obj_dict.items():
        key=str(keys.decode('utf-8'))
        objects=objects+' '+key
    return objects

def get_user_id(first_name,last_name, phone_number):
    try:
        connector = MySQLConnection(user='username', password='enter_password',
                                    host='127.0.0.1',
                                    database="project")
        cursor = connector.cursor()
    except Error as e:
        print("connection error {}".format(e))
        sys.exit("unable to connect to db")
    try:
        # check the values in the database
        insert_values = (first_name,last_name,phone_number)
        insert_command = "SELECT User_id FROM user_info WHERE(user_first_name=%s and user_last_name=%s and user_phone_number=%s)"
        cursor.execute(insert_command, insert_values)
        connector.commit()
        user_id = cursor.fetchone()[0]
        return user_id
    except:
        print("cannot find user ID sorry cannot enter the  Comments")
        return None


#start of the application main class

class start_application():
    def __init__(self):
        self.welcome=send_the_message('Welcome to Comics for blind')
        self.reponse=ask_the_request("Would to like to listen to Comics If so say Yes or say no")
        user_intial_reponse=preprocess(self.reponse,'no')
        if bool(user_intial_reponse)==True:
            send_the_message('Closing the application')
            sys.exit()
        else:
            self.first_name=ask_the_request('Please tell your first name')
            self.last_name=ask_the_request("Please tell your Last Name")
            self.name = self.first_name + " " + self.last_name
            self.phone_number =ask_the_request("Please tell your phone number")
            self.chapter=ask_the_request("Please tell the chapter ID you want to listen")
            self.chapter_id=extract_chapter_id(self.chapter)
            print("This is chapter number "+self.chapter_id)
            if self.chapter_id is None:
                  send_the_message("We have not received a valid chapter Id")
                  self.chapter=ask_the_request("Request you to repeat the chapter")
                  self.chapter_id=extract_chapter_id(self.chapter)
            self.comment=False

    def store_user_information_db(self):
        try:
            connector = MySQLConnection(user='username', password='enter_password',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))
            sys.exit("unable to connect to db")
        try:
            insert_values = (self.first_name, self.last_name,self.phone_number)
            insert_command = "INSERT INTO user_info(user_first_name, user_last_name, user_phone_number) VALUES(%s,%s,%s)"
            cursor.execute(insert_command, insert_values)
            connector.commit()
        except:
            print("cannot insert user information into DB")

# ask the user A which date he want to know about the comic

class ask_data_to_user(start_application):
    def __init__(self,classA):
        self.chapter_id=classA.chapter_id
        self.first_name=classA.first_name
        self.last_name=classA.last_name
        self.phone_number=classA.phone_number

    def process_to_model(self):
        connector = MySQLConnection(user='username', password='enter_password',
                                    host='127.0.0.1',
                                    database="project")
        self.cx = connector.cursor()
        # need to change to the date format need to verify this
        query_fetch_raw_image_id="SELECT img_id FROM raw_table WHERE img_id=%s"
        chapter=(self.chapter_id,)
        self.cx.execute(query_fetch_raw_image_id,chapter)
        img_id=self.cx.fetchone()[0]
        for i in range(1,4):
            query_fetch_split_images="SELECT image FROM split_images WHERE img_id={} and img_no={}".format(img_id,i)
            self.cx.execute(query_fetch_split_images)
            image=self.cx.fetchone()[0]
            #  send image to api

            bubble_text = api_call.api_call(image)
            txt_bubble = bubble_text.detect_text()

            if txt_bubble is None:
                gen_text= model.predict(image)
                send_the_message("we are in page {} of chapter {} ".format(i, self.chapter_id))
                send_the_message("Conversation in image is as follows: ")
                send_the_message(gen_text)
            else:
                obj_detection = object_dectection(image)
                image_objects = obj_detection.run_model()
                obj = generate_objects(image_objects)
                txt_from_bubble=txt_bubble
                if 'bubble' in obj:
                    objects = obj.replace("bubble", '')
                else:
                    objects=obj
                print("we are in page {} of chapter {} and we have ".format(i, self.chapter_id) + str(
                    objects) + " in the current scene ")
                print("Conversation in image is as follows: ")
                # text-voice output to user
                send_the_message("we are in page {} of chapter {} and we have ".format(i,self.chapter_id)+ str(objects) + " in the current scene ")
                send_the_message("Conversation in image is as follows: ")
                time.sleep(1)
                send_the_message(str(txt_from_bubble))

        #ask the user to review on comic on the particular chapter
        self.comment_on_comic = ask_the_request("Would you like to comment on this chapters if yes say yes else no")
        if bool('y' in self.comment_on_comic.lower())==True:
            user_id = get_user_id(self.first_name,self.last_name ,self.phone_number)
            comment = ask_the_request("Please mention your comment now")
            self.store_the_comment(user_id, self.chapter_id, comment)

        # listem to comment
        self.listen_to_user_comments = ask_the_request(
            "Would you like to listen to User comments on same chapter or different is same say yes else no if you want to exit say bye")
        listen_comments_reponse = preprocess(self.listen_to_user_comments, 'y')
        if bool(listen_comments_reponse) == True:
            comments=self.fetch_comments(self.chapter_id)
            if comments is not None:
                for comment in comments:
                    send_the_message(comment[0])
            else:
                send_the_message("we don't Found any comments for the chapter id")
        if bool('b' in self.listen_to_user_comments.lower())==True:
            send_the_message("Thanks for using comic world I hope you like it")
            sys.exit()
        if bool('n' in self.listen_to_user_comments.lower())== True:
            chapter_number = ask_the_request("Mention the Chapter Number")
            chapter =extract_chapter_id(chapter_number)
            comments=self.fetch_comments(chapter)
            if comments is not None:
                for comment in comments:
                    send_the_message(comment[0])
            else:
                send_the_message("we don't Found any comments for the chapter id")
        else:
            send_the_message("we didn't received any voice from you")

        request_for_continution = ask_the_request("would you like to continue the series if so say yes else no")
        continution_response = preprocess(request_for_continution, "y")
        if bool(continution_response) == True:
            self.chapter_id = int(self.chapter_id) + 1
            self.process_to_model()
        else:
            send_the_message("Thanks for using Garfield Comics hope you liked our experience")
            sys.exit()

    def store_the_comment(self, user_id, chapter_id, comment):
        self.user_id = user_id
        self.chapter_id = chapter_id
        self.comment = comment
        self.comment_date = str(date.today())
        try:
            connector = MySQLConnection(user='username', password='enter_password',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))
            sys.exit()
        try:
            insert_values = (self.user_id, self.chapter_id, self.comment, self.comment_date)
            insert_command = "INSERT INTO chapter_comments(user_id,chapter_id,user_comment,comment_date) VALUES(%s,%s,%s,%s)"
            result = cursor.execute(insert_command, insert_values)
            connector.commit()
        except:
            print("cannot insert user information into DB")

    def fetch_comments(self, chapter_id):
        self.chapter_id = chapter_id
        try:
            connector = MySQLConnection(user='username', password='enter_password',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor(buffered=True)
        except Error as e:
            print("connection error {}".format(e))
            sys.exit()
        try:
            insert_command = "SELECT comments FROM chapter_comments WHERE chapter_id={}".format(chapter_id)
            cursor.execute(insert_command)
            comments = cursor.fetchall()
            connector.commit()
            return comments
        except:
            print("cannot insert user information into DB")
            return None
