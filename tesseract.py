# This file contains functions to find Tesseract-OCR on the machine,
# and if it is not found, download it locally

from urllib.request import urlopen, urlretrieve
from os import getcwd, mkdir, remove
from os.path import join, exists, isdir, dirname
from zipfile import ZipFile
from bs4 import BeautifulSoup
from utils import find_files


# Method to get the direct link to download Tesseract-OCR binaries archive
# Here we will use BeautifulSoup module for HTML parsing
# in order to find download button on the web-page and get its link
def get_archive_url() -> str:
    print("DEBUG: Getting direct link to Tesseract-OCR binaries archive...")
    response = urlopen("https://www.mediafire.com/file/mni87p6m5f7c1qt/Tesseract-OCR.zip/file")
    content = response.read().decode('utf-8')
    soup = BeautifulSoup(content, features="html.parser")
    button = soup.find_all("a", { "class": "input popsok" })
    link = button[0]['href']
    print("DEBUG: The link is " + link)
    print("DEBUG: Downloading...")
    return link


# This function is used to find Tesseract-OCR on the machine
def try_find_tesseract() -> str:
    # Firstly we try to find it in the local .tess folder.
    # It is useful when the user didn't install Tesseract-OCR into the system,
    # but they have already run our program and binaries had been locally downloaded
    local_tess = join(getcwd(), ".tess")
    if exists(local_tess):
        return local_tess
    # If it wasn't found locally, we try to find it in Program Files folders
    # at one of the local drives
    for letter in list("ABCDEFGHIJKLMNOPQRSTUVYXYZ"):
        for pf_folder in ["Program Files", "Program Files (x86)"]:
            arr = find_files("tesseract.exe", \
                             join(letter + ":\\", pf_folder))
            if len(arr) > 0:
                return dirname(arr[0])
    # If we still haven't found anything, we return None
    return None


# This function is used when running the OCR process on the screenshot.
# Firstly it tries to find Tesseract-OCR on the machine, and if nothing found,
# the binaries would be installed in .tess local folder
def get_tesseract_cmd_path():
    # Trying to find Tesseract-OCR already installed or previously locally downloaded
    tess = try_find_tesseract()
    # If it wasn't found, starting downloading the binaries archive from the Internet
    if tess is None:
        print("WARNING: Tesseract was not found on your machine! Downloading binaries archive...")
        archive_path = join(getcwd(), "tess-binaries.zip")
        # Downloading file from the URL
        urlretrieve(url=get_archive_url(), filename=archive_path)
        print("DEBUG: Archive has been downloaded, extracting...")
        # Creating local folder `.tess`
        binaries_path = join(getcwd(), ".tess")
        if exists(binaries_path) and not isdir(binaries_path):
            remove(binaries_path)
        if not exists(binaries_path):
            mkdir(binaries_path)
        # Extracting contents of the binaries archive to the .tess folder
        with ZipFile(archive_path) as archive:
            archive.extractall(binaries_path)
        print("DEBUG: Archive has been extracted!")
        remove(archive_path)
        print("DEBUG: Archive has been removed!")
        print("DEBUG: Your Tesseract local path: " + binaries_path)
        # Returning resulting Tesseract-OCR local path
        return binaries_path
    # If it was found, we return it
    else:
        print("DEBUG: Tesseract was successfully found on your machine at " + tess)
        return tess


# This script can be run for debug.
# It will look for Tesseract-OCR on your machine,
# and if not found, download it locally from the Internet
if __name__ == "__main__":
    # get_tesseract_cmd_path()
    print(get_archive_url())