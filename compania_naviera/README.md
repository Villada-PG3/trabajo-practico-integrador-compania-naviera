# 🛳️ Proyecto Compañía Naviera SEA STAR

Este proyecto es una aplicación web desarrollada con Django que gestiona la información de la compañía naviera **SEA STAR**, incluyendo navíos, cubiertas, camarotes, tripulación, itinerarios, viajes y pasajeros.

---

## 📌 Requisitos del Sistema

- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux
- Base de datos: SQLite3

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Villada-PG3/trabajo-practico-integrador-compania-naviera.git
cd trabajo-practico-integrador-compania-naviera

### 2. Crear y activar el entorno virtual
## Windows
python -m venv venv
.\venv\Scripts\activate

## Linux
python3 -m venv venv
source venv/bin/activate

### 3. Instalar dependencias
pip install -r requirements.txt

### 4. Realizar las migraciones
python manage.py makemigrations
python manage.py migrate

## 🕴️ Datos del superuser
user: admin
contraseña: 12345678