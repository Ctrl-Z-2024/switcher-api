# El Switcher - API REST
API del juego de mesa "El Switcher" implementada con FastAPI.

## Instalación
Primero debemos tener instalado Python (seguir la [documentación oficial](https://www.python.org/)) y debemos crear un entorno virtual python ([ejemplo](https://sasheshsingh.medium.com/a-beginners-guide-of-installing-virtualenvwrapper-on-ubuntu-ce6259e4d609)) para poder correr el proyecto e instalar las librerias necesarias.

Clonamos el repositorio y nos movemos al directorio:
```bash
$ git clone https://github.com/Ctrl-Z-2024/switcher-api.git
$ cd switcher-api
```
Ahora activamos nuestro entorno virtual python e instalamos las librerias:
```bash
(env) $ pip install -r requirements.txt
```
Así ya tenemos las librerias necesarias instaladas y podemos proceder a levantar la aplicación.

## Levantamos la app
Para levantar la aplicación, nos movemos al directorio:
```bash
(env) $ cd app
```
Una vez en app, levantamos el servidor con el siguiente comando:
```bash
(env) $ uvicorn main:app --port <puerto> --reload
```
Y listo!

## Accediendo a la API
Una vez que levantemos el servidor, podemos acceder a la API a través de la URL devuelta por uvicorn, por ejemplo `http://127.0.0.1:8000` es la URL por defecto. FastAPI nos brinda una documentación detallada de la API gracias a [Swagger UI](https://github.com/swagger-api/swagger-ui). A esta documentación podemos acceder desde `http://127.0.0.1:8000/docs`.

## Uso de la API
Para usar la API podemos directamente ir a la documentacion (`/docs`) y ahi mismo comenzar a hacer requests.

Otra manera de usar la API es desde Postman haciendo requests a los endpoints especificados en la documentación.

Pero también podemos hacer requests desde cualquier entorno que lo permita (curl, JavaScript, etc).

## Testing
Para testear la aplicación, vamos a pararnos en el directorio principal (`switcher-api`) y vamos a ir al directorio `/test`:
```bash
(env) $ cd test
```
Luego, corremos los tests con el siguiente comando:
```bash
(env) $ pytest <archivo>.py
```
O para correr un test en específico:
```bash
(env) $ pytest <archivo>.py::<test-especifico>
```