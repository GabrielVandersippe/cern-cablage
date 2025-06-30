# C'est mon fichier le premier qui le modifie je le balaye

import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

img = plt.imread("img_test.jpg")

plt.imshow(img)
#plt.show()
top_line = img[500,:,:]
bottom_line = img[5000,:,:]

def avg_light_color(line,side):
    sum = 0
    n = len(line) - 1
    if side == "left":
        for i in range(100):
            sum += line[i,0]
            sum += line[i,1]
            sum += line[i,2]
    elif side == "right":
        for i in range(100):
            sum += line[n-i,0] + line[n-i,1] + line[n-i,2]
    return sum / 100

def detect_borders(line):
    print(avg_light_color(line,"left"))
    print(avg_light_color(line,"right"))

detect_borders(top_line)
detect_borders(bottom_line)
