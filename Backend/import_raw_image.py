from mysql.connector import MySQLConnection
from io import BytesIO
from mysql.connector.errors import Error
from split_strip import split_strip
from PIL import Image


class Database_manupluations():
    def __init__(self):
        self.primary_id = 1
        self.year = 1979
        self.start_month = 1
        self.start_date = 1
        self.Months_list = [1, 3, 5, 7, 8, 10, 12]
        self.Months_list_2 = [2, 4, 6, 9, 11]

# Pipeline to import Images directory to raw_images table to MYSQL DB

    def import_to_raw_image_from_local(self):
        try:
            connector = MySQLConnection(user='username', password='enter_password',
                                        host='127.0.0.1',
                                        database="project")
            cursor = connector.cursor()
        except Error as e:
            print("connection error {}".format(e))

        # opening the images files and loading 100 images into the server
        for i in range(1, 365, 1):
            try:
                img = open(r'path_to\images\{}.jpg'.format(i), 'rb')
                formated_img = img.read()
            except:
                print("image is excepted")
                pass
            insert_image_tuple = (self.primary_id, formated_img, "{}/{}/{}".format(self.year, self.start_month, self.start_date))
            insert_command = """INSERT INTO raw_image(img_id,image,Image_date) VALUES (%s,%s,%s)"""
            result = cursor.execute(insert_command, insert_image_tuple)
            connector.commit()
            self.primary_id = self.primary_id + 1
            self.start_date = self.start_date + 1
            if self.start_date==32 and self.start_month in self.Months_list:
                if self.start_month != 12:
                    self.start_month = self.start_month + 1
                    self.start_date = 1
                else:
                    self.year =self.year+1
                    self.start_month = 1
                    self.start_date = 1
            if self.start_date==31 and self.start_month in self.Months_list_2:
                    self.start_month = self.start_month + 1
                    self.start_date = 1
            if self.start_date == 29 and self.start_month == 2:
                self.start_month = self.start_month + 1

# Splitting the images

    def raw_image_to_split_image(self):
        try:
            connector = MySQLConnection(user='username', password='enter_password',
                                        host='127.0.0.1',
                                        database="project")
            self.cx = connector.cursor()
            for i in range(1, 365, 1):
                query="SELECT image FROM raw_image WHERE img_id= {}".format(i)
                self.cx.execute(query)
                img_field = self.cx.fetchone()[0]
                file=BytesIO()
                file.write(img_field)
                file.seek(0)
                img=Image.open(file)
                split_strip_image=split_strip(file)
                cropped_box=split_strip_image.split()
                for key,value in cropped_box.items():
                    print(str(key) +"and this value"+ str(value))
                    cropped_image=img.crop(value)
                    cropped_image.save(r'path_to\split_images_1\{}_{}.png'.format(i,key))

        except Error as e:
            print('connection error {}' .format(e))


# Pipeline for Split Images to MYSQL

    def store_split_images_to_db(self):
                try:
                    connector = MySQLConnection(user='username', password='enter_password',
                                                host='127.0.0.1',
                                                database="project")
                    cursor = connector.cursor()
                except Error as e:
                    print("connection error {}".format(e))
                for i in range(1, 365, 1):
                    for j in range(1, 4, 1):
                         try:
                            img = open(r'path_to\split_images_1\{}_{}.png'.format(i,j),'rb')
                            formated_img = img.read()
                            print(formated_img)
                            insert_values=(i,j,formated_img)
                            insert_command="INSERT INTO split_images(img_id,img_no,image) VALUES(%s,%s,%s)"
                            result = cursor.execute(insert_command,insert_values)
                            connector.commit()
                         except:
                             print("image is excepted")



