# Sistema de base de datos phyton
proyecto de Alexander Morales Quiroz como proyecto final de mi clase de base de datos



# contenido:
- [Descripción general](#descripcion-general)
- [Características principales](#caracteristicas-principales)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Roles Y autetificacion](#roles-y-autentificacion)
- [Interfaz](#interfaz)
- [Desafios/Soluciones](#Desafios/Soluciones)
- [Como ejecutar](#Como-ejecutar)
- [Capturas](#capturas)
- [Conclusion](#Conclusion)

# Descripcion:
este programa funciona como una interfaz grafica para un inventario usando phyton como lenguaje en respuesta a los problemas que se me dieron
el proyecto implemento las librerias de CustomTikner, Sqlite y phyton

# Caracteristicas:
- Capacidad de logear con diferetes credenciales para evitar problemas con las bases de datos con personas que no deberian estar ahi, crear,editar,eliminar o consultar datos en la base de datos de manera sencilla
- Filtros para buscar la informacion en la base de datos
- Diferentes usuarios (Admin, Productos, Almacen)
- Interfaz facil de entender

# Arquitectura del proyecto:
el sistema esta basado en diferentes clases 
- Main: funciona para abrir el programa y enciende directamente el login
- Login: es el que verifica los usuarios y contraseñas para las credenciales
- Menu principal: es el menu que conecta las dos tablas de la base de datos, no tiene funcionalidad extra
- Productos: funciona como interfaz grafica a la tabla de productos con el crud funcional
- Almacen: funciona como interfaz grafica a la tabla de almacen con el crud funcional

# Base de Datos:
- Usuarios: esta es la tabla que contiene los usuarios y sus contrañas
- Almacenes: contiene la id y el nombre del almacen
