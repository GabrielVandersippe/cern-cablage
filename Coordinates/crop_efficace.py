### Imports

import wire.py

import numpy as np
import pandas as pd
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import imutils
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







### Trouver les bords verts ###

# Trouver la colonne verte à gauche : return le numéro de la colonne et la colonne
def find_colonne_v2_gauche(image):
    colonnes=[image[:,i,:] for i in range(image.shape[1])]
    i=0
    bool=False
    while not bool and i<len(colonnes)-1:
        col=colonnes[i]
        cpt=0
        for pix in col:
            if (40<pix[0]<100) and (40<pix[1]<100) and  (pix[2]<20):
                cpt+=1       
        if cpt>0.1*image.shape[1]:
            bool=True
        if not bool:
            i+=1
    return i, colonnes[i]


# Trouver la colonne verte à droite : return le numéro de la colonne et la colonne
def find_colonne_v2_droite(image):
    colonnes=[image[:,i,:] for i in range(image.shape[1])]
    i=0
    bool=False
    while not bool and i<len(colonnes)-1:
        col=colonnes[image.shape[1]-i-1]
        cpt=0
        for pix in col:
            if (30<pix[0]<100) and (30<pix[1]<100) and  (pix[2]<20):
                cpt+=1       
        if cpt>0.1*image.shape[1]:
            bool=True
        if not bool:
            i+=1
    return image.shape[1]-i-1, col


# Trouver la ligne verte haute : return le numéro de la colonne et la colonne
def find_ligne_v2_haute(image):
    lignes=[image[i,:,:] for i in range(image.shape[0])]
    i=0
    bool=False
    while not bool and i<len(lignes)-1:
        lin=lignes[i]
        cpt=0
        for pix in lin:
            if (30<pix[0]<100) and (30<pix[1]<100) and  (pix[2]<20):
                cpt+=1       
        if cpt>0.1*image.shape[0]:
            bool=True
        if not bool:
            i+=1
    return i, lin


# Trouver la ligne verte basse : return le numéro de la colonne et la colonne
def find_ligne_v2_basse(image):
    lignes=[image[i,:,:] for i in range(image.shape[0])]
    i=0
    bool=False
    while not bool and i<len(lignes)-1:
        lin=lignes[image.shape[0]-i-1]
        cpt=0
        for pix in lin:
            if (30<pix[0]<100) and (30<pix[1]<100) and  (pix[2]<20):
                cpt+=1       
        if cpt>0.1*image.shape[0]:
            bool=True
        if not bool:
            i+=1
    return image.shape[0]-i-1, lin


# Test : affiche l'image et tous ses bords détectés
def verif_bords(image):
    bord_gauche=find_colonne_v2_gauche(image)[0]
    bord_droit=find_colonne_v2_droite(image)[0]
    bord_haut=find_ligne_v2_haute(image)[0]
    bord_bas=find_ligne_v2_basse(image)[0]

    plt.imshow(image)
    plt.scatter(bord_gauche, 0, color='tab:red', marker='+', s=300)
    plt.scatter(bord_droit, 0, color='tab:red', marker='+', s=300)
    plt.scatter(0, bord_haut, color='tab:red', marker='+', s=300)
    plt.scatter(0, bord_bas, color='tab:red', marker='+', s=300)
    plt.title(f'Bords')
    plt.show()





### Croper sur les bords des pads ###

def croper_details_sans_rotation(image):
    # Affiche le détail des calculs pour croper l'image, montre les images correspondantes mais ne return rien

    # On préréduit l'image pour trouver les fils plus simplement
    bord_gauche=find_colonne_v2_gauche(image)[0]
    bord_droit=find_colonne_v2_droite(image)[0]
    bord_haut=find_ligne_v2_haute(image)[0]
    bord_bas=find_ligne_v2_basse(image)[0]

    plt.imshow(image)
    plt.scatter(bord_gauche, 0, color='tab:red', marker='+', s=300)
    plt.scatter(bord_droit, 0, color='tab:red', marker='+', s=300)
    plt.scatter(0, bord_haut, color='tab:red', marker='+', s=300)
    plt.scatter(0, bord_bas, color='tab:red', marker='+', s=300)
    plt.title(f'Bords')
    plt.show()
    
    bounds_h=1000
    bounds_b=5000



    ## Calculs à gauche

    print("---")
    print('Calculs à gauche...')
    print("---")

    bounds_g=bord_gauche-300
    bounds_d=bord_gauche-50
    test_compressed = image[bounds_h:bounds_b:2,bounds_g:bounds_d:2,:]

    # On découpe en plusieurs bouts
    nb_bouts=10
    delta=int(test_compressed.shape[0]/(nb_bouts*5))
    liste_images=[test_compressed[i*delta:(i+1)*delta, :,:] for i in range(0,nb_bouts*50, 5)]

    # On fait le truc sur chaque bout             
    liste_de_mins_g=[]
    for ind, e in enumerate(liste_images):
        list = []
        for i in range(len(e)):
            if isWhite(e,(i,e.shape[1]-10)):
                list += bfsWire(e,(i,e.shape[1]-10))

        test_copy = e.copy()

        for coord in list:
            test_copy[coord[0],coord[1],:] = np.array([255,0,0])
        
        # recherche du minimum
        if len(list)!=0:
            min=list[0]
            for pt in list:
                if pt[1]<min[1]:
                    min=pt
            liste_de_mins_g.append(min[1])
    
    print(f'Nombre de bouts de fils utilisés à gauche : {len(liste_de_mins_g)}')
    
    min_ou_croper_g=2*np.min(liste_de_mins_g)+bounds_g

    print("---")
    print(f'La colonne à croper à gauche est la colonne {min_ou_croper_g}')




    ## Calculs à droite

    print('---')
    print('Calculs à droite...')
    print('---')

    bounds_d=bord_droit+300
    bounds_g=bord_droit+50
    test_compressed = image[bounds_h:bounds_b:2,bounds_g:bounds_d:2,:]

    # On découpe en plusieurs bouts
    nb_bouts=10
    delta=int(test_compressed.shape[0]/(nb_bouts*5))
    liste_images=[test_compressed[i*delta:(i+1)*delta, :,:] for i in range(0,nb_bouts*50, 5)]

    # On fait le truc sur chaque bout             
    liste_de_maxs_d=[]
    for ind, e in enumerate(liste_images):
        list = []
        for i in range(len(e)):
            if isWhite(e,(i,10)):
                list += bfsWire(e,(i,10))

        test_copy = e.copy()

        for coord in list:
            test_copy[coord[0],coord[1],:] = np.array([255,0,0])
        
        # recherche du maximum
        if len(list)!=0:
            max=list[0]
            for pt in list:
                if pt[1]>min[1]:
                    min=pt
            liste_de_maxs_d.append(min[1])
    
    print(f'Nombre de bouts de fils utilisés à droite : {len(liste_de_maxs_d)}')
    
    max_ou_croper_d=2*np.max(liste_de_maxs_d)+bounds_g

    print("---")
    print(f'La colonne à croper à droite est la colonne {max_ou_croper_d}')


    ## Plot pour vérifier
    image_cropee=image[bord_haut:bord_bas, min_ou_croper_g:max_ou_croper_d,:]
    plt.imshow(image_cropee)
    plt.title("Cropée")
    plt.show()






def croper(image):
    # On return juste l'image cropée

    # On préréduit l'image pour trouver les fils plus simplement
    bord_gauche=find_colonne_v2_gauche(image)[0]
    bord_droit=find_colonne_v2_droite(image)[0]
    bord_haut=find_ligne_v2_haute(image)[0]
    bord_bas=find_ligne_v2_basse(image)[0]
    
    bounds_h=1000
    bounds_b=5000



    ## Calculs à gauche

    bounds_g=bord_gauche-300
    bounds_d=bord_gauche-50
    test_compressed = image[bounds_h:bounds_b:2,bounds_g:bounds_d:2,:]

    # On découpe en plusieurs bouts
    nb_bouts=10
    delta=int(test_compressed.shape[0]/(nb_bouts*5))
    liste_images=[test_compressed[i*delta:(i+1)*delta, :,:] for i in range(0,nb_bouts*50, 5)]

    # On fait le truc sur chaque bout             
    liste_de_mins_g=[]
    for ind, e in enumerate(liste_images):
        list = []
        for i in range(len(e)):
            if isWhite(e,(i,e.shape[1]-10)):
                list += bfsWire(e,(i,e.shape[1]-10))

        test_copy = e.copy()

        for coord in list:
            test_copy[coord[0],coord[1],:] = np.array([255,0,0])
        
        # recherche du minimum
        if len(list)!=0:
            min=list[0]
            for pt in list:
                if pt[1]<min[1]:
                    min=pt
            liste_de_mins_g.append(min[1])
    
    min_ou_croper_g=2*np.min(liste_de_mins_g)+bounds_g



    ## Calculs à droite

    bounds_d=bord_droit+300
    bounds_g=bord_droit+50
    test_compressed = image[bounds_h:bounds_b:2,bounds_g:bounds_d:2,:]

    # On découpe en plusieurs bouts
    nb_bouts=10
    delta=int(test_compressed.shape[0]/(nb_bouts*5))
    liste_images=[test_compressed[i*delta:(i+1)*delta, :,:] for i in range(0,nb_bouts*50, 5)]

    # On fait le truc sur chaque bout             
    liste_de_maxs_d=[]
    for ind, e in enumerate(liste_images):
        list = []
        for i in range(len(e)):
            if isWhite(e,(i,10)):
                list += bfsWire(e,(i,10))

        test_copy = e.copy()

        for coord in list:
            test_copy[coord[0],coord[1],:] = np.array([255,0,0])
        
        # recherche du maximum
        if len(list)!=0:
            max=list[0]
            for pt in list:
                if pt[1]>min[1]:
                    min=pt
            liste_de_maxs_d.append(min[1])
    

    max_ou_croper_d=2*np.max(liste_de_maxs_d)+bounds_g

 
    return image[bord_haut:bord_bas, min_ou_croper_g:max_ou_croper_d,:]