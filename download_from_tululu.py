import argparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from tqdm import tqdm
from time import sleep


BOOK_FOLDER = "books/"
IMAGE_FOLDER = "images/"
COMMENTS_FOLDER = "comments/"
GENRE = "Научная фантастика"


def main():

    parser = argparse.ArgumentParser(
        description="Этот скрипт скачивает книги с библиотеки tululu.ru."
    )
    parser.add_argument('start_id', nargs='?', default=1, help="ID - с которого начать.", type=int)
    parser.add_argument('end_id', nargs='?', default=10, help="ID - которым закончить.", type=int)
    args = parser.parse_args()

    downloaded = 0

    for book_id in tqdm(range(args.start_id, args.end_id+1)):
        try:
            print('\033[H')  # Чистим экран
            book_urls = {
                        "book_url": f"https://tululu.org/b{book_id}/",
                        "download_url": f"https://tululu.org/txt.php",
                        }
            for type_of_url, url in book_urls.items():
                response = get_response(url, book_id)
                check_redirect(response)
                if type_of_url == "book_url":
                    head_response = response
                elif type_of_url == "download_url":
                    download_response = response

            book_context = parse_book_context(head_response)

            if GENRE not in book_context['genres']:
                print('\033[H')  # Чистим экран
                print(f'Книги с id: "{book_id}" не подходит по жанру.')
                continue
            book_filename = f"{book_id}. {book_context['title']}.txt"
            book_save_path = download_txt(download_response, book_filename, BOOK_FOLDER)

            image_filename = Path(book_context['image_link']).name
            full_img_link = urljoin(book_urls['book_url'], book_context['image_link'])

            download_image(full_img_link, image_filename, IMAGE_FOLDER)
            if book_context['comments']:
                comments_filename = f"{book_id}. {book_context['title']}-comments.txt"
                save_comments(book_context['comments'], comments_filename, COMMENTS_FOLDER)

            downloaded += 1
            print('\033[H')  # Чистим экран
            print(f'Книга "{book_context["title"]}" сохранена в: "{book_save_path}".')

        except ConnectionError:
            print('\033[H')  # Чистим экран
            print("Проблема с интернет соединением! Повторная попытка...")
            sleep(5)
            continue

        except HTTPError:
            print('\033[H')  # Чистим экран
            print(f'Книги с id: "{book_id}" не существует.')
            continue

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


def save_comments(comments, filename, folder='comments/'):

    os.makedirs(COMMENTS_FOLDER, exist_ok=True)
    comments_save_path = os.path.join(folder, filename)
    with open(comments_save_path, 'w') as file:
        file.write("\n".join(comments))


def get_response(url, id):
    params = {"id": id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response


def check_redirect(response):
    redirect_codes = [300, 301, 302, 303, 304, 305, 306, 307, 308]

    for code in response.history:
        if code.status_code in redirect_codes:
            raise HTTPError()


if __name__ == "__main__":
    main()
