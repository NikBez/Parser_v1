# Download images from tululu.ru
This script can download books in `.txt` format to your computer.

## How to install

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

Run:
````
python3 parse_tululu_category.py
````

