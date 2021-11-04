# Цей файл мiстить функцiї для того, щоб знайти Tesseract-OCR на комп'ютерi,
# а якщо вiн не був знайдений, встановити його локально

from urllib.request import urlretrieve
from os import getcwd, mkdir, remove
from os.path import join, exists, isdir, dirname
from zipfile import ZipFile
from utils import find_files


# Посилання на архiв з бiнарниками Tesseract-OCR на випадок якщо його немає
# на комп'ютерi користувача та його потрiбно встановити локально
TESS_ARCHIVE_URL = "https://download1478.mediafire.com/pi2i3mh4v4rg/mni87p6m5f7c1qt/Tesseract-OCR.zip"


# Ця функцiя використовується для того, щоб знайти Tesseract-OCR на комп'ютерi
def try_find_tesseract() -> str:
    # Спочатку ми спробуємо знайти локальну папку .tess
    # Це корисно, якщо користувач не встановив Tesseract-OCR у систему,
    # але вiн вже запускав нашу програму, та бiнарники вже були локально встановленi
    local_tess = join(getcwd(), ".tess")
    if exists(local_tess):
        return local_tess
    # Якщо Tesseract-OCR не було знайдено локально, ми пробуємо знайти його в папках
    # Program Files на одному з локальних дискiв
    for letter in list("ABCDEFGHIJKLMNOPQRSTUVYXYZ"):
        for pf_folder in ["Program Files", "Program Files (x86)"]:
            arr = find_files("tesseract.exe", \
                             join(letter + ":\\", pf_folder))
            if len(arr) > 0:
                return dirname(arr[0])
    # Якщо ми так нiчого й не знайшли, повертаємо None
    return None


# Ця функцiя використовується при запуску процеса ОРС на скриншотi.
# Спочатку вона пробує знайти Tesseract-OCR на комп'ютерi, а якщо нiчого не було знайдено,
# бiнарники будуть встановленi у локальну папку .tess
def get_tesseract_cmd_path():
    # Спроба знайти Tesseract-OCR, якщо вiн вже встановлений або ранiше локально завантажений
    tess = try_find_tesseract()
    # Якщо вiн не був знайдений, починаємо завантаження архiва бiнарникiв з Iнтернета
    if tess is None:
        print("ПОПЕРЕДЖЕННЯ: Tesseract не було знайдено на вашому комп\'ютерi! Завантаження архiва бiнарникiв...")
        archive_path = join(getcwd(), "tess-binaries.zip")
        # Завантажуємо файл з URL
        urlretrieve(url=TESS_ARCHIVE_URL, filename=archive_path)
        print("DEBUG: Архiв був завантажений, розпакування...")
        # Створюємо локальну папку `.tess`
        binaries_path = join(getcwd(), ".tess")
        if exists(binaries_path) and not isdir(binaries_path):
            remove(binaries_path)
        if not exists(binaries_path):
            mkdir(binaries_path)
        # Розпаковуємо вмiст архiва бiнарникiв в папку `.tess`
        with ZipFile(archive_path) as archive:
            archive.extractall(binaries_path)
        print("DEBUG: Архiв був розпакований!")
        remove(archive_path)
        print("DEBUG: Архiв був видалений!")
        print("DEBUG: Шлях до вашого локально завантаженого Tesseract: " + binaries_path)
        # Повертаємо отриманий у результатi шлях до локально завантаженого Tesseract-OCR
        return binaries_path
    # Якщо Tesseract-OCR був знайдений, повертаємо шлях до нього
    else:
        print("DEBUG: Tesseract був успiшно знайдений на вашому комп\'ютерi в " + tess)
        return tess


# Цей скрипт можна запустити для налагодження.
# Вiн спробує знайти Tesseract-OCR на вашому комп'ютерi,
# та якщо не знайде, встановить його локально з Iнтернета
if __name__ == "__main__":
    get_tesseract_cmd_path()