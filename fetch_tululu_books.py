import argparse
import os
import sys
from time import sleep
from urllib.parse import urlencode, urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import Response, get
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tqdm import tqdm

HOST_URL = "https://tululu.org/"


def parse_book_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "lxml")
    caption_tag = soup.find(id="content").find("h1")
    caption = caption_tag.text
    title, author = map(str.strip, caption.split("::"))

    img_tag = soup.find(class_="bookimage").find("img")
    image_source = img_tag["src"]

    genre_tags = soup.find("span", class_="d_book").find_all("a")
    genres = [genre_tag.text for genre_tag in genre_tags]

    comment_tags = soup.find_all(class_="texts")
    comments = [tag.find("span", class_="black").text for tag in comment_tags]
    
    return {
        "title": title,
        "author": author,
        "relative_image_url": image_source,
        "genres": genres,
        "comments": comments,
    }


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise HTTPError


def download_txt(url, filename, folder="books/"):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = get(url, timeout=5)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))

    with open(filepath, "w") as txt_file:
        txt_file.write(response.text)

    return filepath


def download_image(url, filename, folder="images/"):
    response = get(url, timeout=5)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as txt_file:
        txt_file.write(response.content)

    return filepath


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_id", type=int, default=1)
    parser.add_argument("--end_id", type=int, default=10)

    args = parser.parse_args()

    with tqdm(total=args.end_id + 1 - args.start_id) as progressbar:
        for index in range(args.start_id, args.end_id + 1):
            while True:
                try:
                    book_url = urljoin(HOST_URL, f"b{index}/")
                    response = get(book_url, timeout=5)
                    response.raise_for_status()
                    check_for_redirect(response)
                    book_props = parse_book_page(response.text)
                    params = {
                        "id": index,
                    }
                    txt_url = urljoin(HOST_URL, f"txt.php?{urlencode(params)}")
                    filename = f"{index}. {book_props['title']}"
                    download_txt(txt_url, filename)

                    image_source = urljoin(
                        HOST_URL, book_props["relative_image_url"])
                    image_name = urlsplit(image_source).path.split("/")[-1]
                    download_image(image_source, image_name)
                    break
                except HTTPError:
                    print("HTTP error, skip request...", file=sys.stderr)
                    break
                except ConnectionError as err:
                    print(f"{err} : wait 3 sec.", file=sys.stderr)
                    sleep(3)
                except Timeout:
                    print("Timeout error, try again...", file=sys.stderr)

            progressbar.update()
