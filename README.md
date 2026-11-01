# SmartCampus

Proyecto académico para la gestión de aulas y reservas mediante una aplicación web compuesta por un frontend desarrollado con HTML, CSS y JavaScript, un backend implementado con FastAPI y una base de datos PostgreSQL.

La aplicación ha sido desplegada y validada mediante **Docker Compose y Kubernetes (Minikube)**.

Durante la práctica se han realizado pruebas de funcionamiento de los servicios, persistencia de datos, escalado horizontal del backend, recuperación automática de Pods (*self-healing*) y gestión de configuración y credenciales mediante ConfigMaps y Secrets.

El repositorio incluye los archivos necesarios para el despliegue con Docker Compose y los manifiestos de Kubernetes en la carpeta `k8s/`.
