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

## Corriendo en AWS lambda
1. Crear un rol para poder publicar el layer generado a lambda.
2. Instalar las dependencias en la carpeta (no es necesario crear antes).
```
uv pip install \
  "beautifulsoup4==4.14.3" \
  "requests==2.33.0" \
  "tqdm==4.67.3" \
  --target layer/python/lib/python3.13/site-packages \
  --python-version 3.13 \
  --only-binary=:all:
```
3. Crear un paquete de las dependencias
```
cd layer && zip -r ../layer.zip . && cd ..
```
3. Importar la layer creada a lambda
```
aws lambda publish-layer-version \
  --layer-name "scraper-dependencies" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.13 \
  --compatible-architectures x86_64
```
4. Crear una funcion lambda básica con un Timeout de mínimo 3 minutos y con 512 MB de memoria.
5. Crear un paquete de las funciones a utilizar en lambda
```
zip function.zip lambda_function.py scraper.py
```
6. Actualizar el codigo de la funcion ya creada en el paso 4.
```
aws lambda update-function-code \
 --function-name LAMBDA_FUNC_NAME \
 --zip-file fileb://function.zip
```