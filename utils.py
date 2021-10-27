# This script contains useful functions for our program

# Import windll object from ctypes module
# to get monitor's width and height in pixels
from ctypes import windll
# Also we need walk method from os module,
# to get all the files and subfolders in given folder
from os import walk
# And also join method from os.path module,
# to get full path to the definite file or folder,
# from given folders' and file name
from os.path import join


# First function is to get positive integer input from user.
# It is used in Bot object initialization.
# Here we add optional `seconds` param of boolean type.
# When the bot asks for the rest of the video duration in seconds,
# the seconds value CAN'T be negative but CAN be zero.
def get_positive_int_input(hint: str, seconds=False) -> int:
    # If we convert user input from string to integer,
    # but the user didn't put in the correct data,
    # the ValueError exception will occur.
    # Here we add exception handler, that will try to get user input
    # again, if input data was incorrect
    try:
        result = int(input(hint + ": "))
        # And also here we need exactly positive integers,
        # because video duration and interval between pauses can't be negative.
        # So, if the input is non-positive, we manually raise ValueError exception,
        # and as we already have a handler for this exception, user will be asked
        # for input again.
        # But the rest of the video duration in seconds also can be zero,
        # so here we need to add an extra check.
        if ((not seconds) and result <= 0) or result < 0:
            raise ValueError()
        # Finally, if the input is totally correct, we return it.
        else:
            return result
    except ValueError:
        print("ERROR! Input data must be of integer type and be non-negative. Try again...")
        return get_positive_int_input(hint)


# The second function will return the user's monitor resolution in pixels.
# The output is tuple containing width and height of the monitor
def get_monitor_size() -> tuple:
    return (
        windll.user32.GetSystemMetrics(0),
        windll.user32.GetSystemMetrics(1)
    )


# And one more function, that looks for the file with given name
# in the given folder. Here we use some methods from
# os and os.path modules
def find_files(filename, search_path) -> list:
    result = []
    for root, d, files in walk(search_path):
        if filename in files:
            result.append(join(root, filename))
    return result


# This script can be run only for debug.
# It will just print user's monitor resolution in the console.
if __name__ == "__main__":
    width, height = get_monitor_size()
    print("Your monitor is " + str(width) + "x" + str(height))