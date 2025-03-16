# 🔗 URL Shortener - Acortador de URLs

Un servicio moderno para acortar URLs con interfaz web y API RESTful, construido con Python, Flask y SQLAlchemy.

[![Deploy](https://img.shields.io/badge/Deploy-Docker-blue)](https://docs.docker.com)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green)](https://python.org)

## 🌟 Características

- **Acortamiento de URLs** mediante interfaz web o API
- **Redirección inteligente** con conteo de visitas
- **API RESTful** con soporte JSON
- **Estadísticas detalladas** de cada URL
- **Dockerizado** para despliegues fáciles
- **Validación de URLs** con sistema de reintentos
- **Base de datos SQL** con SQLAlchemy ORM
- **CLI integrado** para gestión de la base de datos
- **Soporte para entornos** múltiples (dev/prod)
- **Interfaz responsive** con Bootstrap 5

## 🚀 Instalación Rápida

### Requisitos
- Python 3.9+
- pip
- SQLite (o cualquier DB soportada por SQLAlchemy)
- Docker

🐳 Usar con Docker

# Construir y ejecutar
docker-compose up --build

# Acceder en:
http://localhost:5000

### Pasos básicos
```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/url-shortener.git
cd url-shortener

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
cp .env.example .env
# Editar .env según sea necesario

# 4. Inicializar base de datos
flask init-db

# 5. Ejecutar la aplicación
flask run --host=0.0.0.0 --port=5000
