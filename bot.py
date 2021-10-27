# Этот скрипт содержит класс нашего бота.

# Здесь мы будем использовать модуль pyautogui для автоматизированных нажатий и печати,
# и функцию `get_positive_int_input` из скрипта utils.py,
# для того чтобы получить длительность видео в минутах и секундах,
# и интервал между рекламными паузами, от пользователя
import pyautogui
from utils import get_positive_int_input as int_input


class Bot:

    # Метод __init__ - это конструктор объекта Bot.
    # Чтобы инициализировать новый объект Bot, нужно написать:
    # our_bot = Bot()
    def __init__(self) -> None:
        # Сначала мы получаем ввод пользователя и устанавливаем полученные значения в поля класса
        self.minutes = int_input("Введите длительность видео в минутах")
        self.seconds = int_input("Введите остаток от длительности видео в секундах", seconds=True)
        self.interval = int_input("Введите целый интервал между рекламными паузами")
        # Далее мы создаём поля класса, которые будут изменять свои значения
        # на протяжении всего процесса автокликинга, пока они не достигнут значения общей длительности видео
        self.current_minutes = 0
        self.current_seconds = 0
        # А это поля для координат кнопки добавления рекламной паузы и таймлайна.
        # Они будут позже получены со скриншота с использованием Tesseract-OCR.
        self.timeline_x = 0
        self.timeline_y = 0
        self.add_x = 0
        self.add_y = 0

    # Этот метод будет вызван после того, как Tesseract-OCR
    # получит все нужные координаты со скриншота
    def specify_coords(self, tx: int, ty: int, ax: int, ay: int) -> None:
        self.timeline_x = tx
        self.timeline_y = ty
        self.add_x = ax
        self.add_y = ay

    # Теперь перейдём к методам, которые будут использованы в процессе авто-кликинга.
    # Этот метод проверяет не достигли ли значения current_minutes и current_seconds
    # общей длительности видео.
    def __can_time_be_incremented__(self) -> bool:
        return self.current_minutes < self.minutes or \
            (self.current_minutes == self.minutes and \
                self.current_seconds <= self.seconds)
    
    # Этот метод устанавливает значения current_minutes и current_seconds
    # на момент следующей рекламной паузы. Логично, что если current_seconds превышает 60,
    # он сбрасывается и добавляется одна минута.
    def __increment_time__(self) -> None:
        self.current_seconds += self.interval
        if self.current_seconds >= 60:
            self.current_minutes += self.current_seconds // 60
            self.current_seconds %= 60

    # Этот метод автоматически печатает двоеточие в таймлайне
    def __write_colon__(self) -> None:
        pyautogui.press(["shift", ":"])

    # Этот метод очищает таймлайн, нажимая на него трижды,
    # а затем нажимая клавишу `backspace`
    def __clear_timeline__(self) -> None:
        pyautogui.moveTo(x=self.timeline_x, y=self.timeline_y)
        pyautogui.click(clicks=3, interval=0.1)
        pyautogui.press("backspace")

    # Этот метод автоматически нажимает на кнопку добавления рекламной паузы
    def __add_pause__(self) -> None:
        pyautogui.moveTo(x=self.add_x, y=self.add_y)
        pyautogui.click()
    
    # Этот метод автоматически печатает момент данной рекламной паузы в таймлайн
    def __write_time__(self) -> None:
        pyautogui.write("0" + str(self.current_minutes) \
            if self.current_minutes < 10 else str(self.current_minutes))
        self.__write_colon__()
        pyautogui.write("0" + str(self.current_seconds) \
            if self.current_seconds < 10 else str(self.current_seconds))
        self.__write_colon__()
        pyautogui.write("00")
    
    # Этот метод вызывается, когда все координаты указаны.
    # Он запускает цикл `while`, который чистит таймлайн, записывает время,
    # добавляет новую рекламную паузу и инкрементирует время, пока его значение
    # не достигнет значения общей длительности видео
    def run(self) -> None:
        if not (self.add_x == 0 and self.add_y == 0 and self.timeline_x == 0 and self.timeline_y == 0):
            while self.__can_time_be_incremented__():
                self.__clear_timeline__()
                self.__write_time__()
                self.__add_pause__()
                self.__increment_time__()
            print("Процесс завершён!")

# И наконец, запуск самого этого скрипта просто не имеет смысла