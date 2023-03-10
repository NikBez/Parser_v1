# Download images from tululu.ru
Этот проект позволяет спарсить книги в формате`.txt` а так же их описания и обложки.
А затем сгенерировать автономный сайт для вашего дедушки, который хочет читать чиать книги у себя в деревне без интернета.

## How to install localy

````
pip3 install pipenv
pipenv install -r requirements.txt
````
## How to setup

All settings have default values, but you can change it if you want.

### parse_tululu_category.py:
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

### render_website.py:
````
COLUMNS_COUNT = сколько колонок верстать на сайте
BOOK_CARDS_PER_PAGE = сколько книг добавлять на одну страницу
````

List of command-line arguments:

````
json_path - можно задать свой путь к файлу json
````

## How to use

Для загрузки исходных данных с сайта tululu:
````
python3 parse_tululu_category.py
````

Для генерации страниц с книгами на основе загруженных данных:
````
python3 render_website.py
````

## How to use Local offline
Будет создана папка `pages/` в которую будет сохранены сгенерированные страницы сайта.  
**Их можно напрямую открыть в вашем браузере** 

## How to use Local online
Start local server using:
````
python3 render_website.py
````
Go to this [**link**](http://127.0.0.1:5500/pages/index1.html)

## LIVE DEMO
Готовый сверстанный сайт можно посмотреть по ссылке 
[nikbez.github.io/DEMO](https://nikbez.github.io/Parser_v1/)
