import argparse
import json
import logging
import os
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathlib import Path

from parse_tululu_category import JSON_FOLDER


COLUMNS_COUNT = 2
BOOK_CARDS_PER_PAGE = 10


def rebuild():
    try:
        with open(Path(args.json_path)/'books.json', 'r') as file:
            books_meta = json.load(file)
    except IOError:
        logging.error('Файл не найден.')
        sys.exit()

    chunked_by_page_book_cards = list(chunked(books_meta, BOOK_CARDS_PER_PAGE))
    os.makedirs('./pages/', exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    for count, page in enumerate(chunked_by_page_book_cards, 1):
        chunked_by_column_books = chunked(page, COLUMNS_COUNT)
        template = env.get_template('template.html')
        rendered_page = template.render(
            book_rows=chunked_by_column_books,
            pages_count=len(chunked_by_page_book_cards)+1,
            active=count,
            next=count+1,
            previous=count-1,
        )
        with open(f'pages/index{count}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скрипт генерирует страницы сайта')
    parser.add_argument('json_path', nargs='?', default=JSON_FOLDER, help='Путь к файлу с данными')
    args = parser.parse_args()

    rebuild()
    server = Server()
    server.watch(Path(args.json_path) / 'books.json', rebuild)
    server.watch('template.html', rebuild)
    server.serve(root='.')
