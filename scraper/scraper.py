import requests
from bs4 import BeautifulSoup
import time
import re
import json
from pathlib import Path
import os

# Cabezeras para evitar que la conexion sea rechazada
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.goodreads.com",
}

# Nombre del arvchivo para los generos
GENRES_FILENAME = "genres.txt"

# Expresion regular para el url de un libro
REGEX_BOOK_URL = r"https://www\.goodreads\.com/book/show/\d+[\w.\-]+$"


DATA_DIR = "data/"


def scrap_genre_names_list():
    """
    Funcion para scrapear el nombre de los generos reconocidos por goodreads
    Guarda salida en documento para evitar scrapear la lista cada vez,
    pues la funcion implementa una espera aleatoria para evitar que la pagina
    bloquee el trafico.
    No correr a menos que el docuento no exista o se quiera actualizar la lista
    """
    genre_names_list : list[str] = []
    base_genres_list_url: str = "https://www.goodreads.com/genres/list?page="

    session = requests.Session()
    session.headers.update(HEADERS)
    for page in range(1, 17):
        print(f"Scraping page {page}/17")
        try:
            response = session.get(base_genres_list_url + f"{page}", timeout=10)
        except requests.exceptions.ReadTimeout:
            print(f"Timeout en {base_genres_list_url + f"{page}"}, reintentando...")
            time.sleep(5)
            try:
                response = session.get(base_genres_list_url + f"{page}", timeout=15)
            except requests.exceptions.ReadTimeout:
                print(f"Timeout definitivo, saltando {base_genres_list_url + f"{page}"}")
                return {}
        if response.status_code != 200:
            print(f"Error scraping page {page}: \n {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        genres_current_page = [
            genre_element.get_text(strip=True)  
            for genre_element in soup.select("div.shelfStat a")
        ]
        genre_names_list.extend(genres_current_page)
        time.sleep(7)
    
    print("Scraping was successful, writing to file")
    with open(GENRES_FILENAME, 'w') as file:
        for g in genre_names_list:
            file.write(g + "\n")
        file.writelines(genre_names_list)


def parse_book_data(soup: BeautifulSoup) -> dict:
    """
        Obtiene la informacion del libro
        Devuelve los metadatos del libro en un diccionario
    """
    book_data = {"title":"", 
                 "author":"", 
                 "description":"" , 
                 "genres":[], 
                 "rating": None, 
                 "date": ""}
    # == Obteniendo los elementos HTML del libro ==
    title_element = soup.select_one("h1[data-testid='bookTitle']")
    author_element = soup.select_one("span.ContributorLink__name[data-testid='name']")
    description_element = soup.select_one("div[data-testid='description'] .Formatted")
    genres_element = soup.select("div[data-testid='genresList'] .Button__labelItem")
    rating_element = soup.select_one("div.RatingStatistics__rating")
    date_element = soup.select_one("p[data-testid='publicationInfo']")

    # == Extrayendo la informacion de los elementos ==
    if title_element:
        book_data["title"] = title_element.get_text(strip=True)
    if author_element:
        book_data["author"] = author_element.get_text(strip=True)
    if description_element:
        book_data["description"] = description_element.get_text(strip=True)
    if genres_element:
        if len(genres_element) > 1:
            genres_element.pop()
        book_data["genres"] = [g.get_text(strip=True) for g in genres_element]
    if rating_element:
        try:
            book_data["rating"] = float(rating_element.get_text(strip=True))
        except ValueError:
            pass
    if date_element:
        date = date_element.get_text(strip=True)
        date = date.replace("First published ", '')
        date = date.replace(',', '')
        book_data["date"] = date
    
    return book_data


def parse_likes(likes: str) -> int:
    likes = likes.strip()
    likes = likes.replace("likes", "")
    if ',' in likes:
        likes = likes.replace(',','')
    elif 'k' in likes:
        likes = likes.replace('k','')
        return int(float(likes) * 1000)
    return int(likes)


def parse_reviews(soup: BeautifulSoup):
    """
    Obtiene la infirmacion de las resenas del libro
    """
    reviews = []

    for card in soup.select("article.ReviewCard"):
        text = None
        likes = None
        # == Obteniendo los elementos HTML de la opinion ==
        text_element = card.select_one(".ReviewText__content") 
        footer = card.select_one("footer.SocialFooter")
        
        # == Extrayendo la informacion de los elementos ==
        if text_element:
            text = text_element.get_text(strip=True)

        buttons = footer.select("span.Button__labelItem") if footer else None
        if buttons:
            for btn in buttons:
                bt_text = btn.get_text(strip=True)
                if "likes" in bt_text:
                    likes = parse_likes(bt_text)
                    break

        if text:
            reviews.append({
                "text": text,
                "likes": likes,
            })

    return reviews


def scrape_book(URL: str) -> dict:
    """
        Recolecta la informacion del libro proporcionado como parametro y sus resenas
        Devuelve un diccionario con el formato {"libro": info_libro, "reviews": info_reviews}
    """
    if not re.match(REGEX_BOOK_URL, URL):
        print(f"El url {URL} es invalido, debes proporcionar el url del libro")
        return {}
    
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        response = session.get(URL, timeout=10)
    except requests.exceptions.ReadTimeout:
        print(f"Timeout en {URL}, reintentando...")
        time.sleep(5)
        try:
            response = session.get(URL, timeout=15)
        except requests.exceptions.ReadTimeout:
            print(f"Timeout definitivo, saltando {URL}")
            return {}

    if response.status_code != 200:
        print(f"Error {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    book_data = parse_book_data(soup)
    reviews = parse_reviews(soup)

    return {
        "book": book_data,
        "reviews": reviews
    }


def get_books_urls_from_genre(genre: str) -> list[str]:
    """
        Obtiene los url a los libros de una seccion o genero 
        El link de la seccion o genero debe comenzar como:\n
        https://www.goodreads.com/shelf/show/\n
        A esta url base se le concatenara el genero que se indique
        en el parametro
    """
    base_genre_url: str = "https://www.goodreads.com/shelf/show/"
    base_book_url: str = "https://www.goodreads.com"
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        response = session.get(base_genre_url + f"{genre}", timeout=10)
    except requests.exceptions.ReadTimeout:
        print(f"Timeout en {base_genre_url + f"{genre}"}, reintentando...")
        time.sleep(5)
        try:
            response = session.get(base_genre_url + f"{genre}", timeout=15)
        except requests.exceptions.ReadTimeout:
            print(f"Timeout definitivo, saltando {base_genre_url + f"{genre}"}")
            return []
    
    if response.status_code != 200:
         print(f"Error scraping genre {genre}: \n {response.status_code}")
         return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    books_urls = [
        base_book_url + str(a.get("href"))
        for a in soup.select("a.bookTitle")
    ]

    return books_urls


def save_to_json(all_books: list, filename: str):
    """
    Guarda toda la lista de libros en un único archivo JSON válido
    """
    with open(filename + ".json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)


def main():
    update_list_input = str(input("¿Actualizar o crear archivo de generos a scrapear? [y,N]:"))
    if update_list_input == "y":
        scrap_genre_names_list()


    with open(GENRES_FILENAME, 'r') as file:
        genres = file.readlines()
    
    if not genres:
        print("No se pudo encontrar el archivo de generos")
        return
    
    try:
        os.mkdir(DATA_DIR)
    except PermissionError:
        print(f"Permiso denegado para crear directorio {DATA_DIR}")
        return
    except FileExistsError:
        pass

    for g in genres:
        if Path(f"{DATA_DIR}{g.strip()}.json").exists():
            print(f"{DATA_DIR}{g.strip()}.json encontrado, omitiendo")
            continue
        print(f"Iniciando scrapeando: {g.strip()}")
        books_urls = get_books_urls_from_genre(g.strip())
        books_data = []
        i: int = 0
        for url in books_urls:
            time.sleep(5)
            book_data = scrape_book(url)
            if book_data:
                books_data.append(book_data)
            i += 1
            print(f"Se han scrapeado {i}/{len(books_urls)} libros del genero {g.strip()}")

        save_to_json(books_data, f"{DATA_DIR}{g.strip()}")
        print(f"Scrapeo finalizado: {g}")


if __name__ == "__main__":
    main()