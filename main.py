import requests
import os

url = "https://tululu.org/txt.php?id=32168"
filename = "book.txt"
response = requests.get(url)
response.raise_for_status()

with open(filename, 'wb') as book:
    book.write(response.content)
