import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from parse_tululu_category import JSON_FOLDER
from pathlib import Path
from livereload import Server
from more_itertools import chunked

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

    chunked_books = chunked(books, 2)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(
        book_rows=chunked_books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


if __name__ == '__main__':

    main()