import numpy as np
import os
import cv2 as cv
import matplotlib.pyplot as plt

## Fonction utile pour normaliser un vecteur
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

## Fonction pour trouver l'image non câblée à l'image câblée (ou l'inverse)
def trouver_la_paire(fichier, dossier):
    bname=os.path.basename(fichier)
    if "AfterBonding" in bname:
        name=bname[:bname.find("AfterBonding")]
        for f in os.listdir(dossier):
            if "Reception" in os.path.basename(f):
                if os.path.basename(f)[:os.path.basename(f).find("Reception")]==name:
                    return f
    elif "Reception" in bname:
        name=bname[:bname.find("Reception")]
        for f in os.listdir(dossier):
            if "AfterBonding" in os.path.basename(f):
                if os.path.basename(f)[:os.path.basename(f).find("AfterBonding")]==name:
                    return f
    return "Pas de paire"

#fonction utile pour afficher une image
def afficher(img) :
    cv.imshow("Image", img)
    cv.waitKey(0)
    cv.destroyAllWindows()

## Fonction qui affiche une liste de points sur une image.
## Paramètre with_cv : si on affiche avec opencv ou avec matplotlib
def afficher_points(img, centres, with_cv = False):
    img_copy = img.copy()
    for centre in centres :
        cv.circle(img_copy, (centre[0],centre[1]),15,(255,0,0),15)

    if with_cv :
        cv.imshow("Image", img_copy)
        cv.waitKey(0)
        cv.destroyAllWindows()
    else:
        plt.imshow(img_copy)
        plt.show()