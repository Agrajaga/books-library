import argparse
import json
import os
import sys
from time import sleep
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tqdm import tqdm

import fetch_tululu_books as ftb

if __name__ == "__main__":
    total_pages = 1
    sci_fi_genre_code = "l55/"
    txt_folder = "books/"
    img_folder = "images/"

    os.makedirs(txt_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)

    books = []
    book_links = []
    base_url = urljoin(ftb.HOST_URL, sci_fi_genre_code)

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_page", type=int, default=699)
    parser.add_argument("--end_page", type=int)
    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page
    if not end_page:
        end_page = start_page + 1
    page_number = start_page

    book_links = []
    while page_number < end_page:
        page_url = base_url
        if page_number > 1:
            page_url = urljoin(base_url, str(page_number))

        response = get(page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        if not args.end_page:
            last_page = soup.select_one("p.center > :last-child").text
            end_page = int(last_page) + 1

        links_selector = ".bookimage a"
        book_links.extend([urljoin(page_url, a_tag["href"])
                           for a_tag in soup.select(links_selector)])
        page_number += 1

    tqdm.write(
        f"Download {len(book_links)} books from page {start_page} to page {end_page}")
    with tqdm(total=len(book_links)) as progressbar:
        for index, book_url in enumerate(book_links):
            while True:
                try:
                    response = get(book_url, timeout=5)
                    response.raise_for_status()
                    ftb.check_for_redirect(response)
                    book_props = ftb.parse_book_page(response.text)

                    txt_url = urljoin(book_url, book_props["relative_txt_url"])
                    txt_path = ftb.download_txt(
                        txt_url, book_props['title'], txt_folder)

                    image_source = urljoin(
                        book_url, book_props["relative_image_url"])
                    url_path = unquote(urlsplit(image_source).path)
                    image_name = os.path.split(url_path)[1]
                    img_path = ftb.download_image(
                        image_source, image_name, img_folder)

                    books.append({
                        "author": book_props["author"],
                        "title": book_props["title"],
                        "img_src": img_path,
                        "txt_path": txt_path,
                        "comments": book_props["comments"],
                        "genres": book_props["genres"],
                    })
                    break
                except HTTPError:
                    tqdm.write(
                        f"HTTP error, skip book {book_url}...", file=sys.stderr)
                    break
                except ConnectionError as err:
                    tqdm.write(f"{err} : wait 3 sec.", file=sys.stderr)
                    sleep(3)
                except Timeout:
                    tqdm.write("Timeout error, try again...", file=sys.stderr)

            progressbar.update()

    with open("books.json", "w", encoding="utf8") as books_file:
        json.dump(books, books_file, ensure_ascii=False)
