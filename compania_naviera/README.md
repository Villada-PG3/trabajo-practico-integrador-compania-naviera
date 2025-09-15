# 🛳️ Proyecto Compañía Naviera SEA STAR

Aplicación web Django para gestionar destinos, viajes y pasajeros.

---

## 📌 Requisitos

- Python 3.10+ (recomendado 3.12)
- Django 5.2.6
- SQLite (por defecto) o tu motor preferido
- Pip / venv

---

## ⚙️ Instalación (paso a paso)

```bash
# 1) Crear y activar un entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# 2) Instalar dependencias
pip install -r compania_naviera/requirements.txt

# 3) Migraciones
cd compania_naviera
python manage.py migrate

# 4) Crear superusuario
python manage.py createsuperuser

# 5) Ejecutar
python manage.py runserver
```

Admin: http://127.0.0.1:8000/admin/

---

## 🎨 Admin con tema (preconfigurado)

Se incluye el paquete **Jazzmin** para modernizar el admin.

- Paquete: `django-jazzmin==3.0.1`
- Compatible con Django 5.2.x
- Ya agregado en `INSTALLED_APPS` y configurado en `Config/settings.py` con `JAZZMIN_SETTINGS`.

Si quieres desactivarlo, quita `'jazzmin'` de `INSTALLED_APPS` y elimina el bloque `JAZZMIN_SETTINGS`.

### Cambiar branding del admin
- Logo: coloca tu archivo en `compania_naviera/compania_naviera/static/` y ajusta `JAZZMIN_SETTINGS["site_logo"]`.
- Colores/tema: cambia `JAZZMIN_SETTINGS["theme"]` o usa el **UI Builder** (ícono pincel) dentro del admin.

---

## 🧰 Comandos útiles

```bash
# Crear app
python manage.py startapp <nombre_app>

# Superusuario
python manage.py createsuperuser

# Recopilar estáticos (si usas DEBUG=False en producción)
python manage.py collectstatic
```

---

## 🧪 Verificación rápida

1. Levanta el servidor y entra a `/admin`.
2. Valida que veas el tema Jazzmin con el branding **SEA STAR**.
3. Crea objetos de ejemplo desde el admin para asegurar que las relaciones funcionan.
