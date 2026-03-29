# Código fuente
Para utilizar este codigo, es recomendable crear un entorno virtual ```uv venv```, para luego instalar las dependencias necesarias con ```uv sync```.
## ```main.py```
Modulo principal que reune la logica del scraper y de subir el documento generado a un cucket de s3. Este script recolecta la información del sitio, la guarda tempralmente en local como json y la sube a s3 antes de borrarla.
## ```scraper.py```
Este scraper tiene como objetivo extraer información acerca de los libros y las opiniones relacionados a ellos dentro de la plataforma goodreads dentro de la seccion "most read", la cual se actualiza cada semana. Esto con fines netamente académicos y de investigación.
La informacion personal de los usuarios es totalmente descartada y únicamente se toma en cuenta la opinion y el apoyo que esta recibió. Si goodreads cambia su layout, es posible que el script se rompa.
Uso:
1. Crear un objeto de la clase ```most_read_scraper```.
2. Ejecutar el metodo ```scrape```, que guarda la informacion obtenida en el atributo ```books_data```.
