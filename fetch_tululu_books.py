import argparse
import os
from urllib.parse import urlencode, urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError, Response, get
from tqdm import tqdm


def parse_book_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "lxml")
    caption_tag = soup.find(id="content").find("h1")
    caption = caption_tag.text
    title, author = map(str.strip, caption.split("::"))

    img_tag = soup.find(class_="bookimage").find("img")
    image_source = img_tag["src"]

    genre_tags = soup.find("span", class_="d_book").find_all("a")
    genres = [genre_tag.text for genre_tag in genre_tags]

    comments = []
    for div_tag in soup.find_all(class_="texts"):
        comment_tag = div_tag.find("span", class_="black")
        comments.append(comment_tag.text)

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
    response = get(url)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))

    with open(filepath, "w") as txt_file:
        txt_file.write(response.text)

    return filepath


def download_image(url, filename, folder="images/"):
    response = get(url)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as txt_file:
        txt_file.write(response.content)

    return filepath


if __name__ == "__main__":
    HOST_URL = "https://tululu.org/"

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_id", type=int, default=1)
    parser.add_argument("--end_id", type=int, default=10)

    args = parser.parse_args()

    with tqdm(total=args.end_id + 1 - args.start_id) as progressbar:
        for index in range(args.start_id, args.end_id + 1):
            book_url = urljoin(HOST_URL, f"b{index}/")
            response = get(book_url)
            response.raise_for_status()
            try:
                check_for_redirect(response)
                book_props = parse_book_page(response.text)
                params = {
                    "id": index,
                }
                txt_url = urljoin(HOST_URL, f"txt.php?{urlencode(params)}")
                filename = f"{index}. {book_props['title']}"
                download_txt(txt_url, filename)

                image_source = urljoin(HOST_URL, book_props["relative_image_url"])
                image_name = urlsplit(image_source).path.split("/")[-1]
                download_image(image_source, image_name)
            except HTTPError:
                pass
            progressbar.update()