import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumrequests import Chrome
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import json
import requests
import os
import re


def get_html_code(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }

    r = requests.get(url, timeout=30, headers=headers, )
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def create_directory(str):
    os.makedirs(str)


def download_chapter(url, chapter_dir):
    soup = get_html_code(url)
    all_image_in_chapter = soup.find(
        class_='src-pages-ChapterView-___styles-module__pages').find_all('img')
    image_list = []
    for image in all_image_in_chapter:
        if 'src' in image.attrs:
            src = image['src']
            image_list.append(src)

    counter = 0

    for image in image_list:
        filepath = str(counter) + ".jpg"

        r = requests.get(image)
        r.raise_for_status()

        with open(chapter_dir + '/' + filepath, "wb") as file:
            file.write(r.content)

        counter += 1


def pars_manga_for_chapters(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    # options.headless = True
    browser = webdriver.Chrome(options=options)
    browser.find_element
    directory_manga_name = url.split('/')[-1]
    create_directory(directory_manga_name)

    browser.get(url)

    chapters = browser.find_elements(
        By.CLASS_NAME, 'src-pages-TitleView-components-ChapterItem-___styles-module__chapter')

    for chapter in chapters:
        chapterUrl = chapter.get_attribute('href')
        directory_chapter_name = directory_manga_name + '/' + \
            chapterUrl.split('/')[-2] + '-' + chapterUrl.split('/')[-1]
        directory_for_image_from_chapter = directory_manga_name + '/' + directory_chapter_name
        create_directory(directory_for_image_from_chapter)
        download_chapter(chapterUrl, directory_for_image_from_chapter)


def pars_catalog_for_manga(url):

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    browser = webdriver.Chrome(options=options)
    browser.find_element

    browser.get(url)

    manga = browser.find_elements(
        By.CLASS_NAME, 'src-components-TitleListElement-___styles-module__imageWrapper')

    for manga_element in manga:
        mangaUrl = manga_element.get_attribute('href')
        pars_manga_for_chapters(mangaUrl)

# инфу надо парсить в папку отдельную. преполагаю, что назвать её надо information_about_manga
# че то типо такого
# после парсинга инфы вызывать парсинг глав. главы скачаются уже дальше по цепочке.
# парсинг инфы надо вызывать в парсинге манги. до парсинга глав.


def pars_information_about_manga(url):
    print("TODO")


def main():
    url = "https://trendymanga.com/top/day"
    pars_catalog_for_manga(url)


main()
