from Coordinates.find_absolute import repere_absolu
import sys

"""
This file is used to find the absolute coordinate system of an image, enabling us to find later on the positions of the pads,... on a
given image

Arguments
-----------
path - str : the path to the image to analyse.

draw - bool (Optional) : whether or not to return images of evey step of the process.

Returns : Prints the transition matrix to the absolute coordinate system, as well as its origin and the dilatation of the given image
"""

if __name__ == '__main__' :
    path = sys.argv[1]

    if len(sys.argv) == 2 :
        print(repere_absolu(path))

    else :
        draw=sys.argv[2] 
        print(repere_absolu(path,draw))