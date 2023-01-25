import requests
from requests.exceptions import HTTPError

import os


def main():
    for id in range(1,11):
        dir = os.makedirs('books', exist_ok=True)
        url = f"https://tululu.org/txt.php?id={id}"

        filename = f"book-{id}.txt"
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        try:
            check_redirect(response)
        except:
            print(f"Книги c id {id} не существует.")
            continue

        with open(f"books/{filename}", 'wb') as book:
            book.write(response.content)
        print(f"{filename} is downloaded")


def check_redirect(response):
    if response.status_code !=200:
        raise HTTPError()





if __name__ == "__main__":
    main()
