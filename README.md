# Download images from tululu.ru
This script can download books in `.txt` format to your computer.

## How to install

````
pipenv install -r requirements.txt
````
## How to setup

All settings have default values, but you can change it if you want.
````
BOOK_FOLDER - путь к папке с книгами
IMAGE_FOLDER - путь к папке с обложками
COMMENTS_FOLDER - путь к папке с комментариями
GENRE - Жанр книги который необходимо скачать
````

## How to use

Run:
````
python3 download_from_tululu.py [start_id] [end_id]
````

