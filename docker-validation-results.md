# Historial de validación Docker Compose

## Validación anterior: 31-10-2026

Los resultados siguientes corresponden a la configuración anterior, en la que
PostgreSQL era obligatorio. Se conservan como histórico y no describen el modo
SQLite predeterminado añadido el 02-11-2026.

## Configuración

- `docker compose config`: correcto; se resolvieron los tres servicios, la red `smartcampus`, el volumen persistente y los puertos publicados.
- `docker compose build`: correcto; se construyeron `smartcampus-backend` y `smartcampus-frontend`.
- `docker compose up -d`: correcto; PostgreSQL ejecutó `database/init/init.sql` durante la inicialización del volumen vacío. Los registros muestran la creación de ambas tablas y `INSERT 0 5` / `INSERT 0 3`.
- `docker compose ps`: los servicios `database`, `backend` y `frontend` quedaron `healthy`.
- `docker compose restart`: correcto, sin borrar ni recrear el volumen.

## Endpoints y frontend

| Comprobación | Resultado |
|---|---|
| `GET http://localhost:8000/health` | HTTP 200, `{"status":"ok"}` |
| `GET http://localhost:8000/rooms` | HTTP 200, 5 registros |
| `GET http://localhost:8000/bookings` | HTTP 200, 3 registros |
| `GET http://localhost:8080/api/rooms` | HTTP 200, 5 registros; Nginx los reenvió a `/rooms` |
| `GET http://localhost:8080/api/bookings` | HTTP 200, 3 registros; Nginx los reenvió a `/bookings` |
| `http://localhost:8080/` | HTTP 200; página SmartCampus servida |
| `http://localhost:8080/css/styles.css` | HTTP 200 |
| `http://localhost:8080/js/app.js` | HTTP 200 |

La inspección de la página en el navegador confirmó 5 tarjetas de aulas, 3 de reservas y solicitudes a `/api/rooms` y `/api/bookings`.

## PostgreSQL y persistencia

Antes y después de `docker compose restart`, PostgreSQL devolvió:

```text
rooms=5
bookings=3
```

Los registros muestran que `init.sql` se ejecutó en la inicialización y que, al reiniciar, PostgreSQL detectó el clúster existente y omitió la inicialización. No se eliminó ningún volumen.

## Registros y observaciones

- FastAPI registró el inicio completo y respuestas HTTP 200 para los endpoints.
- Nginx registró HTTP 200 al servir la página y al atender ambas rutas `/api/`.
- PostgreSQL registró la creación de tablas e índices y la inserción de las filas iniciales.
- Durante `docker compose restart`, PostgreSQL cerró conexiones activas con el mensaje `terminating connection due to administrator command`; es el cierre esperado al reiniciar y no persistió como fallo. Los servicios volvieron a estado `healthy`.
- `initdb` mostró el aviso estándar de autenticación `trust` para conexiones locales dentro del contenedor.

## Credenciales

Se creó `.env` con credenciales exclusivamente locales de desarrollo. `.gitignore` excluye `.env`; no se copiaron sus valores en este informe.

## Validación actual: 02-11-2026

Entorno local: Docker 29.8.0 y Docker Compose v5.5.1. La configuración
predeterminada y el perfil opcional `postgres` pasaron `docker compose config
--quiet`. Se construyeron correctamente las imágenes de backend y frontend con
el `.dockerignore` activo.

Para no alterar los servicios que ya estaban ejecutándose en el equipo, la
prueba usó el proyecto Compose aislado `smartcampus-ci-validation`, SQLite y
los puertos locales `18800` y `18080`.

| Comprobación | Resultado observado |
|---|---|
| Construcción backend y frontend | Correcta |
| Healthcheck del backend (`GET /health`) | `healthy`; respuesta `{"status":"ok"}` |
| Healthcheck del frontend | `healthy` |
| Creación de aula y reserva | Correcta, HTTP `201` |
| Frontend | HTTP `200` |
| Persistencia SQLite | El aula y la reserva continuaron tras reiniciar el backend |
| Limpieza de la prueba | Los servicios aislados quedaron detenidos; se conservaron sus volúmenes |

No se ejecutó el perfil PostgreSQL ni se realizó ningún despliegue externo.
GitHub Actions tampoco se ha ejecutado desde este entorno.
