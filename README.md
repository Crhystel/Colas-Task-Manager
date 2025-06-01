## Este sistema permite la gestión de tareas

- Los **admins** crean usuarios, envían tareas, proyectos o anuncios.
- Los **profesores** asignan tareas a estudiantes.
- Los **estudiantes** ven sus tareas y pueden enviar mensajes a cualquier usuario.
- El sistema persiste tareas y logs en archivos locales.

### Debes tener instalado
- Docker y Docker Compose
- Python

### Levantar RabbitMQ
- Para inciar el servicio debes ir a Docker Desktop
- En terminal ir a la ubicación del proyecto
- Una vez dentro del directorio ejecutar:
    docker compose up -d
- Esperar un rato y abrir la interfaz, con la configuración de docker-compose.yml la interfaz debe abrir con:
    http://localhost:15672

### La aplicación se ejecuta en main
## Cambios Realizados
- Ahora los exchange direct los recibe y envia Microsoft Azure, se activan cuando alguien asigna un deber y cuando el estudiante envia un mensaje a un usuario
- Existen "logs" que muestran las tareas o mensajes enviados a diferentes usuarios para comprobar que funcionan las colas, estos funcionan tanto para RabbitMQ como para los exchange de Azure
- Nota: los mensajes se demoran un minuto en ser consumidos por los usuarios destinatarios, pero funcionan