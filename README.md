Requisitos previos:
1. Tener apache instalado en el servidor con PHP 8.1
2. Tener instalado composer para instalacion de dependencias.
3. Tener instalado de SQL SERVER 2019 con el protocolo TCP activo para comunicación externa.
4. El PHP debe tener instalados las extensiones para conexion del php a SQL SERVER.

Descarga del repositorio:
1. Clonar el repositorio en la carpeta publica del apache
2. Ingresar a la carpeta del repositoria clonado.
3. Ejecutar "composer install"
4. Configurar archivo .env con los datos de conexion a la base de datos
5. Ejecutar "php artisan migrate"

