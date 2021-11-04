# Цей скрипт містить клас нашого бота.

# Тут ми будемо використовувати модуль pyautogui для автоматизованих натискань та друку,
# та функцію `get_positive_int_input` з скрипта utils.py,
# для того щоб отримати тривалість вiдео у хвилинах та секундах,
# та iнтервал мiж рекламними паузами, вiд користувача
import pyautogui
from utils import get_positive_int_input as int_input


class Bot:

    # Метод __init__ - це конструктор об'єкта Bot.
    # Щоб ініціалізувати новий об'єкт Bot, потрiбно написати:
    # our_bot = Bot()
    def __init__(self) -> None:
        # Спочатку ми отримуємо вхiднi данi вiд користувача та встановлюємо значення у поля класу
        self.minutes = int_input("Введiть тривалiсть вiдео у хвилинах")
        self.seconds = int_input("Введiть остачу вiд тривалостi вiдео у секундах", seconds=True)
        self.interval = int_input("Введiть цiлий iнтервал мiж рекламними паузами")
        # Далi ми створюємо поля класу, якi будуть змiнювати своє значення
        # протягом усього процесу автоклiкiнга, допоки вони не досягнуть значення загальної тривалостi вiдео
        self.current_minutes = 0
        self.current_seconds = 0
        # А це поля для координат кнопки додавання рекламної паузи i таймлайна.
        # Вони будуть пiзнiше отриманi зi скрiншота з використанням Tesseract-OCR.
        self.timeline_x = 0
        self.timeline_y = 0
        self.add_x = 0
        self.add_y = 0

    # Цей метод буде викликано пiсля того, як Tesseract-OCR
    # отримає всi потрiбнi координати зi скрiншота
    def specify_coords(self, tx: int, ty: int, ax: int, ay: int) -> None:
        self.timeline_x = tx
        self.timeline_y = ty
        self.add_x = ax
        self.add_y = ay

    # Тепер перейдемо до методiв, якi будуть використанi у процесi автоклiкiнга.
    # Цей метод перевiряє, чи не досягли значення current_minutes та current_seconds
    # загальної тривалостi вiдео.
    def __can_time_be_incremented__(self) -> bool:
        return self.current_minutes < self.minutes or \
            (self.current_minutes == self.minutes and \
                self.current_seconds <= self.seconds)
    
    # Цей метод встановлює значення current_minutes та current_seconds
    # на момент наступної рекламної паузи. Логiчно, що якщо current_seconds перевищує 60,
    # воно скидується та додається одна хвилина.
    def __increment_time__(self) -> None:
        self.current_seconds += self.interval
        if self.current_seconds >= 60:
            self.current_minutes += self.current_seconds // 60
            self.current_seconds %= 60

    # Цей метод автоматично друкує двокрапку в таймлайнi
    def __write_colon__(self) -> None:
        pyautogui.press(["shift", ":"])

    # Цей метод очищає таймлайн, натискаючи на нього тричi,
    # а далi натискаючи клавiшу `backspace`
    def __clear_timeline__(self) -> None:
        pyautogui.moveTo(x=self.timeline_x, y=self.timeline_y)
        pyautogui.click(clicks=3, interval=0.1)
        pyautogui.press("backspace")

    # Цей метод автоматично натискає на кнопку додавання рекламної паузи
    def __add_pause__(self) -> None:
        pyautogui.moveTo(x=self.add_x, y=self.add_y)
        pyautogui.click()
    
    # Цей метод автоматично друкує момент даної рекламної паузи у таймлайн
    def __write_time__(self) -> None:
        pyautogui.write("0" + str(self.current_minutes) \
            if self.current_minutes < 10 else str(self.current_minutes))
        self.__write_colon__()
        pyautogui.write("0" + str(self.current_seconds) \
            if self.current_seconds < 10 else str(self.current_seconds))
        self.__write_colon__()
        pyautogui.write("00")
    
    # Цей метод викликається, коли всi координати вказано.
    # Вiн запускає цикл `while`, який чистить таймлайн, записує час,
    # додає нову рекламну паузу та iнкрементує час, допоки його значення
    # не досягне значення загальної тривалостi вiдео
    def run(self) -> None:
        if not (self.add_x == 0 and self.add_y == 0 and self.timeline_x == 0 and self.timeline_y == 0):
            while self.__can_time_be_incremented__():
                self.__clear_timeline__()
                self.__write_time__()
                self.__add_pause__()
                self.__increment_time__()
            print("Процес завершений!")

# Запуск самого цього скрипта просто не має сенсу