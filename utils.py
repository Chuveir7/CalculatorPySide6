import re
from pathlib import Path

# dirs
ROOT_DIR = Path(__file__).parent
FILES_DIR = ROOT_DIR / 'files'
ICON_PATH = FILES_DIR / 'icon.ico'

# font sizes
BIG_FONT_SIZE = 40
MEDIUM_FONT_SIZE = 24
SMALL_FONT_SIZE = 15 

# sizing
MINIMUM_WIDTH = 30 
MINIMUM_HEIGHT = BIG_FONT_SIZE * 2
TEXT_MARGIN = 15 

# Colors 
PRIMARY_COLOR = '#264d73'
DARKER_PRIMARY_COLOR =  '#132639'
DARKEST_PRIMARY_COLOR = '#060d13'

#functions 
NUM_OR_DOT_REGEX = re.compile(r'^[0-9.]$')

def isNumOrDot(string: str):
    return bool(NUM_OR_DOT_REGEX.search(string))

# check if the string is empty
def isEmpty(string: str):
    return len(string) == 0 


def isValidNumber(string: str):
    valid = False
    try:
        float(string)
        valid = True
    except ValueError:
        valid = False
    return valid 

def convertToNumber(string):
    number = float(string)

    if number.is_integer():
        number = int(number)

    return number