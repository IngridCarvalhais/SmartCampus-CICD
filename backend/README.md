# Backend de SmartCampus

API REST desarrollada con FastAPI, SQLAlchemy y PostgreSQL. Las tablas `rooms` y `bookings` se crean automáticamente al iniciar la aplicación, sin Alembic.

## Configuración

Define `DATABASE_URL` en el entorno antes de iniciar la API. El formato recomendado con el controlador incluido es:

```text
postgresql+psycopg://USUARIO:CONTRASENA@HOST:5432/BASE_DE_DATOS
```

Los valores anteriores son marcadores de posición; no guardes credenciales reales en el código ni en el repositorio.

## Ejecución y pruebas

Desde esta carpeta, instala las dependencias con `pip install -r requirements.txt`. Inicia la API con `uvicorn app.main:app --reload` y ejecuta las pruebas con `pytest`.

Las pruebas configuran SQLite en memoria para no requerir una instancia de PostgreSQL.

## Endpoints

- `GET /health`
- `GET /rooms`
- `GET /rooms/{id}`
- `GET /bookings`
