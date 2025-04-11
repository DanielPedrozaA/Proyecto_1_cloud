# README - Correr la Aplicación en CCP

## 1. Configuración Inicial

### Base de Datos
Se debe iniciar la instancia de **Cloud SQL** configurada y funcionando correctamente.

## 2. Despliegue de Máquinas Virtuales

Todas las máquinas virtuales (VMs) deben ser iniciadas antes de continuar. Estas ya cuentan con un script interno que inicia automáticamente los contenedores Docker necesarios para ejecutar cada componente.

Asegúrate de ejecutar todas estas VMs:

- **file-server**
- **front**
- **redis-server**
- **servidor-webos**
- **worker**

## 3. Creación de la Clave de API

Sigue estos pasos para generar y configurar la clave de API necesaria:

1. Ingresa a tu cuenta de GCP.
2. Navega a **APIs y servicios > Credenciales**.
3. Crea una nueva **Clave de API**.
4. Copia la clave generada.

## 4. Configuración del Worker

Desde tu terminal SSH en la VM del **worker**, ejecuta:

```bash
sudo su
cd ..
cd Proyecto/
cd Proyecto_1_cloud/
cd batch
nano .env
```

Dentro del archivo `.env`, busca la línea que inicia con:

```plaintext
GOOGLE_API_KEY=
```

Pega la clave generada anteriormente justo después del signo `=`.

Guarda y cierra el archivo  luego `Ctrl+X` si estás usando nano.

## 5. Finalización

Ahora la aplicación ya está lista para utilizarse. Puedes acceder a ella usando la **dirección IP externa de la VM del front** desde tu navegador web.


