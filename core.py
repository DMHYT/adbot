# Это скрипт, в котором будут происходить главные процессы,
# такие как получение скриншота и запуск системы ОРС

# То что нам нужно импортировать:
# метод join из модуля os.path для того, чтобы конкатенировать
# пути, чтобы получить полный путь к определённому файлу или папке
from os.path import join
# модуль re для создания регулярных выражений, с которыми
# мы будем пробовать сопоставлять символы, найденные ОРС,
# для того чтобы вычислить расположение таймлайна
import re
# функция mss из модуля mss для того, чтобы делать скриншот
from mss import mss
# метод asarray из библиотеки numpy для конвертации
# объекта ScreenShot из mss в массив пикселей
from numpy import asarray
# модуль pytesseract для запуска Tesseract-OCR из Python
import pytesseract as tess
# Несколько методов из библиотеки opencv-python для того, чтобы конвертировать скриншот,
# представленный как numpy-массив пикселей, в объект Image,
# для использования его в Tesseract-OCR
from cv2 import cvtColor, COLOR_BGR2GRAY
# Функция для получения ширину и высоту монитора в пикселях из скрипта utils.py
from utils import get_monitor_size
# Функция для получения пути к бинарникам Tesseract-OCR из скрипта tesseract.py
from tesseract import get_tesseract_cmd_path

# Для начала, получаем ширину и высоту монитора в пикселях
# для того, чтобы указать разрешение скриншота
MONITOR_SIZE = get_monitor_size()

# Далее, нам понадобится создать два регулярных выражения,
# которые помогут нам найти таймлайн на скриншоте.
# Таймлайн имеет вид `nn:nn:nn`, где n - любая цифра
# Итак, мы создаём шаблон `nn:nn:nn`, а также `nnnnnn`, в случае если
# Tesseract-OCR не сможет распознать двоеточия на таймлайне
TIMELINE_WITHOUT_COLONS = re.compile(r'^\d{6}')
TIMELINE_WITH_COLONS = re.compile(r'^\d{2}:\d{2}:\d{2}')


# Функция скриншота с использованием модуля mss
def take_screenshot():
    with mss() as screenshoter:
        # Инициализируем объект ScreenShot
        screen = screenshoter.grab({
            'left': 0,
            'top': 0,
            'width': MONITOR_SIZE[0],
            'height': MONITOR_SIZE[1]
        })
        # Конвертируем его в массив numpy
        img = asarray(screen)
        # Конвертируем его ещё раз в объект Image OpenCV,
        # а также делаем его чёрно-белым, чтобы упростить
        # распознавание символов для Tesseract-OCR
        rgb = cvtColor(img, COLOR_BGR2GRAY)
        # Возвращаем конечный объект изображения
        return rgb


# Функция для фильтрации словаря данных, возвращаемого Tesseract-OCR
# после завершения процесса ОРС
def filter_data_dict(dic: dict) -> None:
    # Удаляем ненужные ключи со словаря
    del dic['level']
    del dic['page_num']
    del dic['block_num']
    del dic['par_num']
    del dic['line_num']
    del dic['word_num']
    # Конвертируем значения confidency 
    # (уверенности Tesseract-OCR в правильности результата распознавания)
    # из строкового числа с плавающей точкой в целое число
    for i in range(len(dic['conf'])):
        if not isinstance(dic['conf'][i], int):
            dic['conf'][i] = int(float(dic['conf'][i]))
    # Удаляем все элементы со значением confidency -1
    done: bool = False
    while not done:
        try:
            index = dic['conf'].index(-1)
            for key in ('left', 'top', 'width', 'height', 'conf', 'text'):
                dic[key].pop(index)
        except ValueError:
            done = True


# Функция, которая делает структуру словаря данных более читабельной.
# Перед вызовом этой функции словарь данных выглядит так:
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
# А результат функции structurize выглядит уже так:
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


# Функция, которая запускает процесс Tesseract-OCR и возвращает
# список найденных наборов символов с соответствующими им координатами на экране
def find_text(rgb, tess_path=get_tesseract_cmd_path()) -> list:
    # Если Tesseract-OCR не был найден, возвращаем None.
    # В нормальных условиях такого случая быть не должно, для более
    # подробной информации об этом, смотрите скрипт tesseract.py
    if tess_path is None:
        print("Tesseract не был найден на вашем компьютере :-(")
        return None
    else:
        # Устанавливаем путь к директории с тренированными данными ОРС,
        # и путь к исполняемому файлу Tesseract
        tess.pytesseract.environ.setdefault(
            "TESSDATA_PREFIX",
            join(tess_path, "tessdata")
        )
        tess.pytesseract.tesseract_cmd = join(tess_path, "tesseract.exe")
        # Получение словаря данных из Tesseract-OCR
        data: dict = tess.image_to_data(
            # Указываем объект Image скриншота,
            # устанавливаем тип выходных данных - словарь,
            # и русский язык
            rgb, output_type=tess.pytesseract.Output.DICT,
            config=r'-l rus'
        )
        # Фильтруем и структурируем словарь данных
        filter_data_dict(data)
        result = structurize(data)
        # Для увеличения производительности на следующих этапах,
        # мы удаляем все наборы символов длиной меньше 4
        result = list(filter(lambda el: len(el[5]) > 4, result))
        # Возвращаем отфильтрованный список данных
        return result


# Класс исключения, которое будем вызывать, когда не все
# координаты для работы бота были найдены.
# Это просто пустой класс, наследованный от базового класса исключения Python
class NotEverythingFoundError(Exception):
    def __init__():
        super.__init__()


# Функция, возвращающая кортеж из четырёх элементов,
# которые являются координатами кнопки добавления рекламной паузы и таймлайна по оси X и Y
def get_coords_for_bot(data: list) -> tuple:
    # Создаём переменные для координат,
    # устанавливаем им невозможные значения
    tx = ax = MONITOR_SIZE[0] + 1
    ty = ay = MONITOR_SIZE[1] + 1
    for item in data:
        # Кнопка добавления паузы выглядит как `+ РЕКЛАМНАЯ ПАУЗА`.
        # Ищём слово `РЕКЛАМНАЯ` и устанавливаем координаты ax и ay
        if item[5] == "РЕКЛАМНАЯ":
            ax = item[0] + item[2]
            ay = item[1] + item[3] // 2
        # Далее нам нужно найти таймлайн. Сразу несколько наборов символов
        # могут соответствовать нашим регулярным выражениям, но таймлайн
        # всегда находится левее всех.
        # Делаем соответствующую проверку
        if TIMELINE_WITH_COLONS.match(item[5]) or \
                TIMELINE_WITHOUT_COLONS.match(item[5]):
            if tx > item[0]:
                tx = item[0] + item[2] // 2
                ty = item[1] + item[3] // 2
    # После сканирования списка, мы проверяем все координаты,
    # и если как минимум одна из них сохранила невозможное значение,
    # вызываем наше кастомное исключение
    if tx == MONITOR_SIZE[0] + 1 or \
        ax == MONITOR_SIZE[0] + 1 or \
        ty == MONITOR_SIZE[1] + 1 or \
        ay == MONITOR_SIZE[1] + 1:
            raise NotEverythingFoundError()
    # Если не появилось исключений, мы наконец-то возвращаем
    # кортеж с координатами по X и Y таймлайна,
    # а затем координатами по X и Y кнопки добавления рекламной паузы
    return (tx, ty, ax, ay)


# Этот скрипт можно запустить для отладки.
# Он создаст трёхсекундную задержку, после чего
# будет сделан скриншот, и результат процесса ОРС
# будет напечатан в консоль
if __name__ == "__main__":
    from time import sleep
    sleep(3)
    [print(item) for item in find_text(take_screenshot())]