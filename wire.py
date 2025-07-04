import numpy as np
import matplotlib.pyplot as plt
import cv2
import scipy
from collections import deque
import json

# open the json with the iref for each module

with open(".\iref_trim_per_module.json", "r") as f:
    data = json.load(f)

# Utils functions for analyzing pixels in general

def norm(pix: np.ndarray) -> float:
    """Computes the norm of an rgb pixel.

    Arguments :
    pix - array of floats : the pixel.

    Returns : float
    """
    return float(pix[0])**2 + float(pix[1])**2 + float(pix[2])**2


def isWhite(img: np.ndarray, coord: tuple, threshold = 90000) -> bool:
    """Tests whether or not a pixel is considered white, using an arbitrary threshold.

    Arguments :

    img - array of pixels : the working image

    coord - tuple of ints : the coordinates of the pixel

    threshold - float : arbitrary threshold

    Returns : bool
    """
    return norm(img[coord[0],coord[1],:]) > threshold


def validCoord(img: np.ndarray, coord: tuple) -> bool:
    """Tests whether or not the coordinates are within the boundaries of the image.

    Arguments :

    img - array of pixels : the working image

    coord - tuple of ints : the coordinates of the working pixel

    Returns : bool
    """
    return 0 <= coord[0] and coord[0] < len(img) and 0 <= coord[1] and coord[1] < len(img[0])



# Intermediate functions for the Breadth-First Search (BFS) wire recognition function

def neighboursList(img: np.ndarray, coord: tuple) -> list:
    """Creates the list of coordinates of the neighbouring white pixels given the current pixel.

    Arguments :

    img - array of pixels : the working image

    coord - tuple of ints : the coordinates of the current pixel

    Returns : list of coordinates
    """
    directions_list = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    neighbours_list = []
    for direction in directions_list:
        neighbour_coord = (coord[0] + direction[0], coord[1] + direction[1])
        if validCoord(img,neighbour_coord) and isWhite(img,neighbour_coord):
            neighbours_list.append(neighbour_coord)
    return neighbours_list


def visit(img: np.ndarray, coord: tuple, wire: list,queue: deque):
    """Visits (i.e. adds to the visiting queue) all the unvisited neighbouring white pixels given the current pixel.

    Arguments :

    img - array of pixels : the working image

    coord - tuple of ints : the coordinates of the current pixel

    wire - list of coordinates : the list of pixels already visited

    queue - deque of coordinates : the visiting queue
    """
    neighbours_list = neighboursList(img,coord)
    for neighbour in neighbours_list:
        if (neighbour not in wire) and (neighbour not in queue):
            queue.append(neighbour)



# Breadth-First Search (BFS) wire recognition function

def bfsWire(img: np.ndarray, start_coord: tuple) -> list:
    """Creates the list of coordinates of all the pixels of a wire given a starting pixel, using a Breadth-First Search (BFS) algorithm.

    Arguments : 

    img - array of pixels : the working image

    start_coord - tuple of ints : the coordinates of the starting pixel

    Returns : list of coordinates
    """
    wire = []
    queue = deque()
    queue.append(start_coord)
    while len(queue) != 0:
        current_coord = queue[0]
        if current_coord not in wire:
            wire.append(current_coord)
        visit(img,current_coord,wire,queue)
        queue.popleft()
    return wire



# Finding the edges coordinates of a given wire

def extremeCoords(wire: list, side = "left") -> int:
    """Finds the index of either the leftmost or the rightmost pixel of a wire, depending on the input side.

    Arguments :

    wire -- list of coordinates : the list of all pixels in the wire

    side -- string : the side chosen for finding the extreme coordinate, by default : left

    Returns : int
    """
    directions = {"left":-1, "right":1}
    index = 0
    for i in range(1,len(wire)):
        if directions[side] * (wire[i][1] - wire[index][1]) < 0:
            index = i
    return index


def wireEdges(wire: list,) -> tuple:
    """Gives the coordinates of both the leftmost and the rightmost pixels of a wire.

    Arguments :

    wire -- list of coordinates : the list of all pixels in the wire

    Returns : tuple of coordinates
    """
    i_left , i_right = extremeCoords(wire, "left"), extremeCoords(wire, "right")
    return (wire[i_left], wire[i_right])



# Checking if a wire is touching another

def isTouching(wire: list, threshold = 2900) -> bool:
    """Tests whether or not a wire is touching another by checking if it contains too many pixels.

    Arguments :

    wire -- list of coordinates : the list of all pixels in the wire

    threshold - int : arbitrary threshold for how many pixels is too many pixels

    Returns : bool
    """
    return len(wire) > threshold


# Theoretical number of wires

def extract_serial_number (file_name) :
    """Extracts the serial number (starting with 20UPGM) of a module

    Arguments :

    file_name - string : name of the file with the serial number in it

    Returns : string
    """
    names = file_name.split("_")
    for x in names :
        if "20UPGM" in x :
            return (x)
    assert False, "No serial number found in the file name"


def iref_trim (serial_number, data) :
    """Reads the iref of a module

    Arguments :

    serial_number - string : serial number of the module

    data - list[dict] : iref of each module

    Returns : (int, int, int, int)
    """
    ok = False
    for x in data :
        if x['serialNumber'] == serial_number :
            iref = x
            ok = True
    assert ok, "Serial number not found"
    return (iref['IREF_TRIM_1'], iref['IREF_TRIM_2'], iref['IREF_TRIM_3'], iref['IREF_TRIM_4'])


def expected_wire_number (serial_number, data) :
    """Calculates the theoretical number of wires of a module

    Arguments :

    serial_number - string : serial number of the module

    data - list[dict] : iref of each module

    Returns : int
    """
    iref = iref_trim(serial_number, data)
    nb_wire_per_trim = [4, 3, 3, 2, 3, 2, 2, 1, 3, 2, 2, 1, 2, 1, 1, 0] # number of wires expected depending on iref
    return (693 + nb_wire_per_trim[iref[0]] + nb_wire_per_trim[iref[1]] + nb_wire_per_trim[iref[2]] + nb_wire_per_trim[iref[3]]) # 693 wires independant of iref + number of iref wires


# Counting the real number of wires

def crop_ligns (image, level = 0.55) :
    """Determines the limits of the vertical zone of interest of the picture

    Arguments :

    image - array of pixels : the working image

    level (optional) - int : limit of greenness before the algorithm stops

    Returns : (int, int)
    """
    green = image[:,:,1].sum(axis=1) / (image[:,:,0].sum(axis=1) + image[:,:,2].sum(axis=1))
    n = image.shape[0]

    limit_high = 0
    x = green[limit_high]
    while (limit_high < n//2) and (x <= level) :
        limit_high+=1
        x = green[limit_high]
    
    limit_low = n-1
    x = green[limit_low]
    while (limit_low > n//2) and (x <= level) :
        limit_low-=1
        x = green[limit_low]
    
    return (limit_high + 25, limit_low - 22) # +25 and -22 : gaps between the green area and the wire zone


def count (image_grey_crop, column) :
    """Count the number of wires in a specific column

    Arguments :

    image_grey_crop - array of pixels : the working greyscale image, cropped vertically

    column - int : column of interest

    Returns : int
    """
    peaks, _ = scipy.signal.find_peaks(image_grey_crop[:,column], distance=3, prominence=50, height=190, width=(0,9)) # appropriate parameters were determined with already existing datasets
    return (peaks.shape[0])


def crop_columns_left (image_grey_crop, level = 100) :
    """Determines the left limit of the wire zone

    Arguments :

    image_grey_crop - array of pixels : the working greyscale image, cropped vertically

    level (optionnal) - int : number of wires required before the algorithm stops

    Returns : int
    """
    n = image_grey_crop.shape[1]
    left = 0
    count_left = count(image_grey_crop, left)
    while (count_left < level) and (left < n) :
        left += 1
        count_left = count(image_grey_crop, left)
    return (left)


def crop_columns_right (image_grey_crop, level = 100) :
    """Determines the right limit of the wire zone

    Arguments :

    image_grey_crop - array of pixels : the working greyscale image, cropped vertically

    level (optionnal) - int : number of wires required before the algorithm stops

    Returns : int
    """
    n = image_grey_crop.shape[1]
    right = n - 1
    count_right = count(image_grey_crop, right)
    while (count_right < level) and (right > 0) :
        right -= 1
        count_right = count(image_grey_crop, right)
    return (right)


# Useful fonctions

def test_wire_number (file_name, data) :
    """Tests whether the number of wires on a module is correct or not

    Arguments :

    file_name - string : name of the file (the image must be in the same folder as this programm)

    data - list[dict] : iref of each module

    Returns : 
    test - bool : True if the number of wires is correct, False otherwise
    expected_nb - int : theoretical number of wires
    real_nb - int : number of wires counted
    """
    expected_nb = expected_wire_number(extract_serial_number(file_name), data)

    image = cv2.imread(file_name)
    n = image.shape[1]

    high_l, low_l = crop_ligns(image[:,:n//2])
    high_r, low_r = crop_ligns(image[:,n//2:])
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    left = crop_columns_left(grey[high_l:low_l])
    right = crop_columns_right(grey[high_r:low_r])

    real_nb_left = count(grey[high_l:low_l], column = left+35) # +35 : gap between the left limit of the wire zone and the column with every wires
    real_nb_right = count(grey[high_r:low_r], column = right-35) # -35 : gap between the right limit of the wire zone and the column with every wires
    real_nb = real_nb_left + real_nb_right
    test = expected_nb == real_nb

    return (test, expected_nb, real_nb)


def wire_pos (image) :
    """Gives the position of every wire detected

    Arguments :

    image - array of pixels : the working image

    Returns :
    
    real_peaks_left - array of int : the ordinates of the wires on the left side

    real_left - int : the abscissa of the wires on the left side (same for all wires)

    real_peaks_right - array of int : the ordinates of the wires on the right side

    real_right - int : the abscissa of the wires on the right side (same for all wires)
    """
    n = image.shape[1]

    high_l, low_l = crop_ligns(image[:,:n//2])
    high_r, low_r = crop_ligns(image[:,n//2:])
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    left = crop_columns_left(grey[high_l:low_l])
    right = crop_columns_right(grey[high_r:low_r])

    peaks_left, _ = scipy.signal.find_peaks(grey[high_l:low_l, left+35], distance=3, prominence=50, height=190, width=(0,9))
    peaks_right, _ = scipy.signal.find_peaks(grey[high_r:low_r, right-35], distance=3, prominence=50, height=190, width=(0,9))
    real_peaks_left, real_left, real_peaks_right, real_right = peaks_left + high_l, left+35, peaks_right + high_r, right-35

    return(real_peaks_left, real_left, real_peaks_right, real_right)



# Combining start pixel detection, wire counting and wire plotting


def analyseWires(filename: str):
    """Highlights all the wires in an image, with different colors if a pixel is touching another.

    Arguments : 

    filename - str : the file name of the working image
    """
    img = plt.imread(filename)
    n_expected = expected_wire_number(extract_serial_number(filename),data)
    copy = img.copy()
    (x_list_left,y_left,x_list_right,y_right) = wire_pos(img)
    n_detected = len(x_list_left) + len(x_list_right)
    for (x_list, y) in [(x_list_left,y_left),(x_list_right,y_right)]:
        for x in x_list:
            wire = bfsWire(img,(x,y))
            if isTouching(wire):
                for pixel in wire:
                    copy[pixel[0],pixel[1],:] = np.array([0,0,255])
            edges = wireEdges(wire)
    cv2.imwrite("result.jpg",copy)
    print("Wires expected : " + str(n_expected))
    print("Wires detected : " + str(n_detected))


# Testing

analyseWires("1005_20UPGM23211816_AfterBonding.jpg")