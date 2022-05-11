import argparse
import os
import sys
from time import sleep
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import Response, get
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tqdm import tqdm

HOST_URL = "https://tululu.org/"


def parse_book_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "lxml")
    caption_tag = soup.select_one("#content h1")
    caption = caption_tag.text
    title, author = map(str.strip, caption.split("::"))

    img_tag = soup.select_one(".bookimage img")
    image_source = img_tag["src"]

    txt_tag = soup.select_one("table.d_book a[title*='скачать книгу txt']")
    if not txt_tag:
        raise HTTPError
 
    genre_tags = soup.select("span.d_book a")
    genres = [genre_tag.text for genre_tag in genre_tags]

    comment_tags = soup.select(".texts span.black")
    comments = [tag.text for tag in comment_tags]

    return {
        "title": title,
        "author": author,
        "relative_image_url": image_source,
        "relative_txt_url": txt_tag["href"],
        "genres": genres,
        "comments": comments,
    }


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise HTTPError


def download_txt(url, filename, folder):
    """Download text files

    Downloads the text of the book from the link and saves it 
    to the specified folder under the specified name.

    Args:
        url (str): download link
        filename (str): the name of the file to save
        folder (str): the name of the folder to save

    Returns:
        str: the full path to the file where the text is saved
    """

    response = get(url, timeout=5)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))

    with open(filepath, "w") as txt_file:
        txt_file.write(response.text)

    return filepath


def download_image(url, filename, folder):
    response = get(url, timeout=5)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as txt_file:
        txt_file.write(response.content)

    return filepath


if __name__ == "__main__":
    txt_folder = "books/"
    img_folder = "images/"
    os.makedirs(txt_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_id", type=int, default=1)
    parser.add_argument("--end_id", type=int, default=1)
    args = parser.parse_args()

    end_id = args.end_id + 1
    start_id = args.start_id

    with tqdm(total=end_id - start_id) as progressbar:
        for index in range(start_id, end_id):
            while True:
                try:
                    book_url = urljoin(HOST_URL, f"b{index}/")
                    response = get(book_url, timeout=5)
                    response.raise_for_status()
                    check_for_redirect(response)
                    book_props = parse_book_page(response.text)
                    
                    txt_url = urljoin(book_url, book_props["relative_txt_url"])
                    filename = f"{index}. {book_props['title']}"
                    download_txt(txt_url, filename, txt_folder)

                    image_source = urljoin(
                        book_url, book_props["relative_image_url"])
                    url_path = unquote(urlsplit(image_source).path)
                    image_name = os.path.split(url_path)[1]
                    download_image(image_source, image_name, img_folder)
                    break
                except HTTPError:
                    tqdm.write(
                        f"HTTP error, skip request {index}...", file=sys.stderr)
                    break
                except ConnectionError as err:
                    tqdm.write(f"{err} : wait 3 sec.", file=sys.stderr)
                    sleep(3)
                except Timeout:
                    tqdm.write("Timeout error, try again...", file=sys.stderr)

            progressbar.update()
