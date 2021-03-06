import cv2
import numpy as np
from PIL import Image
from keras import models
import tensorflow as tf
import time
import os
import geocoder
#Mysql Connection.
import mysql.connector
db = mysql.connector.connect(host="localhost",user="root",passwd="0000", database="smk")
cursor = db.cursor()

m=-10
s=-10
img_array=[]
#Load the saved model
model = tf.keras.models.load_model('model .h5')
#video = cv2.VideoCapture('1.mp4')
video = cv2.VideoCapture(input("Enter Video name"))
if (video.isOpened()== False): 
        print("Error opening video file")
image_path = '/var/www/html/Illegal/images'
while (video.isOpened()):
        ret, frame = video.read()
        #height, width, layers = frame.shape
        #size = (width,height)
        if (ret == True):
        #Convert the captured frame into RGB
                im = Image.fromarray(frame, 'RGB')

        #Resizing into 128x128 because we trained the model with this image size.
        #299
                im = im.resize((299,299))
                img_array = np.array(im)
                img_array = np.divide(img_array, 255.0) 
                img_array = np.subtract(img_array, 1.0) 
                img_array = np.multiply(img_array, 2.0)
        #Our keras model used a 4D tensor, (images x height x width x channel)
        #So changing dimension 128x128x3 into 1x128x128x3 
                img_array = np.expand_dims(img_array, axis=0)
        #Calling the predict method on model to predict 'me' on the image
                prediction = model.predict(img_array)[0][0]
        #if prediction is 0, which means Non smoking.
        #if prediction is 1, which means smoking.
                font = cv2.FONT_HERSHEY_SIMPLEX
                per = (prediction/2)*100
                frame = cv2.putText(frame, str(time.strftime('%Y-%m-%d %H-%M-%S')), (5, 100 ), font, 1, (255, 255, 255), 2)
                if int(prediction) == 0:
                        frame = cv2.putText(frame, "Not Smoking", (5, 150 ), font, 1, (0, 255, 0), 2)
                elif int(prediction) == 1:
                        frame = cv2.putText(frame, "Smoking "+str(int(per))+"%", (5, 150 ), font, 1, (0, 0, 255), 3)
                        t=str(time.strftime('%Y-%m-%d %H-%M-%S'))
                        n_m=int(t[14:16])
                        n_s=int(t[17:19])
                        if(abs(m-n_m)>0 or abs(s-n_s)>10):
                                g = geocoder.ip("me")
                                l=str(g.latlng[0])+","+str(g.latlng[1])
                                m=n_m
                                s=n_s
                                f_name='smoking'+str(time.strftime('%Y-%m-%d%H-%M-%S'))+'.jpg'
                                sql = "INSERT INTO Smk_Record (name, loc, percentage) VALUES (%s, %s, %s)"
                                val = (f_name, l, str(per))
                                cursor.execute(sql, val)
                                db.commit()
                                cv2.imwrite(os.path.join(image_path,f_name),frame)
                frame = cv2.resize(frame,(960,540))
                cv2.imshow("Capturing", frame)
                #img_array.append(frame)
                key=cv2.waitKey(1)
                if key == ord('q'):
                        break
        else:
                break
#out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
#for i in range(len(img_array)):
 #   out.write(img_array[i])
#out.release()
video.release()
cv2.destroyAllWindows()
