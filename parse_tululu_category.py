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


BOOK_FOLDER = "books/"
IMAGE_FOLDER = "images/"
JSON_FOLDER = ""
CLEAN_TERMINAL_CODE = "\033[H"
CATEGORY_PAGE = "https://tululu.org/l55/"


def main():

    parser = argparse.ArgumentParser(
        description="Этот скрипт скачивает книги с библиотеки tululu.ru."
    )
    parser.add_argument('start_page', nargs='?', default=1, help="Страница с которого начать.", type=int)
    parser.add_argument('end_page', nargs='?', default=1, help="Страница которой закончить.", type=int)
    args = parser.parse_args()

    downloaded = 0
    books_metadata = []
    book_ids = get_book_ids(CATEGORY_PAGE, args.start_page, args.end_page)

    for book_id in tqdm(book_ids):
        try:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран

            book_url = f"https://tululu.org/b{book_id}/"
            download_url = "https://tululu.org/txt.php"
            head_response = get_response(book_url, book_id)
            download_response = get_response(download_url, book_id)

            book_context = parse_book_context(head_response)
            book_filename = f"{book_id}. {book_context['title']}.txt"
            book_save_path = download_txt(download_response, book_filename, BOOK_FOLDER)

            image_filename = Path(book_context['image_link']).name
            full_img_link = urljoin(book_url, book_context['image_link'])
            img_src = download_image(full_img_link, image_filename, IMAGE_FOLDER)

            books_metadata.append({
                "title": book_context['title'],
                "author": book_context['author'],
                "img_src": img_src,
                "book_path": book_save_path,
                "comments": book_context['comments'],
                "genres": book_context['genres'],
            })

            downloaded += 1
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print(f'Книга "{book_context["title"]}" сохранена в: "{book_save_path}".')

        except ConnectionError:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print("Проблема с интернет соединением! Повторная попытка...")
            sleep(5)
            continue

        except HTTPError:
            print(CLEAN_TERMINAL_CODE)  # Чистим экран
            print(f'Книги с id: "{book_id}" не существует.')
            continue

    books_metadata_json = json.dumps(books_metadata, ensure_ascii=False, indent=4)
    with open(urljoin(JSON_FOLDER, 'books.json'), 'w') as file:
        file.write(books_metadata_json)

    print(f"\nВСЕГО ЗАГРУЖЕНО: {downloaded} КНИГ.")


def parse_book_context(response):

    page_text = BeautifulSoup(response.text, 'lxml')
    title_and_author = page_text.find('td', class_='ow_px_td').find('h1').text.split('::')
    title_and_author = list(map(lambda x: x.strip(), title_and_author))
    dirt_genres = page_text.find("span", class_="d_book").find_all("a")
    divs = page_text.find_all("div", class_="texts")

    comments = [div.find("span", class_="black").text for div in divs]

    context = {'title': title_and_author[0],
               'author': title_and_author[1],
               'image_link': page_text.find("div", class_="bookimage").find("img")["src"],
               'genres': list(map(lambda x: x.text, dirt_genres)),
               'comments': comments,
               }
    return context


def download_txt(response, filename, folder='books/'):

    os.makedirs(BOOK_FOLDER, exist_ok=True)
    cleaned_filename = sanitize_filename(filename)
    book_save_path = os.path.join(folder, cleaned_filename)
    with open(book_save_path, 'wb') as book:
        book.write(response.content)
    return book_save_path


def download_image(img_url, img_filename, folder='images/'):

    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    image_save_path = os.path.join(folder, img_filename)
    with open(image_save_path, "wb") as image:
        image.write(response.content)
    return image_save_path


def get_response(url, id):
    params = {"id": id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    if response.history:
        raise HTTPError()
    return response


def get_book_ids(base_url, start_page, end_page):
    book_ids = []
    for page in range(start_page, end_page+1):
        page_url = urljoin(base_url, str(page))
        response = requests.get(page_url)
        response.raise_for_status()
        book_ids += get_page_ids(response)
    return book_ids


def get_page_ids(response):
    page_text = BeautifulSoup(response.text, 'lxml')
    book_ids = page_text.find("div", id="content").find_all("table", class_="d_book")
    return [book_id.a['href'].lstrip("/b").rstrip("/") for book_id in book_ids]


if __name__ == "__main__":
    main()
