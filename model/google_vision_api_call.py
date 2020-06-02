import os
from google.cloud import vision
import re

def preprocess_bubble_text(bubble_text):
    s = re.sub('._.', '', bubble_text)
    s = s.replace("JIM", '')
    s = s.replace('DAVIS','')
    s = s.replace('All rights reserved', '')
    s = s.replace("(numbers)", '')
    s = s.replace("1979", '')
    s = s.replace('INC,', '')
    bubble_text_cleaned = s.replace('O0o', '')
    return bubble_text_cleaned

class api_call():

    def __init__(self,image_bytearray):
        credential_path = r"pathto \vision_api_cred.json"
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
        self.image_bytes=bytes(image_bytearray)

    def detect_text(self):
        """Detects text in the file."""
        client = vision.ImageAnnotatorClient()
        # with open(self.path, 'rb') as image_file:
        #     content = image_file.read()
        content=self.image_bytes
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        bubble_text= texts[0].description
        bubble_text=str(bubble_text).strip()
        cleaned_bubble_text = preprocess_bubble_text(bubble_text)
        if len(cleaned_bubble_text)<5:
            bubble_text=None
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        return bubble_text


