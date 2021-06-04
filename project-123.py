import cv2
import numpy as np
import pandas as pd
from pandas.core.indexes import multi
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from PIL import Image
import PIL.ImageOps 
import os , ssl,time

#fetching the data + 
X = np.load('image.npz')['arr_0']
y = pd.read_csv("labels.csv")["labels"]

print(pd.Series(y).value_counts())

classes = ['A','B','C','D','E','F','G','H','I','J','K','L','N','M','O','P','Q','R','S','T','U','V','W','X','Y','Z']
nclasses = len(classes)

X_train,X_test,y_train,y_test = train_test_split(X,y,random_state = 9,train_size = 7500,test_size = 2500)
#scaling the features
 
X_train_scaled = X_train/255.0
X_test_scaled = X_test/255.0


#fitting the training data into the model
cls = LogisticRegression(solver = 'saga',multi_class = 'multinomial').fit(X_train_scaled,y_train)

#calculating the accuracy of the model

y_pred = cls.predict(X_test_scaled)
accuracy = accuracy_score(y_test,y_pred)
print("Accuracy ->",accuracy)

#starting the camera

cap = cv2.VideoCapture(0)


while(True):
    try:
        ret,frame = cap.read()
        #our operations on the frame
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        #join the box in the centre of the video
        height,width = gray.shape
        upper_left = (int(width/2 - 56),int(height/2 - 56))
        bottom_right = (int(width/2 + 56),int(height/2 + 56))
        cv2.rectangle(gray,upper_left,bottom_right,(0,255,0),2)
        #To only consider the area inside the box for detecting the digit
        #ROI = Region Of Interest
        roi = gray[upper_left[1]:bottom_right[1],upper_left[0]:bottom_right[0]]
        #converting cv2 image to pil image
        im_pil = Image.fromarray(roi)
        #convert to gray-scale image
        #L format for each pixel
        image_bw = im_pil.convert('L')
        image_bw_resize = image_bw_resize((28,28),Image.ANTIALIAS) 
        #invert the image
        image_bw_resize_inverted = PIL.ImageOps.invert(image_bw_resize)
        pixel_filter = 20
        #convert to scalar quantity
        min_pixel = np.percentile(image_bw_resize_inverted,pixel_filter)
        image_bw_resize_inverted_scale = np.clip(image_bw_resize_inverted - min_pixel , 0 , 255)
        max_pixel = np.max(image_bw_resize_inverted)
        #convert into array
        image_bw_resize_inverted_scale = np.asarray(image_bw_resize_inverted_scale) / max_pixel
        test_sample = np.array(image_bw_resize_inverted_scale).reshape(1,784)
        test_pred = cls.predict(test_sample)
        print("Predicted class is", test_pred)
        #display the resulting frame
        cv2.imshow('frame', gray)
        if cv2.waitKey(1)|0xFF == ord('q'):
            break
    
    except Exception as e:
        pass

cap.release()
cv2.destroyAllWindows()