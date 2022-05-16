from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

if __name__ == "__main__":
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("template.html")

    with open("books.json", "r") as books_file:
        books_json = books_file.read()

    books = json.loads(books_json)

    rendered_page = template.render(
        books=books,
    )

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)
