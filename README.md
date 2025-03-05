# README - Correr la Aplicación en Docker

## Requisitos del sistema
Para ejecutar esta aplicación en Docker, es necesario que tu máquina cumpla con los siguientes requisitos:

- **Sistema Operativo**: Windows, macOS o Linux.
- **RAM**: Al menos **32GB** de memoria RAM.
- **Docker**: Instalado y configurado correctamente.
- **Docker Compose**: Instalado (Docker Desktop ya lo incluye en versiones recientes).

## Instalación de Docker y Docker Compose
Si aún no tienes Docker y Docker Compose instalados, sigue estas instrucciones:

### Windows y macOS
1. Descarga e instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Verifica la instalación ejecutando:
   ```sh
   docker --version
   docker-compose --version
   ```

### Linux
1. Instala Docker:
   ```sh
   sudo apt update
   sudo apt install -y docker.io
   ```
2. Instala Docker Compose:
   ```sh
   sudo apt install -y docker-compose
   ```
3. Verifica la instalación:
   ```sh
   docker --version
   docker-compose --version
   ```
   
## Cómo Ejecutar la Aplicación
Para correr la aplicación en Docker, sigue estos pasos:

1. Asegúrate de estar en la carpeta del proyecto donde se encuentra el archivo `docker-compose.yml`.
2. Ejecuta el siguiente comando para construir y correr los contenedores:
   ```sh
   docker-compose up --build
   ```
3. Espera a que los servicios se inicien correctamente.
4. La aplicación estará disponible en `http://localhost:3000`.

## Detener y Limpiar Contenedores
Para detener la aplicación, usa:
```sh
docker-compose down
```
Si deseas eliminar los volúmenes y limpiar completamente los contenedores:
```sh
docker-compose down -v
```

## Solución de Problemas
Si experimentas problemas, considera lo siguiente:
- Verifica que Docker esté corriendo con `docker ps`.
- Asegúrate de tener suficiente memoria disponible (al menos 32GB de RAM).
- Revisa los logs con:
  ```sh
  docker-compose logs
  ```
- Si necesitas reconstruir completamente las imágenes, usa:
  ```sh
  docker-compose up --build --force-recreate
  ```
