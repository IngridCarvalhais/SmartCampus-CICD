# SmartCampus

Práctica universitaria **Automatización y Despliegue de una aplicación con Git
Hooks y GitHub Actions**, de la asignatura Despliegue y Monitorización en la
Nube. SmartCampus permite consultar aulas y gestionar sus reservas mediante
una API REST.

## Arquitectura

```text
Navegador → Nginx (frontend) → FastAPI (backend) → SQLAlchemy → SQLite/PostgreSQL
                   /api/                 /health
```

- `backend/`: API FastAPI, modelos SQLAlchemy, esquemas Pydantic y pruebas
  unitarias y de integración.
- `frontend/`: interfaz HTML, CSS y JavaScript servida por Nginx. Nginx reenvía
  `/api/` al backend.
- `docker-compose.yml`: red interna, volúmenes persistentes y servicios locales.
- `githooks/`: hooks versionados de Git.
- `.github/workflows/ci-cd.yml`: lint, pruebas, construcción y verificación de
  Docker; el despliegue persistente es opcional y permanece desactivado.
- `k8s/`: manifiestos de Kubernetes existentes; su guía está en
  [k8s/README.md](k8s/README.md).

## Tecnologías

Python 3.11/3.12, FastAPI, Pydantic, SQLAlchemy 2, SQLite, PostgreSQL con
`psycopg`, pytest, Ruff, Docker, Docker Compose, Nginx y GitHub Actions.

## Requisitos

- Windows 10/11, PowerShell y Git for Windows.
- Python 3.11 o 3.12.
- Docker Desktop con Docker Compose v2 para el entorno en contenedores.
- GitHub Actions requiere acceso al repositorio. El despliegue requiere además
  un servidor Linux persistente autorizado, Docker Compose y un runner
  self-hosted.

## Instalación y ejecución local en Windows

Desde PowerShell, en la raíz de este proyecto:

```powershell
Set-Location .\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:DATABASE_URL = "sqlite+pysqlite:///./smartcampus.db"
python -m uvicorn app.main:app --reload
```

La API estará disponible en <http://127.0.0.1:8000>. Si no se define
`DATABASE_URL`, el backend utiliza `sqlite+pysqlite:///./smartcampus.db` en el
directorio actual. Las tablas se crean al iniciar la aplicación. Para usar
Python 3.12, sustituye `py -3.11` por `py -3.12`.

El archivo de base de datos local está excluido de Git. Para PostgreSQL se
puede definir `DATABASE_URL` con una URL compatible con SQLAlchemy y el
controlador `psycopg`.

## API REST

| Método | Ruta | Resultado |
|---|---|---|
| `GET` | `/health` | Comprueba que la API y la base de datos responden |
| `GET` | `/rooms` | Lista las aulas |
| `GET` | `/rooms/{id}` | Consulta un aula |
| `POST` | `/rooms` | Crea un aula; devuelve `201` |
| `DELETE` | `/rooms/{id}` | Elimina un aula; devuelve `204` |
| `GET` | `/bookings` | Lista las reservas |
| `POST` | `/bookings` | Crea una reserva; devuelve `201` |
| `DELETE` | `/bookings/{id}` | Elimina una reserva; devuelve `204` |

Un aula incluye `id`, `nombre`, `edificio`, `capacidad` y `equipamiento`. Una
reserva incluye `id`, `aula_id`, `usuario`, `fecha`, `hora_inicio` y `hora_fin`.

Las capacidades deben ser positivas y el inicio de una reserva debe ser
anterior a su fin (`422` si los datos no son válidos). No se puede reservar un
aula inexistente (`404`). Las reservas que se solapan para una misma aula y
fecha devuelven `409`; las reservas consecutivas sí se aceptan. Eliminar un
aula o una reserva inexistente devuelve `404`. Si un aula tiene reservas, su
eliminación se rechaza con `409` para conservarlas y evitar errores de clave
foránea; primero hay que eliminar sus reservas.

Ejemplos en PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/rooms

$room = @{
    nombre = "Aula 101"
    edificio = "Edificio A"
    capacidad = 30
    equipamiento = @("proyector", "pizarra")
} | ConvertTo-Json
$createdRoom = Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:8000/rooms `
    -ContentType "application/json" -Body $room

$booking = @{
    aula_id = $createdRoom.id
    usuario = "estudiante"
    fecha = "2026-11-15"
    hora_inicio = "09:00"
    hora_fin = "10:00"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/bookings `
    -ContentType "application/json" -Body $booking
```

La documentación interactiva está en `/docs`.

## Pruebas y calidad

Las pruebas usan SQLite en memoria y sustituyen `DATABASE_URL` antes de
importar la aplicación; no leen ni modifican la base de datos local.

```powershell
Set-Location .\backend
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
```

`test_schemas.py` comprueba reglas de validación y el resto de la suite verifica
los endpoints con `TestClient`. Los mismos comandos se ejecutan localmente, en
los hooks y en GitHub Actions.

## Git Hooks

Los hooks están versionados en `githooks/`; su activación es explícita. Desde la
raíz del repositorio, después de instalar las dependencias de desarrollo:

```powershell
git config core.hooksPath githooks
```

Al preparar los hooks para un commit en un sistema Unix, conserva el permiso de
ejecución en el índice:

```powershell
git add --chmod=+x githooks/validate.sh githooks/pre-commit `
    githooks/pre-push githooks/post-commit scripts/git-push.sh
```

- `pre-commit`: lint, formato y toda la suite; bloquea el commit si falla una
  comprobación.
- `post-commit`: añade autor, fecha ISO, hash y asunto del commit a
  `commit-log.txt`, que es local y está excluido de Git.
- `pre-push`: ejecuta las pruebas unitarias y de integración y bloquea el push
  si fallan.
- Git no proporciona un hook nativo `post-push`. Para mostrar el mensaje solo
  después de un push exitoso, usa uno de estos envoltorios en lugar de `git
  push`:

```powershell
.\scripts\git-push.ps1 origin main
```

En Git Bash:

```bash
bash scripts/git-push.sh origin main
```

Los envoltorios delegan en `git push`, conservan su código de salida y solo
muestran el mensaje de éxito si el push termina correctamente. No se activan
hooks ni se realizan commits o pushes automáticamente.

## Docker y Docker Compose

El modo predeterminado usa SQLite dentro del volumen persistente `sqlite-data`;
el frontend existente se conserva y PostgreSQL se ofrece como perfil opcional.
Desde la raíz del proyecto:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
docker compose config
docker compose up -d --build
docker compose ps
```

La API se publica en `http://localhost:8000` y el frontend en
`http://localhost:8080`. Cambia `API_PORT` o `FRONTEND_PORT` en `.env` si esos
puertos están ocupados. El healthcheck consulta `GET /health`, que verifica
también la conexión a la base de datos. El frontend espera a que el backend
esté saludable.

Para usar PostgreSQL con el servicio Compose opcional, configura en `.env` una
contraseña local propia, `POSTGRES_DB`, `POSTGRES_USER` y `DATABASE_URL` con
formato `postgresql+psycopg://usuario:contraseña@database:5432/base_de_datos`.
Codifica los caracteres reservados de la contraseña para URL. Inicia primero
la base de datos y espera su estado saludable; después inicia la aplicación:

```powershell
docker compose --profile postgres up -d database
docker compose --profile postgres ps
docker compose up -d --build backend frontend
```

No uses las credenciales de ejemplo en un entorno compartido o expuesto. `.env`
no se versiona. `docker compose down` conserva los volúmenes; no ejecutes
`docker compose down -v` si necesitas conservar los datos.

## GitHub Actions, matrix, Secrets y despliegue

El workflow se encuentra en `.github/workflows/ci-cd.yml` y se activa con eventos `push` y `pull_request`. El pipeline realiza checkout, instalación de dependencias, comprobaciones de calidad con Ruff, pruebas con pytest, validación de Docker Compose, construcción de imágenes y verificación de ejecución. La matriz de pruebas cubre **Python 3.11 y 3.12**.

### Variables y secretos

Los parámetros locales se documentan en `.env.example`; el archivo `.env` real está excluido mediante `.gitignore`. GitHub Actions utiliza el token proporcionado por GitHub (`GITHUB_TOKEN`) para una operación autenticada de solo lectura y el Secret del repositorio `DATABASE_URL` en el trabajo de despliegue. **Nunca** se imprimen valores de secretos en logs ni se incorporan al código. La URL SQLite utilizada como valor de prueba no es una credencial sensible; en un despliegue real debería emplearse un secreto que contenga credenciales auténticas, cuando corresponda.

### Despliegue automático temporal

En la rama `feat/deploy-automatico` se preparó un cambio del trabajo `deploy` para ejecutarse **únicamente en pushes a `main`**, después de que terminen correctamente `tests` y `docker`. La versión modificada usa `ubuntu-latest`, construye y arranca backend y frontend mediante `docker compose up --detach --build --wait`, verifica las rutas `/health`, `/rooms` y `/`, guarda logs como artefacto y finalmente detiene los contenedores. Emplea los puertos `18000` (API) y `18080` (frontend).

**Estado de verificación:** el push de la rama pasó 24 tests localmente y el Pull Request mostró 8/8 comprobaciones correctas. No se afirma aquí que el trabajo `deploy` haya terminado correctamente en `main`: debe comprobarse en la pestaña **Actions** después de fusionar el Pull Request.

**Limitación importante del enunciado:** los contenedores iniciados en un runner temporal de GitHub desaparecen al terminar el trabajo. Por ello, este mecanismo valida la automatización, pero **no constituye un despliegue persistente**. Para cumplir esa exigencia se necesita un runner `self-hosted` en un equipo servidor, una VM por SSH u otro mecanismo autorizado expresamente por el profesor. No se ha acreditado un despliegue persistente.

### Cómo comprobar el pipeline

1. Abrir **GitHub → Pull requests** y comprobar que los trabajos obligatorios del PR estén correctos.
2. Fusionar el PR en `main` solo si las comprobaciones requeridas han pasado.
3. Abrir **GitHub → Actions**, seleccionar la ejecución de `main` y revisar `tests`, `docker` y `deploy`.
4. En `deploy`, revisar la salida de los comandos `curl`, el estado de los contenedores y el artefacto `smartcampus-deploy-logs`.
5. Si falla un trabajo, consultar sus logs antes de declarar el despliegue completado.

## Flujo de trabajo con Git y Pull Requests

El desarrollo se organiza en ramas y commits descriptivos. La rama `feat/deploy-automatico` contiene la mejora del pipeline y se integrará en `main` mediante un Pull Request tras pasar las comprobaciones. El uso de ramas y Pull Requests forma parte de las buenas prácticas valoradas por el enunciado.

Ejemplos de comandos:

```powershell
git status
git checkout -b feat/nueva-funcionalidad
git add .
git commit -m "feat: añadir funcionalidad"
# Ejecutar push solo después de revisar los cambios:
git push -u origin feat/nueva-funcionalidad
```

## Kubernetes existente

Los manifiestos de PostgreSQL, backend y frontend se conservan en `k8s/`. La
guía existente, el almacenamiento persistente, el Secret de ejemplo y los
comandos de Minikube están en [k8s/README.md](k8s/README.md). No se ha aplicado
ningún manifiesto ni realizado un despliegue.

## Solución de problemas

- **`DATABASE_URL` no conecta:** comprueba el formato SQLAlchemy y, para
  PostgreSQL, que el servicio o servidor exista y que la contraseña esté
  codificada para URL.
- **Puerto ocupado:** cambia `API_PORT` o `FRONTEND_PORT` en `.env` y recrea los
  servicios con `docker compose up -d`.
- **El aula no se puede eliminar (`409`):** elimina antes sus reservas.
- **Ruff no está instalado:** activa el entorno virtual y ejecuta
  `python -m pip install -r backend/requirements-dev.txt` desde la raíz.
- **Docker no responde:** inicia Docker Desktop y comprueba
  `docker compose version`.
- **Un push/commit falla en un hook:** revisa primero la salida de Ruff o pytest;
  no se debe omitir el hook para ocultar un fallo.
- **El job de despliegue aparece omitido:** es lo esperado mientras
  `DEPLOY_ENABLED` no sea `true` o no se cumplan las condiciones del runner y
  del entorno protegido.

## Evidencias para la entrega

Guarda capturas propias de:

1. `python --version`, los comandos Ruff y el resultado final de pytest.
2. Swagger `/docs` y una consulta correcta a `/health`.
3. Creación/listado de un aula y de una reserva desde la API.
4. Respuestas `422`, `404` y `409`, incluyendo una reserva solapada y la
   eliminación protegida de un aula con reservas.
5. `docker compose ps` con los servicios saludables y el frontend abierto.
6. La configuración de hooks (`git config --get core.hooksPath`) y su salida en
   una demostración controlada; no crees commits o pushes reales sin revisar
   antes el alcance.
7. El resumen de un run real de GitHub Actions, después de ejecutarlo en
   GitHub; no se debe presentar una ejecución local como resultado del workflow.
8. El trabajo `deploy` en Actions (si se ejecuta en `main`), sus verificaciones HTTP y los logs; distinguirlo de un despliegue persistente.
9. El Pull Request con sus comprobaciones aprobadas y la fusión en `main`.
10. La configuración de GitHub Secrets mostrando únicamente los nombres, nunca los valores.
