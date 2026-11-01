# Despliegue de SmartCampus en Kubernetes

Estos manifiestos son independientes de Docker Compose. Compose conserva sus
nombres de host `database` y `backend`; en Kubernetes, el backend usa el Service
DNS `postgresql` y Nginx reenvía `/api/` al Service DNS `backend`. La
configuración de Nginx para Kubernetes está en un ConfigMap montado sobre el
archivo de configuración del contenedor, por lo que `frontend/nginx.conf` no se
modifica.

## Credenciales

No guardes credenciales reales en Git. Copia
`secret.example.yaml.template` a `secret.yaml` y sustituye los marcadores por
credenciales propias:

```powershell
Copy-Item k8s\secret.example.yaml.template k8s\secret.yaml
```

`k8s\secret.yaml` está excluido de Git. Usa el mismo usuario y contraseña en
`POSTGRES_USER`, `POSTGRES_PASSWORD` y `DATABASE_URL`. Para evitar errores en
la URL de SQLAlchemy, elige una contraseña con caracteres URL-safe (por
ejemplo, letras, números, guion y guion bajo). No apliques el archivo de ejemplo
sin editarlo: sus valores son marcadores.

Kubernetes Secret evita incluir los valores en los manifiestos de la aplicación,
pero no cifra por sí mismo los datos del clúster ni convierte Git en un almacén
seguro. No compartas ni confirmes `secret.yaml`.

## Imágenes locales

Los manifiestos usan las imágenes locales ya disponibles:
`smartcampus-backend:latest`, `smartcampus-frontend:latest` y
`postgres:16-alpine`. Cárgalas en Minikube antes de crear los Deployments.
`imagePullPolicy: Never` impide que Kubernetes intente descargar las imágenes
de la aplicación de un registro:

```powershell
minikube image load smartcampus-backend:latest
minikube image load smartcampus-frontend:latest
minikube image load postgres:16-alpine
```

Si reconstruyes alguna imagen de la aplicación, vuelve a cargar esa misma
etiqueta en Minikube antes de actualizar sus Pods.

## Orden y almacenamiento

Una vez autorizada la aplicación al clúster, crea primero el namespace y el
Secret, y después aplica los demás manifiestos:

```powershell
kubectl apply -f k8s\00-namespace.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\01-configmap.yaml
kubectl apply -f k8s\02-nginx-configmap.yaml
kubectl apply -f k8s\10-postgresql.yaml
kubectl apply -f k8s\20-backend.yaml
kubectl apply -f k8s\30-frontend.yaml
```

PostgreSQL es un StatefulSet de una réplica porque necesita identidad estable y
almacenamiento persistente: `volumeClaimTemplates` crea un PVC dedicado que
mantiene sus datos aunque el Pod se recree. El volumen es nuevo y separado del
volumen de Compose; estos manifiestos no borran ni reemplazan volúmenes
existentes. El script `init.sql` se monta como ConfigMap en
`/docker-entrypoint-initdb.d/10-init.sql`; la imagen oficial lo ejecuta al crear
una base en un directorio de datos vacío. No se vuelve a ejecutar
automáticamente si el PVC ya contiene datos.

Cada Pod del backend espera en su init container a que PostgreSQL acepte
conexiones. La imagen oficial completa `init.sql` antes de iniciar el servidor
PostgreSQL normal, así que el backend no comienza antes de terminar esa
inicialización. Las sondas de disponibilidad y salud comprueban PostgreSQL,
FastAPI (`/health`) y Nginx (`/`).

El Service `smartcampus-frontend` expone Nginx mediante NodePort `30080`; tras
el despliegue puede obtenerse la URL con:

```powershell
minikube service smartcampus-frontend -n smartcampus --url
```
