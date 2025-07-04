import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from Coordinates.utils import *
from Coordinates.data import *


## Fonction pour trouver les mires sur l'image non câblée

def mires(img_input:np.ndarray, draw = False):
    """Finds the positions of the 8 targets on the unwired PCB, or an error if it could not.

    Arguments :

    img_input - array of pixels : the working image (in BGR)

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray : array of centers
    """
    assert img_input is not None, "file could not be read, check with os.path.exists()" #Vérifier si l'image existe

    img = cv.cvtColor(img_input,cv.COLOR_BGR2GRAY) #Mettre en noir et blanc
    (height,length) = img.shape

    ## TODO : changer cette extraction à la main par quelque chose d'automatisé
    sliceparams = [(100, 400, 300, 600, 1),  
                   (-400, -100, 300, 600, 1),
                   (3800, 4200, 500, 800, 2), 
                   (100, 400, -600,-300, 1), 
                   (-400, -100, -600, -300, 1), 
                   (3800, 4200, -800, -500, 2)]

    cimg = cv.cvtColor(img,cv.COLOR_GRAY2BGR) #Avec 3 canaux pour pouvoir l'afficher bien

    centers = []

    for (beg1, end1, beg2, end2, nbmires) in sliceparams :
        mask = img[beg1:end1, beg2:end2]

        #Blur pour réduire le bruit
        mask = cv.medianBlur(mask,5)
        #Fonction qui détecte les cercles. Trouve un seul cercle ou deux à chaque fois en fonction de nbmires
        circles = cv.HoughCircles(mask,cv.HOUGH_GRADIENT,1,minDist = 100,
                                    param1=50,param2=20,minRadius=20 ,maxRadius=30)

        if circles is not None:
            circles = np.int16(np.around(circles))
            for i in circles[0,:nbmires]:
                
                centers.append([i[0]+beg2%length,i[1]+beg1%height])

                #Dessin des cercles
                if draw :
                    cv.circle(cimg,(i[0]+beg2%length,i[1]+beg1%height),i[2],(0,255,0),20)
                    cv.circle(cimg,(i[0]+beg2%length,i[1]+beg1%height),2,(0,0,255),3)

    if draw :
        plt.imshow(cimg)
        plt.show()

    assert len(centers) == 8, "Mires manquantes"

    return np.array(centers)



#Détection à la main de la frontière supérieure verte :

def horiz_pcb(img,draw=False) :
    """Finds the position of the top and bottom contour of a given PCB.

    Arguments :

    img - array of pixels : the working image (in BGR)

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray, np.ndarray, float : The slopes, intercepts of both contours, and the average spacing between top and bottom 
    """

    lower_bound = np.array([0, 40, 0])
    upper_bound = np.array([40,110,110])
    bwimg = cv.inRange(img, lower_bound, upper_bound) #On passe l'image en noir et blanc avec un threshold
    imagemask_green = cv.medianBlur(bwimg,25) #Uniformisation du tout

    middle = img.shape[1]//2

    top_contour = np.zeros((1000,2),dtype=np.int32) #On prend 1000 points au dessus, et 1000 en dessous de la carte
    bot_contour = np.zeros((1000,2),dtype=np.int32)

    for j in range(middle - 2000, middle - 1500) :

        top_contour[(j - middle + 2000)] = [j,min(np.where(imagemask_green[:,j] == 255)[0])] #Position des premiers et derniers pixels blancs
        bot_contour[(j - middle + 2000)] = [j,max(np.where(imagemask_green[:,j] == 255)[0])]

    for j in range(middle + 1500, middle + 2000) : 

        top_contour[(j - middle-1000)] = [j,min(np.where(imagemask_green[:,j] == 255)[0])] #idem
        bot_contour[(j - middle-1000)] = [j,max(np.where(imagemask_green[:,j] == 255)[0])]

    top_regress = stats.linregress(top_contour[:,0], top_contour[:,1]) #Régressions linéaires des points que l'on vient de trouver
    bot_regress = stats.linregress(bot_contour[:,0], bot_contour[:,1])

    slopes = [top_regress.slope, bot_regress.slope] 
    intercepts = [int(top_regress.intercept), int(bot_regress.intercept)]

    #écart entre le contour du haut et celui de bas pour trouver l'écart moyen (dilatation)
    spacing = bot_contour[:,1]-top_contour[:,1]

    #Pour dessiner les résultats et éventuellement ajuster la zone de repérage de bord
    if draw :

        img_copy=img.copy()

        for i in range(len(top_contour)):
            cv.circle(img_copy,(top_contour[i][0], top_contour[i][1]),15,(255,0,0),15)
            cv.circle(img_copy,(bot_contour[i][0], bot_contour[i][1]),15,(255,0,0),15)

        plt.imshow(img_copy)
        plt.show()

    ## XXX : pas besoin de renvoyer les informations sur le contour supérieur parce qu'il n'est pas utilisé ailleurs à ma connaissance 
    ## (il sert pour trouver l'écart de dilatation)
    return slopes,intercepts,np.mean(spacing) #On renvoie l'écart moyen (dilatation)



## Fonction qui trouve la ligne verticale qui est en théorie le fil de cuivre au centre du pcb

def trouve_ligne(img, draw=False):
    """Finds the position of a vertical wire at the center of the PCB.

    Arguments :

    img - array of pixels : the working image (in BGR)

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : tuple of floats, int, int : average rho and theta found with the Hough Line algorithm ; positions of the cropped image
    """
    (height,width) = img.shape

    img = img[height//3 : height//2, width//2 - 200 : width//2 + 200]
    img_copy = img.copy()

    img = cv.medianBlur(img,3)

    dst = cv.Canny(img, 50, 200, None, 3)

    lines = cv.HoughLines(dst, 1, np.pi / 360, 220, None, 0, 0,min_theta=-np.pi/8, max_theta=np.pi/8)

    lines = lines[:2,0,:] #XXX On ne conserve que les deux premières lignes, qui sont celles qui nous intéressent (sauf s'il a décidé d'en trouver d'autres avant)

    #Si le paramètre draw est activé, on fait un rendu
    if draw:
        for line in lines:
            rho,theta = line
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
    
            cv.line(img_copy,(x1,y1),(x2,y2),(255,0,0),10)
        
        plt.imshow(img_copy)
        plt.show()

    #On fait la moyenne des deux lignes que l'on vient de trouver
    median_line = np.mean(lines,axis=0)

    return median_line, width//2 - 200, height//2 #On renvoie la ligne et la translation de l'origine (alpha, beta)


# Fonction qui calcule la matrice de passage et l'origine du repère absolu pour une image donnée

def matrice_psg(img, draw = False):
    """Returns the transition matrix of a given image from the coordinate system of the image to the 
    transitory coordinate system of the image, as well as the origin of the transitory coordinate system
    and the dilatation of the image.
    The transitory coordinate system is used to find the positions of the targets in the wired image,
    thus giving us access to the absolute coordinate system. Its origin is at the intersection of the
    bottom of the PCB and the vertical wire at the center of the PCB. 

    Arguments :

    img - array of pixels : the working image (in BGR)

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray, np.ndarray, float
    """
    [rho,theta],alpha,beta = trouve_ligne(cv.cvtColor(img,cv.COLOR_BGR2GRAY), draw)
    [_,c],[_,d], dilatation = horiz_pcb(img, draw) #Droite horizontale y = cx + d

    ## Si droite parfaitement verticale, ie theta = 0
    if theta==0 :
        pt_intersection = (int(alpha + rho), int(c*(alpha+rho) + d))
        vert_vector = np.array([0,1])

    else :
        a = -(np.cos(-theta)/np.sin(-theta)) ### ATTENTION : comme y vers le bas, il faut penser à inverser les signes
        b = (rho/np.sin(-theta) + beta + alpha/np.tan(-theta)) #Droite verticale y = ax + b

        x = int((d-b)/(a-c))
        ## FIXME : ne fonctionne pas avec ax + b pour une raison qui m'échappe, et est pas très précis
        pt_intersection = (x,int(c*x+d))
        
        #Vecteur directeur de la partie haute
        vert_vector = normalize(np.array([1,-a]))
    
    # Vecteur directeur de la partie basse
    horiz_vector = normalize(np.array([1,c]))

    matrice_passage = np.transpose(np.array([horiz_vector,vert_vector])) #Matrice de passage de l'espace normal à l'espace qui nous intéresse

    return matrice_passage, pt_intersection, dilatation
    


def mires_cablees(path, draw = False):
    """Finds the positions of the targets on a wired PCB.

    Arguments :

    path - string : the path to the wired image.

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray : array of new centers.
    """
    
    ## Récupération du couple d'images
    img_cablee = cv.imread(path)
    img_non_cablee = cv.imread('ModulePictures/' + trouver_la_paire(path,"ModulePictures"))

    ## On trouve le centre des mires sur l'image non câblée
    centres_mires = mires(img_non_cablee)

    ## On trouve le repère absolu dans l'image non câblée
    matrice_passage_init, pt_intersection_init, dilatation_init = matrice_psg(img_non_cablee, draw)

    ## On trouve le repère absolu dans l'image câblée
    matrice_passage_dst, pt_intersection_dst, dilatation_dst = matrice_psg(img_cablee, draw)

    ## On calcule la dilatation relative
    dilatation = (dilatation_dst)/dilatation_init

    ## On calcule la position des mires sur la carte câblée à partir du repère absolu (changement de repère x2)
    nouveaux_centres = []
    for centre in centres_mires:
        nouveaux_centres.append(np.dot(np.linalg.inv(matrice_passage_dst),dilatation*np.dot(matrice_passage_init,centre - pt_intersection_init)) + pt_intersection_dst)

    ## On arrondit en entiers
    nouveaux_centres = np.array(nouveaux_centres).astype(np.int16)

    return nouveaux_centres



## Fonction qui renvoie le repère absolu de l'image câblée

def repere_absolu(path, draw = False):
    """Returns the transition matrix to the absolute coordinate system, as well as its origin
    and the dilatation factor.

    Arguments :

    path - string : the path to the wired image.

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray, np.ndarray, float
    """

    ## Fonction précédente
    centres = mires_cablees(path, draw)

    ## Dilatation mesurée du ces nouvelles mires
    dilat_measured = 0.5*(np.linalg.norm(centres[0]-centres[5]) + np.linalg.norm(centres[1]-centres[4]))

    centres_en_ij = np.flip(centres,axis=1)

    a = sum([(centres_en_ij[i+4,0]-centres_en_ij[i,0])/(centres_en_ij[i+4,1]-centres_en_ij[i,1]) for i in range(0,4)])/4 #Pente horizontale moyenne
    origine = np.mean(centres,axis=0).astype(np.int16)

    mat_passage = 1/np.sqrt(a**2 + 1) * np.array([[1,-a],[a,1]])

    if draw: afficher_points(cv.imread(path),centres)

    return mat_passage, origine, dilat_measured #Origine renvoyée en x,y



## Fonction qui trouve les pads sur n'importe quelle image
## TODO : importer les positions absolues des pads depuis le ficher JSON, et dilat_ref

def find_pads(path, draw=False):
    """Returns the positions of the pads on any given wired board.

    Arguments :

    path - string : the path to the wired image.

    draw - bool : whether or not the function should return images of what it is doing.

    Returns : np.ndarray : array of pads
    """

    mat, origine, dilat_measured = repere_absolu(path, draw)

    dilatation = dilat_measured/dilat_ref

    #Trouve les pads en inversant la matrice de passage
    pads_img = np.array([np.dot(np.linalg.inv(mat),dilatation*pads_nouveau_repere[i])+np.flip(np.array([origine,origine]),axis = 1) for i in range(46)]).astype(np.int16)

    img = cv.imread(path)

    #Dessin des pads
    if draw :
        for pad in pads_img :
            cv.rectangle(img,np.flip(pad[0]),np.flip(pad[1]),(255,0,0),15)

        afficher(img)

        plt.imshow(img)
        plt.show()

    return pads_img