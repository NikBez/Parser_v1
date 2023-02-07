import os
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from parse_tululu_category import JSON_FOLDER
from pathlib import Path
from livereload import Server
from more_itertools import chunked

COLUMNS_COUNT = 2
BOOKS_PER_PAGE = 10

def main():

    rebuild()
    server = Server()
    server.watch('books.json', rebuild)
    server.watch('template.html', rebuild)
    server.serve(root='.')

def rebuild():
    try:
        with open(Path(JSON_FOLDER)/'books.json', "r") as file:
            books = json.load(file)
    except IOError:
        print("Файл не найден")
        sys.exit()

    chunked_by_page_books = chunked(books, BOOKS_PER_PAGE)
    os.makedirs('./pages/', exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    for count, page in enumerate(chunked_by_page_books, 1):
        chunked_by_column_books = chunked(page, COLUMNS_COUNT)
        template = env.get_template('template.html')
        rendered_page = template.render(
            book_rows=chunked_by_column_books
        )
        with open(f'pages/index{count}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

    print("Site rebuilt")


if __name__ == '__main__':

    main()