import argparse
import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

BOOK_FOLDER="books/"
IMAGE_FOLDER="images/"
COMMENTS_FOLDER="comments/"
GENRE="Научная фантастика"

def main():

    parser = argparse.ArgumentParser(
        description = "Этот скрипт скачивает книги с библиотеки tululu.ru"
    )
    parser.add_argument('start_id', help="ID - с которого начать", type=int)
    parser.add_argument('end_id', help="ID - которым закончить", type=int)
    args = parser.parse_args()

    downloaded = 0

    for id in range(args.start_id, args.end_id+1):

        book_url = f"https://tululu.org/b{id}/"
        download_url = f"https://tululu.org/txt.php?id={id}"
        try:
            head_response, download_response = get_response_and_check(book_url, download_url)
        except:
            print(f'Книги с id: "{id}" не существует.')
            continue
        book_context = parse_book_context(head_response)
        if not GENRE in book_context['genres']:
            print(f'Книги с id: "{id}" не подходит по жанру.')
            continue
        book_filename = f"{id}. {book_context['title']}.txt"
        book_save_path = download_txt(download_response, book_filename, BOOK_FOLDER)

        image_filename = Path(book_context['image_link']).name
        full_img_link = urljoin(book_url, book_context['image_link'])

        download_image(full_img_link, image_filename, IMAGE_FOLDER)
        if book_context['comments']:
            comments_filename = f"{id}. {book_context['title']}-comments.txt"
            save_comments(book_context['comments'], comments_filename, COMMENTS_FOLDER)

        downloaded+=1
        print(f'Книга "{book_context["title"]}" сохранена в: "{book_save_path}"')

    print(f"\nВСЕГО ЗАГРУЖЕНО: {downloaded} КНИГ")


def parse_book_context(response):

    context={}
    page_text = BeautifulSoup(response.text, 'lxml')
    
    title_and_author = page_text.find('td', class_='ow_px_td').find('h1').text.split('::')
    title_and_author = map(lambda x: x.strip(), title_and_author)

    context['title'], context['author'] = title_and_author
    context["image_link"] = page_text.find("div", class_="bookimage").find("img")["src"]
    dirt_genres = page_text.find("span", class_="d_book").find_all("a")
    context['genres'] = list(map(lambda x: x.text, dirt_genres))

    context['comments'] = []
    divs = page_text.find_all("div", class_="texts")
    for div in divs:
        comment = div.find("span", class_="black").text
        context['comments'].append(comment)

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


def get_response_and_check(*urls):
    responses = []
    for url in urls:
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        check_redirect(response)
        responses.append(response)
    return responses

def check_redirect(response):
    if response.status_code !=200:
        raise HTTPError()


if __name__ == "__main__":
    main()
