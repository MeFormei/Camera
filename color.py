import cv2
import numpy as np

def get_color(red,green,blue):
    color = np.uint8([[[red,green,blue]]])
    return str(cv2.cvtColor(color,cv2.COLOR_BGR2HSV))