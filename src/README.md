# Código fuente
## ```scraper.py```
Este scraper tiene como objetivo extraer información acerca de los libros y las opiniones relacionados a ellos dentro de la plataforma goodreads dentro de la seccion "most read", la cual se actualiza cada semana. Esto con fines netamente académicos y de investigación.
La informacion personal de los usuarios es totalmente descartada y únicamente se toma en cuenta la opinion y el apoyo que esta recibió. Si goodreads cambia su layout, es posible que el script se rompa.
Uso:
1. Crear un objeto de la clase ```most_read_scraper```.
2. Ejecutar el metodo ```scrape```, que guarda la informacion obtenida en el atributo ```books_data```.
