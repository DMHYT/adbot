# This is the script where the main processes,
# like taking screenshot and running OCR system, will happen

# Things that we need to import:
# join method from os.path module to concatenate paths
# in order to get full path to the definite file or folder
from os.path import join
# re module to create regular expressions, with which
# we will try to match characters found by OCR,
# in order to find timeline position
import re
# mss function from mss module to take a screenshot
from mss import mss
# asarray method from numpy library to convert
# mss ScreenShot object to pixel array
from numpy import asarray
# pytesseract module to run Tesseract-OCR from Python
import pytesseract as tess
# Some methods from opencv-python library to convert the screenshot,
# represented as numpy pixel array, into Image object,
# to use it in Tesseract-OCR
from cv2 import cvtColor, COLOR_BGR2GRAY
# Function for getting monitor width and height in pixels from utils.py script
from utils import get_monitor_size
# Function to get Tesseract-OCR binaries path from tesseract.py script
from tesseract import get_tesseract_cmd_path


# Firstly, we receive monitor width and height in pixels
# to specify screenshot resolution
MONITOR_SIZE = get_monitor_size()

# Then, we need to create two regular expressions, that will help us
# find timeline on the screenshot.
# The timeline looks like `nn:nn:nn`, where n is any number
# So we create `nn:nn:nn` pattern, and also `nnnnnn`, in case if
# Tesseract-OCR doesn't recognize colons in the timeline
TIMELINE_WITHOUT_COLONS = re.compile(r'^\d{6}')
TIMELINE_WITH_COLONS = re.compile(r'^\d{2}:\d{2}:\d{2}')


# Function to take a screenshot using mss module
def take_screenshot():
    with mss() as screenshoter:
        # Initializing ScreenShot object
        screen = screenshoter.grab({
            'left': 0,
            'top': 0,
            'width': MONITOR_SIZE[0],
            'height': MONITOR_SIZE[1]
        })
        # Converting it to numpy array
        img = asarray(screen)
        # Converting it one more time into OpenCV Image object,
        # and also grayscaling it to make it easier to recognize
        # characters for Tesseract-OCR
        rgb = cvtColor(img, COLOR_BGR2GRAY)
        # Returning resulting image object
        return rgb


# Function to filter data dictionary returned by Tesseract-OCR
# after finishing the OCR process
def filter_data_dict(dic: dict) -> None:
    # Removing unneeded keys from the dictionary
    del dic['level']
    del dic['page_num']
    del dic['block_num']
    del dic['par_num']
    del dic['line_num']
    del dic['word_num']
    # Converting confidency values from stringified float to integer
    for i in range(len(dic['conf'])):
        if not isinstance(dic['conf'][i], int):
            dic['conf'][i] = int(float(dic['conf'][i]))
    # Removing all the elements with confidency parameter of -1 value
    done: bool = False
    while not done:
        try:
            index = dic['conf'].index(-1)
            for key in ('left', 'top', 'width', 'height', 'conf', 'text'):
                dic[key].pop(index)
        except ValueError:
            done = True


# Function to make data dictionary structure more readable.
# Before this function call the data dictionary looks like:
'''
{
'left': [left1, left2, left3, left4, left5, ...],
'top': [top1, top2, top3, top4, top5, ...],
'width': [width1, width2, width3, width4, width5, ...],
'height': [height1, height2, height3, height4, height5, ...],
'conf': [conf1, conf2, conf3, conf4, conf5, ...],
'text': [text1, text2, text3, text4, text5, ...]
}
'''
# And the output of the structurize function looks like:
'''
[
(left1, top1, width1, height1, conf1, text1),
(left2, top2, width2, height2, conf2, text2),
(left3, top3, width3, height3, conf3, text3),
(left4, top4, width4, height4, conf4, text4),
(left5, top5, width5, height5, conf5, text5),
...
]
'''
def structurize(dic: dict) -> list:
    return [
        (
            dic['left'][i],
            dic['top'][i],
            dic['width'][i],
            dic['height'][i],
            dic['conf'][i],
            dic['text'][i]
        ) for i in range(len(dic['left']))
    ]


# Function that runs Tesseract-OCR process and returns
# list of found character sets, with coordinates on the screen corresponding to them
def find_text(rgb, tess_path=get_tesseract_cmd_path()) -> list:
    # If Tesseract-OCR was not found, returning None.
    # In normal conditions this case can't be, for more detailed
    # information about this, go to tesseract.py script
    if tess_path is None:
        print("Tesseract was not found on your machine :-(")
        return None
    else:
        # Setting path to OCR trained data directory,
        # and path to Tesseract executable
        tess.pytesseract.environ.setdefault(
            "TESSDATA_PREFIX",
            join(tess_path, "tessdata")
        )
        tess.pytesseract.tesseract_cmd = join(tess_path, "tesseract.exe")
        # Getting the data dictionary from Tesseract-OCR
        data: dict = tess.image_to_data(
            # Putting our screenshot Image object,
            # setting dictionary output type and Russian language
            rgb, output_type=tess.pytesseract.Output.DICT,
            config=r'-l rus'
        )
        # Filtering and structurizing the data dictinary
        filter_data_dict(data)
        result = structurize(data)
        # For better performance in next steps,
        # we remove all the characters sets with length below 4
        result = list(filter(lambda el: len(el[5]) > 4, result))
        # Returning the filtered data list
        return result


# Class of the exception to raise when not all coordinates
# for bot job were found.
# It is just an empty class, inherited from base Python exception class
class NotEverythingFoundError(Exception):
    def __init__():
        super.__init__()


# Function that returns a 4-element tuple containing
# `Add pause` button and timeline coords by X and Y axis
def get_coords_for_bot(data: list) -> tuple:
    # Creating variables for coords,
    # setting them to impossible values
    tx = ax = MONITOR_SIZE[0] + 1
    ty = ay = MONITOR_SIZE[1] + 1
    for item in data:
        # The `Add pause` button looks like `+ AD PAUSE`,
        # `+ РЕКЛАМНАЯ ПАУЗА` in Russian. Looking for `РЕКЛАМНАЯ` word
        # and setting ax and ay coordinates
        if item[5] == "РЕКЛАМНАЯ":
            ax = item[0] + item[2]
            ay = item[1] + item[3] // 2
        # Then we find the timeline. Multiple character sets can
        # match our regular expressions, but the timeline is always
        # the most to the left of all.
        # Making corresponding check
        if TIMELINE_WITH_COLONS.match(item[5]) or \
                TIMELINE_WITHOUT_COLONS.match(item[5]):
            if tx > item[0]:
                tx = item[0] + item[2] // 2
                ty = item[1] + item[3] // 2
    # After the list scan, we check all the coords,
    # and if at least one remains at impossible value,
    # raising our custom exception
    if tx == MONITOR_SIZE[0] + 1 or \
        ax == MONITOR_SIZE[0] + 1 or \
        ty == MONITOR_SIZE[1] + 1 or \
        ay == MONITOR_SIZE[1] + 1:
            raise NotEverythingFoundError()
    # If no exceptions occured, we finally return
    # a tuple with X and Y coords of the timeline,
    # and then X and Y coords of the `Add pause` button
    return (tx, ty, ax, ay)


# This script can be run for debug.
# It will create a 3-second delay, after that
# the screenshot will be taken, and the OCR process output
# will be printed in the console
if __name__ == "__main__":
    from time import sleep
    sleep(3)
    [print(item) for item in find_text(take_screenshot())]