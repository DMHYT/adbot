# This script contains the class of our bot.

# Here we will use pyautogui module for automatic clicking and printing,
# and `get_positive_int_input` function from the utils.py script,
# to get the video duration in minutes and seconds, and interval between
# ad pauses, from the user
import pyautogui
from utils import get_positive_int_input as int_input


class Bot:

    # The __init__ method is a constructor of the Bot object.
    # To initialize new Bot object, we have to write like:
    # our_bot = Bot()
    def __init__(self) -> None:
        # Firstly we get user input and put the received values into the class fields
        self.minutes = int_input("Enter your video duration in minutes")
        self.seconds = int_input("Enter the seconds left after minutes", seconds=True)
        self.interval = int_input("Enter integer interval between ad pauses")
        # Then we create class fields, that will change their values
        # all the time during the auto-clicking process, until they reach total video duration value
        self.current_minutes = 0
        self.current_seconds = 0
        # And these are the fields for the coords of `Add pause` button and timeline.
        # They will be received from the screenshot using Tesseract-OCR later.
        self.timeline_x = 0
        self.timeline_y = 0
        self.add_x = 0
        self.add_y = 0

    # This method will be called after the Tesseract-OCR will get
    # all the needed coords from the screenshot
    def specify_coords(self, tx: int, ty: int, ax: int, ay: int) -> None:
        self.timeline_x = tx
        self.timeline_y = ty
        self.add_x = ax
        self.add_y = ay

    # Now let's get into methods, that will be used in auto-clicking process.
    # This method checks if current_minutes and current_seconds values
    # haven't reached the total video duration value yet.
    def __can_time_be_incremented__(self) -> bool:
        return self.current_minutes < self.minutes or \
            (self.current_minutes == self.minutes and \
                self.current_seconds <= self.seconds)
    
    # This method sets the current_minutes and current_seconds values to
    # the next ad pause moment. Logically, if current_seconds gets over 60,
    # it's been reset and a minute is added.
    def __increment_time__(self) -> None:
        self.current_seconds += self.interval
        if self.current_seconds >= 60:
            self.current_minutes += self.current_seconds // 60
            self.current_seconds %= 60

    # This method auto-prints colon to the timeline
    def __write_colon__(self) -> None:
        pyautogui.press(["shift", ":"])

    # This method clears timeline by clicking on it three times,
    # and then pressing `backspace` key
    def __clear_timeline__(self) -> None:
        pyautogui.moveTo(x=self.timeline_x, y=self.timeline_y)
        pyautogui.click(clicks=3, interval=0.1)
        pyautogui.press("backspace")

    # This method auto-clicks on `Add pause` button
    def __add_pause__(self) -> None:
        pyautogui.moveTo(x=self.add_x, y=self.add_y)
        pyautogui.click()
    
    # This method auto-prints current ad pause moment into the timeline
    def __write_time__(self) -> None:
        pyautogui.write("0" + str(self.current_minutes) \
            if self.current_minutes < 10 else str(self.current_minutes))
        self.__write_colon__()
        pyautogui.write("0" + str(self.current_seconds) \
            if self.current_seconds < 10 else str(self.current_seconds))
        self.__write_colon__()
        pyautogui.write("00")
    
    # This method is called, when all the coords are specified.
    # It starts a `while` loop, that clears timeline, writes time,
    # adds new ad pause and increments the time, until the end of the
    # video's total duration is reached
    def run(self) -> None:
        while self.__can_time_be_incremented__():
            self.__clear_timeline__()
            self.__write_time__()
            self.__add_pause__()
            self.__increment_time__()
        print("Finished!")

# And finally, launching this script itself just does not make sense