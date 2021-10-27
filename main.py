# Here is our main script, which will be run, when the .exe file
# will be executed. If you will use this bot directly via Python
# sources, you have to run exactly this file and not the other one.

# Let's import all the needed modules.
# Firstly, we import sys to use sys.exit() method that will terminate the program,
# if an error occurs in Tesseract-OCR
import sys
# Then, we will need `sleep` method from time module, to create a 10-second delay
# after all the data for bot is specified.
from time import sleep
# Import the Bot class itself from the bot.py script
from bot import Bot
# And lastly, we import needed stuff from core.py script: functions to get
# `Add pause` button and timeline coords for the bot,
# to find text on the screenshot using Tesseract-OCR,
# to take the screenshot itself,
# and NotEverythingFoundError class to handle this exception, if there were problems
# with getting coords for bot
from core import get_coords_for_bot, find_text, take_screenshot, NotEverythingFoundError

# The main block of our program
if __name__ == "__main__":
    # Firstly we say welcome to the user in the console,
    # and ask them to follow the instructions
    print("Welcome to adbot by vsdum! Please follow the instructions...")
    # Next we initialize the Bot object,
    # it will get video duration in minutes and seconds, and interval between ad pauses,
    # from the user input
    bot = Bot()
    print("Bot object is initialized!")
    print("Now you will have 10 seconds to open your YouTube video's ad pauses editor page.")
    # Now we give our user ten seconds to open video editor page after pressing Enter
    input("Press Enter to start this timer. ")
    # Here we use `sleep` method from time module to set 10-second delay
    sleep(10)
    # Receiving list of the characters, found by Tesseract-OCR on the screenshot
    data = find_text(take_screenshot())
    # If there is no Tesseract-OCR installed on your machine, the program will be `killed`
    # It mustn't happen, because if you didn't previously install Tesseract-OCR,
    # the program will download it locally automatically.
    if data is None:
        sys.exit()
    else:
        # So, if there were no problems with locating Tesseract-OCR on the user's machine,
        # We start the main process. Here, firstly we get `Add pause` button and timeline coords.
        # Notice that here we added exception handler, in case if not all coords were found by OCR.
        try:
            coords = get_coords_for_bot(data)
            # When we received all the needed coords, we put them to the bot object
            bot.specify_coords(coords[0], coords[1], coords[2], coords[3])
            # And finally, we run our bot
            bot.run()
            print("Thank you for using my bot! I wish you good luck with your YouTube channel!")
            input("Press Enter to exit. ")
        # If exception occurs, we simply say to the user, what had happened.
        # In the end we call input(), to give the user some time to read the console output.
        except NotEverythingFoundError:
            print("ERROR: Not all the needed coords were found by OCR system. Try again (try change browser theme to light, or increase the GUI scale)")
            input()