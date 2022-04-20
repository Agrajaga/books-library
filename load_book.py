import os
import urllib.parse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError, Response, get


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise HTTPError


def download_txt(url, filename, folder='books/'):
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


if __name__ == "__main__":
    os.makedirs("books", exist_ok=True)

    for index in range(1, 11):
        book_url = f"https://tululu.org/b{index}/"
        response = get(book_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)

            soup = BeautifulSoup(response.text, "lxml")
            caption_tag = soup.find(id="content").find("h1")
            caption = caption_tag.text
            title, author = map(str.strip, caption.split("::"))

            params = {
                "id": index,
            }
            txt_url = f"https://tululu.org/txt.php?{urllib.parse.urlencode(params)}"
            filename = f"{index}. {title}"
            download_txt(txt_url, filename)
        except HTTPError:
            print(f"HTTPError on {index}")
        