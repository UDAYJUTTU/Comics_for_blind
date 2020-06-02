from PIL import Image

class split_strip():
    def __init__(self,image):
        self.image=Image.open(image)
        self.width,self.height=self.image.size
        self.start_width=0
        self.split_length=self.width/3
        self.intial_split_length=self.split_length

    def split(self):
        cropped_image={}
        for i in range(1,4):
            crop_box=(self.start_width,0,self.split_length,self.height)
            cropped_image[i]=crop_box
            self.start_width = self.split_length
            self.split_length=self.split_length+self.intial_split_length
        return cropped_image

