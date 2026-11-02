# Backend SmartCampus

API REST con FastAPI, SQLAlchemy y Pydantic. SQLite es la base de datos
predeterminada para desarrollo local y pruebas; también se admite PostgreSQL
mediante `DATABASE_URL` y el controlador `psycopg`. Las tablas se crean al
iniciar la aplicación.

Desde esta carpeta, crea un entorno virtual, instala las dependencias de
desarrollo y arranca la API:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:DATABASE_URL = "sqlite+pysqlite:///./smartcampus.db"
python -m uvicorn app.main:app --reload
```

Valida el código con `python -m ruff check app tests`,
`python -m ruff format --check app tests` y `python -m pytest -q`. Las pruebas
usan una base SQLite en memoria aislada de la base local.

Endpoints: `GET /health`, `GET /rooms`, `GET /rooms/{id}`, `POST /rooms`,
`DELETE /rooms/{id}`, `GET /bookings`, `POST /bookings` y
`DELETE /bookings/{id}`. La referencia de estados, Docker y GitHub Actions está
en el [README del proyecto](../README.md).
