# Це скрипт, в якому будуть вiдбуватися головнi процеси,
# такi як отримання скриншота й запуск системи ОРС

# Те що нам потрiбно iмпортувати:
# метод join з модуля os.path для того, щоб конкатенувати
# шляхи, щоб отримати повний шлях до певного файла або папки
from os.path import join
# модуль re для створення регулярних виразiв, з якими
# ми будемо пробувати зiставляти символи, знайденi ОРС,
# для того щоб обчислити положення таймлайна
import re
# функцiя mss з модуля mss для того, щоб робити скриншоти
from mss import mss
# метод asarray з бiблiотеки numpy для конвертацiї
# об'єкта ScreenShot з mss у масив пiкселiв\
from numpy import asarray
# модуль pytesseract для запуску Tesseract-OCR з Python
import pytesseract as tess
# Кiлька методiв з бiблiотеки opencv-python для того, щоб конвертувати скрiншот,
# представлений як numpy-масив пiкселiв, в об'єкт Image,
# для використання його в Tesseract-OCR
from cv2 import cvtColor, COLOR_BGR2GRAY
# Функцiя для отримання ширини та висоти монiтора у пiкселях iз скрипта utils.py
from utils import get_monitor_size
# Функцiя для отримання шляху до бiнарникiв Tesseract-OCR зi скрипта tesseract.py
from tesseract import get_tesseract_cmd_path

# Спочатку, отримаємо ширину й висоту монiтора в пiкселях
# для того, щоб вказати роздiльну здатнiсть скриншота
MONITOR_SIZE = get_monitor_size()

# Далi, нам потрiбно створити два регулярних вираза,
# якi допоможуть нам знайти таймлайн на скриншотi.
# Таймлайн має вид `nn:nn:nn`, де n - будь-яка цифра
# Отже, ми створюємо шаблон `nn:nn:nn`, а також `nnnnnn`, на випадок якщо
# Tesseract-OCR не зможе розпiзнати двокрапки на таймлайнi
TIMELINE_WITHOUT_COLONS = re.compile(r'^\d{6}')
TIMELINE_WITH_COLONS = re.compile(r'^\d{2}:\d{2}:\d{2}')


# Функцiя скриншота з використанням модуля mss
def take_screenshot():
    with mss() as screenshoter:
        # Iнiцiалiзуємо об'єкт ScreenShot
        screen = screenshoter.grab({
            'left': 0,
            'top': 0,
            'width': MONITOR_SIZE[0],
            'height': MONITOR_SIZE[1]
        })
        # Конвертуємо його в масив numpy
        img = asarray(screen)
        # Конвертуємо його ще раз в об'єкт Image OpenCV,
        # а також робимо його чорно-бiлим, щоб спростити
        # розпiзнавання символiв для Tesseract-OCR
        rgb = cvtColor(img, COLOR_BGR2GRAY)
        # Повертаємо кiнечний об'єкт зображення
        return rgb


# Функцiя для фiльтрацiї словника даних, якого повертає Tesseract-OCR
# пiсля завершення процесу ОРС
def filter_data_dict(dic: dict) -> None:
    # Видаляємо непотрiбнi ключi зi словника
    del dic['level']
    del dic['page_num']
    del dic['block_num']
    del dic['par_num']
    del dic['line_num']
    del dic['word_num']
    # Конвертуємо значення confidency
    # (впевненостi Tesseract-OCR в правильностi результата розпiзнавання)
    # iз рядкового числа з плаваючою комою в цiле число
    for i in range(len(dic['conf'])):
        if not isinstance(dic['conf'][i], int):
            dic['conf'][i] = int(float(dic['conf'][i]))
    # Видаляємо усi елементи зi значенням confidency -1
    done: bool = False
    while not done:
        try:
            index = dic['conf'].index(-1)
            for key in ('left', 'top', 'width', 'height', 'conf', 'text'):
                dic[key].pop(index)
        except ValueError:
            done = True


# Функцiя, яка робить структуру словника даних бiльш легкою для читання.
# Перед викликом цiєї функцiї словник даних виглядає так:
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
# А результат функцiї structurize виглядає вже так:
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


# Функцiя, яка запускає процес Tesseract-OCR й повертає
# список знайдених наборiв символiв з вiдповiдними їм координатами на екранi
def find_text(rgb, tess_path=get_tesseract_cmd_path()) -> list:
    # Якщо Tesseract-OCR не був знайдений, повертаємо None.
    # В нормальних умовах такого випадку не повинно бути, для бiльш
    # детальної iнформацiї про це, дивiться скрипт tesseract.py
    if tess_path is None:
        print("Tesseract не було знайдено на вашому комп\'ютерi :-(")
        return None
    else:
        # Встановлюємо шлях до директорiї з тренованими даними ОРС,
        # та шлях до виконуваного файлу Tesseract
        tess.pytesseract.environ.setdefault(
            "TESSDATA_PREFIX",
            join(tess_path, "tessdata")
        )
        tess.pytesseract.tesseract_cmd = join(tess_path, "tesseract.exe")
        # Отримання словника даних з Tesseract-OCR
        data: dict = tess.image_to_data(
            # Вказуємо об'єкт Image скриншота,
            # встановлюємо тип вихiдних даних - словник,
            # та росiйську мову
            rgb, output_type=tess.pytesseract.Output.DICT,
            config=r'-l rus'
        )
        # Фiльтруємо та структуруємо словник даних
        filter_data_dict(data)
        result = structurize(data)
        # Для пiдвищення продуктивностi на наступних етапах,
        # ми видаляємо всi набори символiв довжиною менше 4
        result = list(filter(lambda el: len(el[5]) > 4, result))
        # Повертаємо вiдфiльтрований список даних
        return result


# Класс винятку, який будемо викликати, коли не всi
# координати для роботи бота були знайденi.
# Це просто пустий клас, успадкований вiд базового класа винятку Python
class NotEverythingFoundError(Exception):
    def __init__():
        super.__init__()


# Функцiя, яка повертає кортеж з чотирьох елементiв,
# якi є координатами кнопки додавання рекламної паузи i таймлайна по осям X та Y
def get_coords_for_bot(data: list) -> tuple:
    # Створюємо змiннi для координат,
    # встановлюємо їм неможливi значення
    tx = ax = MONITOR_SIZE[0] + 1
    ty = ay = MONITOR_SIZE[1] + 1
    for item in data:
        # Кнопка додавання паузи виглядає як `+ РЕКЛАМНАЯ ПАУЗА`.
        # Шукаємо слово `РЕКЛАМНАЯ` та встановлюємо координати ax та ay
        if item[5] == "РЕКЛАМНАЯ":
            ax = item[0] + item[2]
            ay = item[1] + item[3] // 2
        # Далi нам потрiбно знайти таймлайн. Одразу кiлька наборiв символiв
        # можуть вiдповiдати нашим регулярним виразам, проте таймлайн
        # завжди знаходиться лiвiше за все iнше.
        # Робимо вiдповiдну перевiрку
        if TIMELINE_WITH_COLONS.match(item[5]) or \
                TIMELINE_WITHOUT_COLONS.match(item[5]):
            if tx > item[0]:
                tx = item[0] + item[2] // 2
                ty = item[1] + item[3] // 2
    # Пiсля сканування списку, ми перевiряємо всi координати,
    # i якщо як мiнiмум одна з них зберегла неможливе значення,
    # викликаємо наш кастомний виняток
    if tx == MONITOR_SIZE[0] + 1 or \
        ax == MONITOR_SIZE[0] + 1 or \
        ty == MONITOR_SIZE[1] + 1 or \
        ay == MONITOR_SIZE[1] + 1:
            raise NotEverythingFoundError()
    # Якшо не з'явилось виняткiв, ми нарештi повертаємо
    # кортеж з координатами по X та Y таймлайна,
    # а потiм координати по X та Y кнопки додавання рекламної паузи
    return (tx, ty, ax, ay)


# Цей скрипт можна запустити для налагодження.
# Вiн створить трисекундну затримку, пiсля чого
# буде зроблено скриншот, i результат процесу ОРС
# буде надруковано в консоль
if __name__ == "__main__":
    from time import sleep
    sleep(3)
    [print(item) for item in find_text(take_screenshot())]