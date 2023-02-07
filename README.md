# Download images from tululu.ru
This script can download books in `.txt` format to your computer.
Generate HTML pages in a local site for my Granny

## How to install localy

````
pipenv install -r requirements.txt
````
## How to setup

All settings have default values, but you can change it if you want.
````
BOOK_FOLDER - стандартное название папки с книгами
IMAGE_FOLDER - стандартное название папки с обложками
JSON_FOLDER = стандартный путь к папке с json-файлом
CATEGORY_URL = ссылка на страницу категории книг с сайта tululu.org
BASE_PATH = корневая папка для сохранения материалов
COLUMNS_COUNT = сколько колонок верстать на сайте
BOOKS_PER_PAGE = сколько книг добавлять на одну страницу
````

List of command-line arguments:

````
start_page - с какой страницы начать
end_page - на какой странице закончить
dest_path - пользовательский путь на корневую папку
json_path - пользовательский путь для json-файла
skip_imgs - Скачивать обложки
skip_txt - Скачивать книги
````

Use `-h` for see more information


## How to use

Запустите для загрузки исходных данных с сайта tululu:
````
python3 parse_tululu_category.py
````

Запустите скрипт по рендерингу страниц для генерации страниц с книгами на основе загруженных данных:
````
python3 render_website.py
````


## LIVE DEMO
Готовый сверстанный сайт можно посмотреть по ссылке 
[nikbez.github.io/DEMO](https://nikbez.github.io/Parser_v1/)
