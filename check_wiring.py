from Wiring_Checks.wire import analyseWires
import sys

"""
This file is used to run checks on an image, namely the number of wires and whether or not these wires are in contact.

Arguments
-----------
path - str : the path to the image to analyse.

Returns : the wire count next to the theoretical one ; creates an image highlighting the touching wires.
"""

if __name__ == '__main__' :
    path = sys.argv[1]
    analyseWires(path)