# Автономная библиотека книг с сайта tululu.org
![image](https://user-images.githubusercontent.com/22379662/169149217-24a2c20d-f536-4248-be75-92bc4f694bbc.png)

Данный проект предназначен для создания автономной библиотеки книг в жанре научной фантастики с сайта [tululu.org](https://tululu.org).  
Библиотеку можно использовать с компьютера не подключенного к сети Интернет. Для этого скачайте папку `library` на локальный компьютер и откройте в браузере любой файл из папки `library/pages`.  
Также библиотека размещена на [ресурсе GitPages](https://agrajaga.github.io/books-library/library/pages/index1.html), там можно ознакомиться с представленными книгами.


## Создание автономной библиотеки
Проект содержит 3 скрипта:
1. fetch_tululu_books.py  
Умеет скачивать книги по `id`. В папке `books` будут располагаться тексты загруженных книг в виде txt-файлов, а в папку `images` скачаются изображения обложек. 
2. parse_tululu_category.py  
Скачивает книги в жанре [научной фантастики](https://tululu.org/l55/). Умеет скачивать книги с различных страниц, т.к. сайт выводит список книг с разбиением на страницы. Помимо скачивания текстов и обложек книг, составляет `json-файл`, в котором хранит информацию о скачанных книгах:
```json
[
    {
        "author": "ИВАНОВ Сергей", 
        "title": "Алиби", 
        "img_src": "data/images/239.jpg", 
        "txt_path": "data/books/Алиби.txt", 
        "comments": [
            "Детский вариант анекдотов про Шерлока Холмса)", 
            "Загадки я люблю.)))", 
            "А мне понравилось, люблю, знаете ли, всякие загадочки, головоломочки, кроссвордики, Гимнастика ума, одним словом... \nВо всём можно найти положительные моменты, не разгадал загадку, так хоть гренки научился готовить отменные... :-)", 
            "Очень поучительное для ребенка 10 лет."
            ], 
        "genres": [
            "Научная фантастика", 
            "Прочие Детективы"]
    }
]
```
3. render_website.py  
Генерирует веб-страницы библиотеки


### Как установить

Для запуска понадобится установленный Python3. Установите необходимые библиотеки командой:
```
pip install -r requirements.txt
```

### Использование
#### ___fetch_tululu_books.py___
При использовании скрипта можно указывать начальный и конечный id-книг с помощью параметров `--start_id` и `--end_id`. Например, чтобы скачать книги с 20 по 30 (включительно):

```
python fetch_tululu_books.py --start_id 20 --end_id 30
```
Если параметры не указать, то будут скачаны первые 10 книг.

#### ___parse_tululu_category.py___
При запуске скрипта можно указывать следующие параметры:
- _`--start_page`_ номер страницы, начиная с которой будут скачиваться книги, если не указывать, то будут скачаны книги начиная с первой страницы.
- _`--end_page`_ номер страницы, до которой будут скачиваться книги, если не указывать, то книги будут скачаны до последней страницы сайта
- _`--dest_folder`_ путь к каталогу с результатами парсинга: картинкам, книгам, JSON
- _`--json_path`_ указать свой путь к *.json файлу с результатами, по-умолчанию `books.json`
- _`--skip_imgs`_ не скачивать картинки
- _`--skip_txt`_ не скачивать книги

Например, будут скачаны без картинок обложек книги с 20 по 30 (исключая) страницу
```
python parse_tululu_category.py --start_page 20 --end_page 30 --skip_imgs
```
#### ___render_website.py___
При запуске генерирует html-страницы для просмотра списков книг. После генерации страниц запускается веб-сервер и библиотека становится доступна по адресу http://127.0.0.1:5500/library/pages/index1.html
```
python render_website.py
```


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
