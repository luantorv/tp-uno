# Trabajo Práctico Nº1 de Estadística y Exploración de Datos

## Alumnos:

- Maidana, Jonatan
- Reis Viera, Luis Antonio

## Árbol del Proyecto

El proyecto se dividió en dos carpetas `src` y `file`. En `src` se encuentran todos los archivos Python que se encargan de la lógica del proyecto; y en `file` se guardó al archivo `.csv` que fué analizado para el desarrollo del trabajo.

De ésta forma nos queda el siguiente árbol de carpetas:

```
/
|   file/
|   |   Covid19Casos.csv
|   src/
|   |   answer.py
|   |   db.py
|   |   main.py
|   |   tools.py
|   README.md
```

Donde:

Como habíamos mencionado `Covid19Casos.csv` es el archivo sobre el cuál se ha basado este proyecto.

`answer.py` es un archivo auxiliar que se ha utilizado como módulo, y en el cuál se han escrito las funciones y procedimientos destinados a la lógica de negocio, al análisis y tratamientos o modificaciones que se vayan haciendo para poder contestar las preguntas debidamente.

`db.py` es el módulo que contiene todas las funciones y procedimientos destinados al manejo de la base de datos `SQLite3`.

El archivo `main.py` es el archivo principal del programa, y el que se encarga del control del flujo, a través de un menú con opciones que se maneja desde la consola.

`tools.py` es un módulo con funciones muy útiles, pero que fueron separadas del archivo principal por prolijidad y para que sea más reutilizable a futuro.

Y el `README.md` es el archivo que usted está leyendo ahora mismo, siendo la documentación del presente proyecto.

## Créditos

Este proyecto es/fue realizado en el contexto de la matería __Estadística y Exploración de Datos__ de la __Tecnicatura Superior en Ciencia de Datos e Inteligencia Artificial__ del __Instituto Superior de Formación Docente y Técnica__ de Posadas, Misiones, Argentina.

> Para más información: `https://web.esim.edu.ar/`
