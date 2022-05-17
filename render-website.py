import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import json

def on_reload():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("template.html")

    with open("books.json", "r") as books_file:
        books_json = books_file.read()

    books = json.loads(books_json)

    chunked_books = list(chunked(books, 10))
    for page_num, books_chunk in enumerate(chunked_books, start=1):
        rendered_page = template.render(
            books=list(chunked(books_chunk, 2)),
            current_page=page_num,
            total_page=len(chunked_books),
        )

        with open(f"pages/index{page_num}.html", "w", encoding="utf8") as file:
            file.write(rendered_page)

    print("Site rebuild")


if __name__ == "__main__":
    os.makedirs("pages", exist_ok=True)
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".")

    
