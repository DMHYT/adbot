# Этот файл содержит функции для того, чтобы найти Tesseract-OCR на компьютере,
# а если он не был найден, установить его локально

from urllib.request import urlretrieve
from os import getcwd, mkdir, remove
from os.path import join, exists, isdir, dirname
from zipfile import ZipFile
from utils import find_files


# Ссылка на архив с бинарниками Tesseract-OCR в случае если его нет
# на компьютере пользователя и его нужно установить локально
TESS_ARCHIVE_URL = "https://download1478.mediafire.com/pi2i3mh4v4rg/mni87p6m5f7c1qt/Tesseract-OCR.zip"


# Эта функция используется для того, чтобы найти Tesseract-OCR на компьютере
def try_find_tesseract() -> str:
    # Для начала мы попробуем найти локальную папку .tess
    # Это полезно, если пользователь не установил Tesseract-OCR в систему,
    # но он уже запускал нашу программу, и бинарники уже были локально установлены
    local_tess = join(getcwd(), ".tess")
    if exists(local_tess):
        return local_tess
    # Если Tesseract-OCR не был найден локально, мы пробуем найти его в папках
    # Program Files на одном из локальных дисков
    for letter in list("ABCDEFGHIJKLMNOPQRSTUVYXYZ"):
        for pf_folder in ["Program Files", "Program Files (x86)"]:
            arr = find_files("tesseract.exe", \
                             join(letter + ":\\", pf_folder))
            if len(arr) > 0:
                return dirname(arr[0])
    # Если мы так ничего и не нашли, возвращаем None
    return None


# Эта функция используется при запуске процесса ОРС на скриншоте.
# Сначала она пробует найти Tesseract-OCR на компьютере, а если ничего не было найдено,
# бинарники будут установлены в локальную папку .tess
def get_tesseract_cmd_path():
    # Попытка найти Tesseract-OCR, если он уже установлен или ранее локально скачан
    tess = try_find_tesseract()
    # Если он не был найден, начинаем установку архива бинарников с Интернета
    if tess is None:
        print("ПРЕДУПРЕЖДЕНИЕ: Tesseract не был найден на вашем компьютере! Установка архива бинарников...")
        archive_path = join(getcwd(), "tess-binaries.zip")
        # Скачиваем файл с URL
        urlretrieve(url=TESS_ARCHIVE_URL, filename=archive_path)
        print("ОТЛАДКА: Архив был скачан, извлечение...")
        # Создаём локальную папку `.tess`
        binaries_path = join(getcwd(), ".tess")
        if exists(binaries_path) and not isdir(binaries_path):
            remove(binaries_path)
        if not exists(binaries_path):
            mkdir(binaries_path)
        # Извлекаем содержимое архива бинарников в папку `.tess`
        with ZipFile(archive_path) as archive:
            archive.extractall(binaries_path)
        print("ОТЛАДКА: Архив был извлечён!")
        remove(archive_path)
        print("ОТЛАДКА: Архив был удалён!")
        print("ОТЛАДКА: Путь к вашему локально установленному Tesseract: " + binaries_path)
        # Возвращаем полученный в результате путь к локально установленному Tesseract-OCR
        return binaries_path
    # Если Tesseract-OCR был найден, возвращаем путь к нему
    else:
        print("ОТЛАДКА: Tesseract был успешно найден на вашем компьютере в " + tess)
        return tess


# Этот скрипт можно запустить для отладки.
# Он попробует найти Tesseract-OCR на вашем компьютере,
# и если не найдёт, установит его локально с Интернета
if __name__ == "__main__":
    get_tesseract_cmd_path()