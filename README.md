SmartCampus
Práctica de Despliegue y monitorización en la nube
Universidad Camilo José Cela
Autora: Ingrid Carvallhais Silva

SmartCampus es una aplicación académica de consulta de aulas y reservas. Consta de un frontend HTML, CSS y JavaScript servido por Nginx, una API REST FastAPI y una base de datos PostgreSQL. El repositorio permite desplegarla tanto con Docker Compose como con Kubernetes (Minikube).
1. Arquitectura
Navegador → Nginx (frontend) → FastAPI (backend) → PostgreSQL
                   /api/               SQL
En Docker Compose, los servicios se comunican mediante la red interna y los nombres backend y database. En Kubernetes, utilizan Services; PostgreSQL se ejecuta mediante StatefulSet con almacenamiento persistente.
2. Requisitos previos
- Git (opcional si se descarga el ZIP).
- Docker Desktop con Docker Compose.
- PowerShell en Windows (los ejemplos están escritos para este entorno).
- Para Kubernetes: kubectl y Minikube con el controlador Docker.
3. Ejecución con Docker Compose
Abrir PowerShell en la raíz del repositorio, donde se encuentra docker-compose.yml.

3.1. Configurar las variables locales
Copy-Item .env.example .env
Revisar los valores de .env, especialmente POSTGRES_DB, POSTGRES_USER y POSTGRES_PASSWORD. No publicar el archivo .env ni usar las credenciales de ejemplo en un entorno expuesto a Internet.

3.2. Construir y arrancar
docker compose config
docker compose up -d --build
docker compose ps
Esperar a que los tres servicios aparezcan como healthy; el frontend puede mostrar temporalmente health: starting mientras arranca.

3.3. Acceder a la aplicación
- Frontend: http://localhost:8080
- Documentación interactiva FastAPI: http://localhost:8000/docs
- Comprobación de salud: http://localhost:8000/health
3.4. Probar los endpoints
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/rooms
Invoke-RestMethod http://localhost:8000/rooms/1
Invoke-RestMethod http://localhost:8000/bookings
Método y ruta	Función
GET /health	Estado de la API
GET /rooms	Listado de aulas
GET /rooms/{id}	Información de un aula; devuelve 404 si no existe
GET /bookings	Listado de reservas


La ruta /rooms/1 se ha comprobado con el aula Aula Magna en el entorno de práctica.

3.5. Detener y recuperar servicios
docker compose stop backend
docker compose ps -a
docker compose start backend
docker compose ps
Para detener todo el entorno sin eliminar el volumen de PostgreSQL:
docker compose down
Importante: no ejecutar docker compose down -v si se quieren conservar los datos; -v elimina los volúmenes administrados por Compose.
4. Despliegue con Kubernetes (Minikube)
Los manifiestos se encuentran en k8s/. La explicación detallada de credenciales, imágenes, orden de aplicación y almacenamiento está en [README.md](k8s/README.md).

4.1. Iniciar el clúster
minikube start --driver=docker
kubectl config current-context
4.2. Construir y cargar las imágenes locales
docker compose build
minikube image load smartcampus-backend:latest
minikube image load smartcampus-frontend:latest
minikube image load postgres:16-alpine
Los manifiestos de la aplicación utilizan imágenes locales; si se reconstruyen, es necesario volver a cargarlas en Minikube antes de actualizar los Pods.

4.3. Preparar el Secret
Copy-Item k8s\secret.example.yaml.template k8s\secret.yaml
Editar k8s\secret.yaml y sustituir todos los marcadores REPLACE_WITH_.... Mantener el mismo usuario y contraseña en POSTGRES_USER, POSTGRES_PASSWORD y DATABASE_URL. Utilizar una contraseña compatible con URL. No subir k8s/secret.yaml a GitHub.

4.4. Aplicar los manifiestos en orden
kubectl apply -f k8s\00-namespace.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\01-configmap.yaml
kubectl apply -f k8s\02-nginx-configmap.yaml
kubectl apply -f k8s\10-postgresql.yaml
kubectl apply -f k8s\20-backend.yaml
kubectl apply -f k8s\30-frontend.yaml
4.5. Verificar el despliegue
kubectl get pods,deployments,services -n smartcampus
kubectl get statefulsets,pvc -n smartcampus
La configuración prevista incluye 2 réplicas del backend, 1 del frontend, 1 StatefulSet PostgreSQL, Services internos y un PVC de 1 GiB.

4.6. Abrir el frontend
minikube service smartcampus-frontend -n smartcampus --url
Abrir en el navegador la URL indicada. En Windows con el driver Docker puede ser necesario mantener abierta la ventana de PowerShell que proporciona el acceso.
5. Pruebas de orquestación
Escalado horizontal del backend:
kubectl scale deployment backend --replicas=4 -n smartcampus
kubectl get pods -n smartcampus
kubectl scale deployment backend --replicas=2 -n smartcampus
kubectl get pods -n smartcampus
Recuperación automática (self-healing): consultar los Pods con kubectl get pods -n smartcampus, eliminar manualmente uno de los Pods del backend con kubectl delete pod NOMBRE_DEL_POD -n smartcampus y volver a consultar para observar cómo el Deployment crea un sustituto. Reemplazar NOMBRE_DEL_POD por un nombre real obtenido en el comando anterior.

ConfigMap: el backend lee APP_ENV desde smartcampus-config. Tras cambiar su valor, reiniciar controladamente el Deployment para que los nuevos Pods reciban las variables de entorno:
kubectl rollout restart deployment/backend -n smartcampus
kubectl rollout status deployment/backend -n smartcampus
kubectl exec -n smartcampus deployment/backend -- printenv APP_ENV
Persistencia: PostgreSQL usa un PVC. Recrear su Pod conservando el PVC permite comprobar que las reservas continúan disponibles. Esta prueba no sustituye a una copia de seguridad y puede producir un error transitorio de conexión mientras PostgreSQL reinicia.
6. Estructura del repositorio
SmartCampus/
├── backend/                 # API FastAPI, dependencias y pruebas
├── database/init/init.sql   # Datos iniciales PostgreSQL
├── frontend/                # Nginx e interfaz web
├── k8s/                     # Manifiestos y guía Kubernetes
├── .env.example             # Plantilla de variables para Compose
├── docker-compose.yml      # Servicios locales
└── README.md                # Esta guía
7. Seguridad y consideraciones
- .env y k8s/secret.yaml deben mantenerse fuera del repositorio público.
- Los Secrets de Kubernetes requieren medidas adicionales de protección y control de acceso; no equivalen por sí solos a cifrado seguro en reposo.
- El volumen de Docker y el PVC de Kubernetes son independientes. No comparten automáticamente los datos.
- Las pruebas se han realizado en un entorno local; no demuestran alta disponibilidad multinodo ni preparación para producción.
