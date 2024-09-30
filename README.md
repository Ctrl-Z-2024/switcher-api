# El Switcher - API REST
API del juego de mesa "El Switcher" implementada con FastAPI.

## Requisitos previos
Antes de comenzar, asegúrate de tener **Python** instalado. Puedes seguir la [documentación oficial de Python](https://www.python.org/) para la instalación. Además, es recomendable crear un entorno virtual para gestionar las dependencias del proyecto.

## Instalación

Clona el repositorio y navega al directorio del proyecto:

```bash
$ git clone https://github.com/Ctrl-Z-2024/switcher-api.git
$ cd switcher-api
```

### Configuración del entorno virtual
Activa tu entorno virtual y luego instala las librerías necesarias:
```bash
(env) $ pip install -r requirements.txt
```
Una vez hecho esto, tendrás todas las dependencias instaladas para ejecutar la aplicación.

## Ejecutar la aplicación
Para ejecutar la API, navega al directorio app/ y ejecuta el servidor con FastAPI CLI:

```bash
(env) $ cd app
(env) $ fastapi run main.py
```

Esto iniciará el servidor. Si quieres especificar un puerto, puedes agregar `--port <numero de puerto>`.

Si quieres iniciar el servidor en modo desarrollo, deberás ejecutarlo de la siguiente manera:
```bash
(env) $ fastapi dev main.py
```

## Acceso a la API
Una vez que el servidor esté corriendo, puedes acceder a la API a través de la URL mostrada en la consola, por defecto será `http://0.0.0.0:8000`.

FastAPI proporciona una documentación interactiva a través de [Swagger UI](https://swagger.io/tools/swagger-ui/), accesible en:
```php
http://<direccion>:<puerto>/docs
```

## Uso de la API
Puedes utilizar la API directamente desde la interfaz de Swagger UI o enviar solicitudes desde herramientas como **Postman**, **curl** o desde cualquier lenguaje que soporte HTTP.

Enlace a Google Sheets con la [definición de la API](https://docs.google.com/spreadsheets/d/19sXUdj81GLNWPH86Uja328Gk27BWLL2Hj1xli5Ad8ss/edit?usp=sharing).


## Testing
Para ejecutar los tests, ubícate en el directorio principal del proyecto (`switcher-api`) y navega al directorio `/test`:
```bash
(env) $ cd test
```
Luego, ejecuta los tests con el siguiente comando:
```bash
(env) $ pytest <archivo>.py
```
Para ejecutar un test específico:
```bash
(env) $ pytest <archivo>.py::<test-especifico>
```
