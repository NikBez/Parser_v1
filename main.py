import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import os
from  pathvalidate import sanitize_filename


def main():

    os.makedirs('books', exist_ok=True)
    for id in range(1,11):
        book_url = f"https://tululu.org/b{id}/"
        download_url = f"https://tululu.org/txt.php?id={id}"

        try:
            head_response, download_response = get_response_and_check(book_url, download_url)
        except:
            print(f'Книги c id "{id}" не существует.')
            continue

        title, author = get_book_headers(head_response)
        filename = f"{id}. {title}.txt"

        to_save_path = download_txt(download_response, filename)
        print(f'Книга "{title}" сохранена: {to_save_path}')


def check_redirect(response):
    if response.status_code !=200:
        raise HTTPError()

def get_book_headers(response):

    titles = BeautifulSoup(response.text, 'lxml')
    title_and_author = titles.find('td', class_='ow_px_td').find('h1').text
    title, author =  title_and_author.split('::')
    return title.strip(), author.strip()

def download_txt(response, filename='text/text/1.txt', folder='books/'):

    cleaned_filename = sanitize_filename(filename)
    to_save_path = os.path.join(folder, cleaned_filename)
    with open(to_save_path, 'wb') as book:
        book.write(response.content)
    return to_save_path



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
