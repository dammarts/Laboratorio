# Backend — Sistema de Reservas de Laboratorios

## Stack

| Tecnología | Uso |
|---|---|
| Python 3.11 + FastAPI | API REST |
| SQL Server (MSSQL) en Docker | Base de datos |
| SQLAlchemy 1.x + pymssql | ORM y driver MSSQL |
| python-jose + passlib[bcrypt] | JWT y hashing de contraseñas |
| pytest + pytest-cov | Pruebas unitarias e integración |
| locust | Pruebas de carga y estrés |

## Estructura del proyecto

```
backend/
├── app/
│   ├── config/
│   │   └── db.py                  # Conexión SQLAlchemy y SessionLocal
│   ├── controller/
│   │   ├── auth_controller.py     # POST /auth/login, /auth/register, GET /usuarios/me
│   │   ├── horario_controller.py  # CRUD de horarios y bloqueos
│   │   ├── laboratorio_controller.py
│   │   ├── reporte_controller.py  # GET /reportes/* y exportación CSV
│   │   └── reserva_controller.py  # CRUD de reservas e historial
│   ├── models/
│   │   ├── base.py                # DeclarativeBase única
│   │   ├── historial_reserva.py
│   │   ├── horario.py
│   │   ├── laboratorio.py
│   │   ├── reserva.py
│   │   └── usuario.py
│   ├── repositories/              # Queries SQLAlchemy, sin lógica de negocio
│   │   ├── historial_repository.py
│   │   ├── horario_repository.py
│   │   ├── laboratorio_repository.py
│   │   ├── reporte_repository.py
│   │   ├── reserva_repository.py
│   │   └── usuario_repository.py
│   ├── schemas/                   # Pydantic V2 — request/response DTOs
│   │   ├── historial_reserva_schema.py
│   │   ├── horario_schema.py
│   │   ├── laboratorio_schema.py
│   │   ├── reporte_schema.py
│   │   ├── reserva_schema.py
│   │   └── usuario_schema.py
│   ├── security/
│   │   ├── config.py              # JWT_SECRET y ALGORITHM
│   │   └── dependencies.py        # get_current_user(), require_roles()
│   ├── services/                  # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── horario_service.py
│   │   ├── laboratorio_service.py
│   │   ├── reporte_service.py
│   │   └── reserva_service.py
│   └── main.py                    # App FastAPI, registro de routers
├── tests/
│   ├── integration/               # Tests contra endpoints reales
│   ├── smoke/                     # 10 tests de humo (< 200ms)
│   ├── unit/                      # Tests unitarios con mocks
│   ├── load/locustfile.py         # Carga normal: 50 usuarios
│   └── stress/locustfile_stress.py # Estrés: 200 usuarios
├── seed.py                        # Crea el primer usuario ADMIN
├── Dockerfile
├── .coveragerc
└── requirements.txt
```

## Requisitos previos

- Python 3.11
- Docker y docker-compose
- ODBC Driver 17 for SQL Server *(solo desarrollo local sin Docker)*

## Variables de entorno

Crea un archivo `.env` en la raíz del repositorio basándote en esta plantilla:

```env
# Base de datos
DB_USER=sa
DB_PASSWORD=TuPasswordSegura123!
DB_NAME=reservas
DB_SERVER=db          # "db" en Docker, "localhost" en desarrollo local
DB_PORT=1433

# Auth
JWT_SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria

# Entorno
APP_ENV=development   # "testing" deshabilita init_db al arrancar

# Script seed (solo para crear primer admin)
SEED_EMAIL=admin@uni.edu
SEED_PASSWORD=Admin123!
```

> Nunca commitees `.env`. El archivo está en `.gitignore`.

## Cómo levantar localmente

### Con Docker (recomendado)

```bash
docker-compose up --build
```

Levanta SQL Server y el backend juntos. La BD se crea automáticamente.

### Sin Docker

```bash
# 1. Levantar solo la BD
docker-compose up -d db

# 2. Instalar dependencias
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# 3. Arrancar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Crear primer usuario ADMIN

Ejecutar **una sola vez** después de que la BD esté corriendo:

```bash
# Linux/Mac
SEED_EMAIL=admin@uni.edu SEED_PASSWORD=Admin123! python seed.py

# Windows PowerShell
$env:SEED_EMAIL="admin@uni.edu"; $env:SEED_PASSWORD="Admin123!"; python seed.py
```

## Correr pruebas

```bash
# Suite completa (unitarios + integración + smoke)
pytest tests/ -v

# Solo smoke tests
pytest tests/smoke/ -m smoke -v

# Con reporte de cobertura
pytest tests/ --cov=app --cov-report=term-missing
```

Cobertura actual: **87%** (118 tests passing).

## Pruebas de carga y estrés

Requiere el servidor corriendo en `http://localhost:8000`.

```bash
# Carga normal — 50 usuarios, 2 minutos
locust -f tests/load/locustfile.py --headless -u 50 -r 5 -t 2m --host=http://localhost:8000

# Estrés — 200 usuarios, 3 minutos
locust -f tests/stress/locustfile_stress.py --headless -u 200 -r 20 -t 3m --host=http://localhost:8000
```

Variables de entorno opcionales para locust:

```bash
LOAD_ADMIN_EMAIL=admin@uni.edu
LOAD_ADMIN_PASSWORD=Admin123!
LOAD_DOCENTE_EMAIL=docente@uni.edu
LOAD_DOCENTE_PASSWORD=Docente123!
```

## API

Swagger UI disponible en **http://localhost:8000/docs** cuando el servidor esté corriendo.

Endpoints principales:

| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| POST | `/auth/login` | Público | Obtener JWT |
| POST | `/auth/register` | ADMIN | Crear usuario |
| GET | `/usuarios/me` | Autenticado | Perfil propio |
| GET | `/laboratorios` | Público | Listar laboratorios |
| POST | `/reservas/` | ADMIN, COORD, DOCENTE | Crear reserva |
| GET | `/reservas/historial` | ADMIN, COORD | Ver historial |
| GET | `/reportes/uso-laboratorio` | ADMIN, COORD | Reporte de uso |
| GET | `/reportes/ocupacion-mensual` | ADMIN, COORD | Ocupación mensual |
| GET | `/reportes/por-docente` | ADMIN, COORD | Actividad por docente |
| GET | `/reportes/uso-laboratorio/csv` | ADMIN, COORD | Exportar CSV |
