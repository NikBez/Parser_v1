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

def main():

    os.makedirs(BOOK_FOLDER, exist_ok=True)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    os.makedirs(COMMENTS_FOLDER, exist_ok=True)

    for id in range(1,11):
        book_url = f"https://tululu.org/b{id}/"
        download_url = f"https://tululu.org/txt.php?id={id}"

        try:
            head_response, download_response = get_response_and_check(book_url, download_url)
        except:
            print(f'Книги c id "{id}" не существует.')
            continue

        title, author, image_link, comments = get_book_context(head_response)

        book_filename = f"{id}. {title}.txt"
        book_save_path = download_txt(download_response, book_filename, BOOK_FOLDER)

        image_filename = Path(image_link).name
        full_img_link = urljoin(book_url, image_link)

        download_image(full_img_link, image_filename, IMAGE_FOLDER)
        if comments:
            comments_filename = f"{id}. {title}-comments.txt"
            save_comments(comments, book_filename, COMMENTS_FOLDER)

        print(f'Книга "{title}" сохранена в: "{book_save_path}"')


def check_redirect(response):
    if response.status_code !=200:
        raise HTTPError()


def get_book_context(response):

    context = BeautifulSoup(response.text, 'lxml')

    title_and_author = context.find('td', class_='ow_px_td').find('h1').text
    title, author = title_and_author.split('::')
    picture_link = context.find("div", class_="bookimage").find("img")["src"]

    comments = []
    divs = context.find_all("div", class_="texts")
    for div in divs:
        comment = div.find("span", class_="black").text
        comments.append(comment)


    return title.strip(), author.strip(), picture_link, comments


def download_txt(response, filename, folder='books/'):

    cleaned_filename = sanitize_filename(filename)
    book_save_path = os.path.join(folder, cleaned_filename)
    with open(book_save_path, 'wb') as book:
        book.write(response.content)
    return book_save_path

def download_image(img_url, img_filename, folder='images/'):

    response = requests.get(img_url)
    response.raise_for_status()
    image_save_path = os.path.join(folder, img_filename)
    with open(image_save_path, "wb") as image:
        image.write(response.content)
    return image_save_path

def save_comments(comments, filename, folder='comments/'):
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


if __name__ == "__main__":
    main()
