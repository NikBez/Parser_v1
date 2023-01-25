import requests
import os

for id in range(1,11):
    dir = os.makedirs('books', exist_ok=True)
    url = f"https://tululu.org/txt.php?id={id}"

    filename = f"book-{id}.txt"
    response = requests.get(url)
    response.raise_for_status()
    print(filename)

    with open(f"books/{filename}", 'wb') as book:
        book.write(response.content)
