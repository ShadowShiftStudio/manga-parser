import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
import argparse
import json
import requests
import os
from tqdm import tqdm

manga_n = ""


def get_html_code(url):
    """
    Возвращает HTML-код указанного URL-адреса в виде объекта BeautifulSoup.

    Аргументы:
    url (str): URL-адрес страницы, для которой необходимо получить HTML-код.

    Возвращает:
    soup (BeautifulSoup): Объект BeautifulSoup, содержащий HTML-код страницы.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }

    r = requests.get(url, timeout=30, headers=headers, )
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def create_directory(str):
    os.makedirs(str)


def download_chapter(url, chapter_dir):
    """
    Загружает главу манги с указанного URL-адреса и сохраняет изображения главы в указанную директорию.

    Аргументы:
    url (str): URL-адрес страницы с главой манги.
    chapter_dir (str): Путь к директории для сохранения изображений главы.

    Возвращает:
    None
    """

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


def get_title_preview_page(url, path):
    """
    Получает превью тайтла манги с указанного URL-адреса и сохраняет его в указанную директорию.

    Аргументы:
    url (str): URL-адрес страницы с мангой.
    path (str): Путь к директории для сохранения превью.

    Возвращает:
    None
    """

    soup = get_html_code(url)
    previews = soup.find(
        class_='src-pages-TitleView-___styles-module__sidebar').find_all('img')

    preview_url = []

    for preview in previews:
        if 'src' in preview.attrs:
            src = preview['src']
            preview_url.append(src)

    r = requests.get(preview_url[0])
    r.raise_for_status()

    os.makedirs(path + '/' + "Preview")

    with open(path + '/' + "Preview" + '/' + "preview.jpg", "wb") as file:
        file.write(r.content)

    print("Preview " + path + " done")


def pars_manga_for_chapters(url, isInf):
    """
    Парсит мангу по главам с указанного URL-адреса и вызывает методы для получения информации о манге,
    получения превью тайтла и загрузки глав.

    Аргументы:
    url (str): URL-адрес страницы с мангой.
    isInf (bool, по умолчанию False): Флаг, указывающий, нужно ли также получить информацию о манге.

    Возвращает:
    None
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    browser = webdriver.Chrome(options=options)
    browser.find_element
    directory_manga_name = url.split('/')[-1]
    create_directory(directory_manga_name)
    create_directory(directory_manga_name + '/' + "Chapters")
    browser.get(url)

    pars_information_about_manga(url, directory_manga_name)

    if (isInf == False):
        get_title_preview_page(url, directory_manga_name)

        chapters = browser.find_elements(
            By.CLASS_NAME, 'src-pages-TitleView-components-ChapterItem-___styles-module__chapter')
        chapter_count = len(chapters)

        for index, chapter in enumerate(tqdm(chapters, desc=directory_manga_name, leave=True)):
            chapterUrl = chapter.get_attribute('href')
            directory_chapter_name = chapterUrl.split(
                '/')[-2] + '-' + chapterUrl.split('/')[-1]
            directory_for_image_from_chapter = directory_manga_name + \
                '/' + 'Chapters' + '/' + directory_chapter_name
            create_directory(directory_for_image_from_chapter)
            download_chapter(chapterUrl, directory_for_image_from_chapter)
            tqdm.write(f"Chapter {index+1}/{chapter_count} downloaded")

    browser.quit()


def pars_catalog_for_manga(url):
    """
    Парсит каталог манги с указанного URL-адреса и вызывает метод для парсинга манги по главам.

    Аргументы:
    url (str): URL-адрес страницы с каталогом манги.

    Возвращает:
    None
    """

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
        pars_manga_for_chapters(mangaUrl, False)

    browser.quit()


def pars_information_about_manga(url, path):
    """
    Парсит информацию о манге с указанного URL-адреса и сохраняет в JSON-файл.

    Аргументы:
    url (str): URL-адрес страницы с информацией о манге.\n
    path (str): Путь к директории, в которую будет сохранен JSON-файл.

    Возвращает:
    None
    """

    soup = get_html_code(url)

    manga_name = soup.find(
        class_='src-pages-TitleView-___styles-module__title').text
    manga_status = soup.find(
        class_='src-pages-TitleView-___styles-module__header').find_all('div')[-1].text[1:-1]
    manga_rating = random.randint(10, 100) / 10
    manga_likes = random.randint(100, 10000)
    manga_views = random.randint(100, 2500000)
    manga_bookmarks = random.randint(100, 10000)
    manga_year = random.randint(2001, 2023)
    manga_type = soup.find(
        class_='src-pages-TitleView-___styles-module__stats').find_all('span')[-1].text
    manga_ganres_html = soup.find_all(
        class_='src-pages-TitleView-___styles-module__tagsAndGenres')
    manga_ganres_a = []
    manga_ganres = []
    for mangaGanHtml in manga_ganres_html:
        manga_ganres_a = mangaGanHtml.find_all('a')
        for mangaGanA in manga_ganres_a:
            manga_ganres.append(mangaGanA.text)
    manga_description = soup.find(
        class_='src-pages-TitleView-___styles-module__description').find('span').text

    data = {
        "manga_name": manga_name,
        "manga_status": manga_status,
        "manga_rating": manga_rating,
        "manga_likes": manga_likes,
        "manga_views": manga_views,
        "manga_bookmarks": manga_bookmarks,
        "manga_year": manga_year,
        "manga_type": manga_type,
        "manga_ganres": manga_ganres,
        "manga_description": manga_description
    }

    os.makedirs(path + '/' + "Information")

    with open(path + '/' + "Information" + '/' + "info.json", 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    print("Information about " + path + " done")


parser = argparse.ArgumentParser(
    description="Программа создана для парсинга сайта trendymanga.com.")
parser.add_argument('--url', type=str,
                    help='URL для обработки. Значение обязательно. Если иные флаги не указывать, то код воспримет ссылку, как ссылку на каталог.', action='store')
parser.add_argument(
    '--catalog', help="Будет ли парситься каталог. В таком случае обязательна ссылка на каталог.", action='store_true')
parser.add_argument(
    '--manga', help='Будет ли парситься только один тайтл. В таком случае обязательна ссылка на определенную мангу.', action='store_true')
parser.add_argument('--information',
                    help='Будет ли парситься только информация о манге. В таком случае обязательна ссылка на определенную мангу', action='store_true')

args = parser.parse_args()

if args.catalog:
    pars_catalog_for_manga(args.url)
elif args.manga:
    pars_manga_for_chapters(args.url, False)
elif args.information:
    pars_manga_for_chapters(args.url, True)
else:
    pars_catalog_for_manga(args.url)
