# Scraper para goodreads
Este scraper tiene como objetivo extraer información acerca de los libros y las opiniones relacionados a ellos dentro de la plataforma goodreads. Esto con fines netamente académicos y de investigación.
La informacion personal de los usuarios es totalmente descartada y únicamente se toma en cuenta la opinion y el apoyo que esta recibió. Si goodreads cambia su layout, es posible que el script se rompa.

## Uso
Es opcional, pero recomendado crear un entorno virtual.
1. Descargar las dependencias: ```pip install -r requirements.txt```.
2. Ejecutar el programa: ```python scraper.py```.
3. Elegir si se desea generar el archivo de géneros, esto no es necesario, pues ya se incluyen en ```genres.txt```.
4. Esperar a que se generen los JSON relacionados a los libros.
