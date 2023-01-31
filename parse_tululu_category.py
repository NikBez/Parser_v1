from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


def get_book_ids(base_url, start_page, end_page):
    book_ids = []
    for page in range(start_page, end_page+1):
        page_url = urljoin(base_url, str(page))
        response = requests.get(page_url)
        response.raise_for_status()
        book_ids += get_page_ids(response)
    return book_ids


def get_page_ids(response):
    page_text = BeautifulSoup(response.text, 'lxml')
    book_ids = page_text.find("div", id="content").find_all("table", class_="d_book")
    return [book_id.a['href'].lstrip("/b").rstrip("/") for book_id in book_ids]
