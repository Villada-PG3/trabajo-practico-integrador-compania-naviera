# 🛳️ Compañía Naviera SEA STAR — Guía de Instalación

## 📘 Introducción

La *Compañía Naviera SEA STAR* se dedica a la realización de cruceros y cuenta con una flota de navíos que ofrecen distintos niveles de lujo y capacidad.
El sistema desarrollado permite gestionar navíos, cubiertas, camarotes, tripulación, itinerarios, viajes y pasajeros, manteniendo toda la información organizada y accesible.

El proyecto está desarrollado con *Django, utiliza **SQLite* como base de datos por defecto y el tema *Unfold* para personalizar el panel de administración.

---

## ⚙️ 1. Requisitos previos

Antes de comenzar, asegurate de tener instalado:

* *Python 3.10+*
* *Git*
* *Pip* (incluido con Python)
* *Virtualenv* (opcional, pero recomendado)

---

## 🐍 2. Clonar el repositorio

bash
git clone https://github.com/Villada-PG3/trabajo-practico-integrador-compania-naviera.git
cd trabajo-practico-integrador-compania-naviera


---

## 🧩 3. Crear y activar entorno virtual

### En Windows:

bash
python -m venv venv
venv\Scripts\activate


### En Linux/Mac:

bash
python3 -m venv venv
source venv/bin/activate


---

## 📦 4. Instalar dependencias

bash
pip install -r requirements.txt


> Para asegurarte de que requirements.txt tenga todas las librerías instaladas, podés actualizarlo con:
>
> bash
> pip freeze > requirements.txt
> 

---

## 🚀 5. Crear y aplicar migraciones

Ejecutá los siguientes comandos para crear las tablas en la base de datos:

bash
python manage.py makemigrations
python manage.py migrate


> ⚠️ La base de datos estará vacía hasta que se agreguen datos.

---

## 📂 6. Cargar datos iniciales desde data.json

Si querés poblar la base de datos con datos de ejemplo, podés usar el fixture data.json incluido en el proyecto:

bash
python manage.py loaddata data.json


> Esto agregará los registros de navíos, cubiertas, camarotes, tripulación, itinerarios, viajes y pasajeros a la base de datos.

---

## 🧑‍💻 7. Crear un superusuario

Para acceder al panel de administración y agregar datos manualmente:

bash
python manage.py createsuperuser


Ingresá los datos solicitados.

---

## ▶️ 8. Ejecutar el servidor

bash
python manage.py runserver


Luego abrí tu navegador y accedé a:


http://127.0.0.1:8000/


---

## 👥 Autores

Proyecto desarrollado por el equipo de *Villada PG3*,
como parte del *Trabajo Práctico Integrador — Compañía Naviera SEA STAR*.