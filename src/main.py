from scraper import most_read_scraper
import json
from datetime import date
import logging
import boto3
from botocore.exceptions import NoCredentialsError

BUCKET = "unam-2026-ingenieriadedatos-equipo4-203433203458-us-east-2-an"


def main():
    scraper = most_read_scraper()
    scraper.scrape()
    if not scraper.books_data:
        logging.error("No se pudo obtener informacion de los libros, terminando")
        return
    
    local_filename: str = str(date.today()) + ".json"
    with open(local_filename, "w", encoding="utf-8") as file:
        json.dump(scraper.books_data, file, ensure_ascii=False, indent=2)

    remote_filename: str = f"1bronze/{local_filename}"

    s3_bucket = boto3.client('s3')

    try:
        print(f"Subiendo {local_filename} a s3://{BUCKET}/{remote_filename}...")
        s3_bucket.upload_file(local_filename, BUCKET, remote_filename)
        print("Carga exitosa")

    except FileNotFoundError:
        logging.exception("El archivo local no fue encontrado.")
    except NoCredentialsError:
        logging.exception("No se encontraron credenciales de AWS configuradas.")
    except Exception as e:
        logging.exception(f"{e}")

    


if __name__ == "__main__":
    main()
