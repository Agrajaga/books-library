import os
from urllib.parse import urlsplit, urljoin, urlencode

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError, Response, get


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
            img_tag = soup.find(class_="bookimage").find("img")
            image_source = urljoin("https://tululu.org", img_tag["src"])

            image_name = urlsplit(image_source).path.split("/")[-1]
            download_image(image_source, image_name)

            print(title)
            for div_tag in soup.find_all(class_="texts"):
                comment_tag = div_tag.find("span", class_="black")
                print(comment_tag.text)
            print()
            
            params = {
                "id": index,
            }
            txt_url = f"https://tululu.org/txt.php?{urlencode(params)}"
            filename = f"{index}. {title}"
            download_txt(txt_url, filename)
        except HTTPError:
            print(f"HTTPError on {index}")
        