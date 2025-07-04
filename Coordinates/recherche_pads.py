### Imports

import wire.py

import numpy as np
import pandas as pd
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import imutils
import scipy.stats as stats
import statistics
import os
from collections import deque



### Fonctions utiles ###

def norme(pix):         
    
    # comprise entre 0 et racine de 3
    
    return np.sqrt((pix[0]/255)**2+(pix[1]/255)**2+(pix[2]/255)**2)


def tourner_image(image, pente):        
    
    # recadrer l'image à partir des pentes des bords
    
    return imutils.rotate(image, np.arctan(pente))


def trouver_la_paire(fichier, dossier):         
    
    # Trouver le module non câblé à partir du câblé et inversement
    
    bname=os.path.basename(fichier)
    if "After" in bname:
        name=bname[:bname.find("After")]
        for f in os.listdir(dossier):
            if "Reception" in os.path.basename(f):
                if os.path.basename(f)[:os.path.basename(f).find("Reception")]==name:
                    return f
    elif "Reception" in bname:
        name=bname[:bname.find("Reception")]
        for f in os.listdir(dossier):
            if "After" in os.path.basename(f):
                if os.path.basename(f)[:os.path.basename(f).find("After")]==name:
                    return f
    return "Pas de paire"


### Trouver les pads sur la puce ###

# Les trouver
def trouver_pads_chip(image):
    # Entrée : image cropée contenant uniquement la zone des pads (obtenable grâce au repère absolu de Gabriel)
    # Sortie : nombre de pads et zones de chaque pads 


    pads=0
    zones=[]
    i=0
    cop=image.copy()
    col=[np.mean([norme(pix) for pix in ligne]) for ligne in cop]
    checkpoint=0
    while i<image.shape[0]:
        if col[i]<0.8 and np.abs(checkpoint-i)>8:      # On a trouvé une délimitation entre deux pads, qu'on ne confondra pas avec un pad non occupé un peu trop sombre
            
            zone=[image[checkpoint:i,:,:], [checkpoint, 0]]        # zone et coin sup
            pads+=1
            zones.append(zone)

            bool=True

            while ((bool) and (i<image.shape[0]-1)):
                if col[i+1]>0.55:
                    bool=False
                    i+=1
                    checkpoint=i
                else:
                    i+=1
        else:
            i+=1

    return pads, zones




# Trouver si chaque pads est cablé ou non
def pads_cables(image,liste_points):      
    # Entrée : image cropée contenant uniquement la zone des pads ; liste des points extremaux à gauche de chaque fil (obtenable grâce aux fonctions de wire.py)
    # Sortie : liste de 0 et de 1 si pads non cablés ou cablés

    nb_pads,zones=trouver_pads_chip(image)
    num_pads_cables=[]
    i,k=0,0
    while i<nb_pads and k<=len(liste_points):
        if liste_points[k] in zones[i]:
            num_pads_cables.append(1)
            k+=1
            i+=1
        else:
            num_pads_cables.append(0)
            i+=1
    if i!=nb_pads or k!=len(liste_points):
        return "Error"
    else:
        return num_pads_cables