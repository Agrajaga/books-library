import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import json


BOOKS_ON_PAGE = 10
BOOK_COLUMNS = 2


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("template.html")

    with open("books.json", "r") as books_file:
        books = json.load(books_file)

    chunked_books = list(chunked(books, BOOKS_ON_PAGE))
    for page_num, books_chunk in enumerate(chunked_books, start=1):
        rendered_page = template.render(
            books=list(chunked(books_chunk, BOOK_COLUMNS)),
            current_page=page_num,
            total_page=len(chunked_books),
        )

        with open(f"library/pages/index{page_num}.html", "w", encoding="utf8") as file:
            file.write(rendered_page)

    print("Site rebuild")


if __name__ == "__main__":
    os.makedirs("library/pages", exist_ok=True)
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".")
