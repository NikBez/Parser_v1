import sys

from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from tqdm import tqdm
import requests
from requests.exceptions import HTTPError, ConnectionError

import argparse
import os
from time import sleep
import json


BOOK_FOLDER = 'books/'
IMAGE_FOLDER = 'images/'
JSON_FOLDER = Path.cwd()
CATEGORY_URL = 'https://tululu.org/l55/'
BASE_PATH = Path.cwd()

CLEAN_TERMINAL_CODE = '\033[H'


def main():

    parser = argparse.ArgumentParser(
        description='Этот скрипт скачивает книги с библиотеки tululu.ru.'
    )
    parser.add_argument('start_page', nargs='?', default=0, help='Страница с которого начать.', type=int)
    parser.add_argument('end_page', nargs='?', default=1, help='Страница которой закончить.', type=int)
    parser.add_argument('-d', '--dest_path', nargs='?', default=BASE_PATH, help='Корневой путь к папкам')
    parser.add_argument('-j', '--json_path', nargs='?', default=JSON_FOLDER, help='Путь, по которому сохранять файл c данными')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать изображения')
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать книги')
    args = parser.parse_args()

    downloaded = 0
    books = []

    book_ids = []
    for page in range(args.start_page, args.end_page + 1):
        try:
            page_ids = get_page_ids(CATEGORY_URL, str(page))
            book_ids += page_ids
        except HTTPError:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print(f'Страница {page} не существует.')

    for book_id in tqdm(book_ids):
        try:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            book_url = f'https://tululu.org/b{book_id}/'
            download_url = 'https://tululu.org/txt.php'
            head_response = get_response(book_url, book_id)
            download_response = get_response(download_url, book_id)

            book_context = parse_book_context(head_response)
            book_filename = f"{book_id}. {book_context['title']}.txt"
            if args.skip_txt:
                book_save_path = ""
            else:
                book_save_path = download_txt(download_response, book_filename, Path(args.dest_path, BOOK_FOLDER))
            image_filename = Path(book_context['image_link']).name
            full_img_link = urljoin(book_url, book_context['image_link'])
            if args.skip_imgs:
                img_src = ""
            else:
                img_src = download_image(full_img_link, image_filename, Path(args.dest_path, IMAGE_FOLDER))

            books.append({
                'title': book_context['title'],
                'author': book_context['author'],
                'img_src': str(img_src),
                'book_path': str(book_save_path),
                'comments': book_context['comments'],
                'genres': book_context['genres'],
            })

            downloaded += 1
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print(f'Книга "{book_context["title"]}" сохранена в: "{book_save_path}".')

        except ConnectionError:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print('Проблема с интернет соединением! Повторная попытка...')
            sleep(5)
            continue

        except HTTPError:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print(f'Книги с id: "{book_id}" не существует.')
            continue

    if args.json_path == args.dest_path:
        json_file_path = Path(args.dest_path) / 'books.json'
    else:
        json_file_path = Path(args.json_path)/'books.json'

    with open(json_file_path, 'w') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)
    print(f'\nВСЕГО ЗАГРУЖЕНО: {downloaded} КНИГ.')


def parse_book_context(response):

    page_text = BeautifulSoup(response.text, 'lxml')

    title_and_author_selector = '.ow_px_td h1'
    dirt_genres_selector = 'span.d_book a'
    divs_selector = 'div.texts'
    comments_selector = 'span.black'

    title_and_author = page_text.select_one(title_and_author_selector).text.split('::')
    title_and_author = list(map(lambda x: x.strip(), title_and_author))
    dirt_genres = page_text.select(dirt_genres_selector)

    divs = page_text.select(divs_selector)
    comments = [div.select_one(comments_selector).text for div in divs]

    context = {
        'title': title_and_author[0],
        'author': title_and_author[1],
        'image_link': page_text.find('div', class_='bookimage').find('img')['src'],
        'genres': list(map(lambda x: x.text, dirt_genres)),
        'comments': comments,
        }
    return context


def download_txt(response, filename, folder):

    os.makedirs(folder, exist_ok=True)
    cleaned_filename = sanitize_filename(filename)
    book_save_path = Path(folder)/cleaned_filename
    with open(book_save_path, 'wb') as book:
        book.write(response.content)
    return book_save_path


def download_image(img_url, img_filename, folder):

    os.makedirs(folder, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    image_save_path = Path(folder)/img_filename
    with open(image_save_path, 'wb') as image:
        image.write(response.content)
    return image_save_path


def get_response(url, id):
    params = {'id': id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    if response.history:
        raise HTTPError()
    return response


def get_page_ids(url, page_number):

    page_url = urljoin(url, page_number)
    while True:
        try:
            response = requests.get(page_url, allow_redirects=False)
            response.raise_for_status()
            break
        except ConnectionError:
            print('Проблема с интернет соединением! Повторная попытка...')
            sleep(5)
            continue
    if not response.is_redirect:
        return parse_book_ids(response)
    raise HTTPError()


def parse_book_ids(response):
    book_ids_selector = 'div#content table.d_book'
    page_text = BeautifulSoup(response.text, 'lxml')
    book_ids = page_text.select(book_ids_selector)
    return [book_id.a['href'].lstrip('/b').rstrip('/') for book_id in book_ids]


if __name__ == '__main__':
    main()
