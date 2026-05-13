# 🔬 Sistema de Reservas de Laboratorios Universitarios

Sistema centralizado para gestionar la disponibilidad, reservas y horarios de laboratorios universitarios. Elimina los conflictos generados por el manejo manual mediante correos y hojas de cálculo.


## 🚀 Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Base de datos | SQL Server 2022 |
| ORM | SQLAlchemy |
| Validaciones | Pydantic v2 |
| Autenticación | JWT (python-jose) |
| Contenedores | Docker + Docker Compose |
| Pruebas | pytest + pytest-cov |
| Calidad | SonarQube |
| CI/CD | GitHub Actions |


## 📁 Estructura del proyecto

ReservasLaboratorio/
├── backend/
│   ├── app/
│   │   ├── config/          # Conexión BD y variables de entorno
│   │   ├── controller/      # Endpoints FastAPI (Capa 1)
│   │   ├── services/        # Lógica de negocio (Capa 2)
│   │   ├── repositories/    # Acceso a datos (Capa 3)
│   │   ├── models/          # Modelos SQLAlchemy (Capa 4)
│   │   ├── schemas/         # Schemas Pydantic (Capa 4)
│   │   ├── security/        # JWT y dependencias de auth
│   │   └── main.py
│   ├── tests/               # Pruebas unitarias
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── init_db.sql          # Script de inicialización
├── docs/
│   ├── diagramas/
│   │   ├── er.md            # Diagrama Entidad-Relación
│   │   ├── secuencia.md     # Diagrama de Secuencia
│   │   └── componentes.md   # Diagrama de Componentes
│   └── docs_reservas.md     # Documentación del módulo reservas
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 👥 Roles del sistema

| Rol | Permisos |
|---|---|
| ADMINISTRADOR | Acceso total al sistema |
| COORDINADOR | Gestión de laboratorios y horarios |
| DOCENTE | Crear y cancelar sus propias reservas |
| CONSULTA | Solo lectura |

---

## ⚙️ Instalación y ejecución local

### Prerrequisitos
- Docker Desktop instalado y corriendo
- Git

### Pasos

**1. Clona el repositorio**
```bash
git clone https://github.com/valeriacaro23/Laboratorio.git
cd Laboratorio
```

**2. Configura las variables de entorno**
```bash
cp .env.example .env
# Edita .env con tu contraseña de SQL Server
```

**3. Levanta los contenedores**
```bash
docker-compose up --build
```

**4. Accede a la API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 Ejecutar pruebas

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

Resultado actual: **83 pruebas · 90% cobertura**

---

## 📊 Endpoints principales

| Método | Endpoint | Descripción | Roles |
|---|---|---|---|
| POST | /horarios/ | Crear horario | Admin, Coordinador |
| GET | /horarios/laboratorio/{id} | Listar horarios | Todos |
| PATCH | /horarios/{id}/bloquear | Bloquear fecha | Admin, Coordinador |
| GET | /laboratorios/ | Listar laboratorios | Todos |
| POST | /laboratorios/ | Crear laboratorio | Admin, Coordinador |
| POST | /reservas/ | Crear reserva | Docente |
| GET | /reservas/ | Listar reservas | Todos |

---

## 📐 Diagramas

- [Diagrama ER](docs/diagramas/er.md)
- [Diagrama de Secuencia](docs/diagramas/secuencia.md)
- [Diagrama de Componentes](docs/diagramas/componentes.md)

---

## 🌿 Ramas de trabajo

| Rama | Responsable | Módulo |
|---|---|---|
| feature/gestion-horarios | Valeria | Gestión de horarios |
| feature/gestion-laboratorios | Compañero | Gestión de laboratorios |
| feature/gestion-reservas | Compañero | Gestión de reservas |
| feature/docs | Valeria | Documentación y diagramas |
| feature/ci | Valeria | CI/CD y SonarQube |

---

## 🔐 Variables de entorno

Copia `.env.example` como `.env` y completa los valores:

```env
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=reservas
DB_USER=sa
DB_PASSWORD=TuContraseñaSegura
JWT_SECRET_KEY=tu_clave_secreta
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🐳 Docker

```bash
# Levantar todo
docker-compose up --build

# Solo la base de datos
docker-compose up db -d

# Ver logs del backend
docker logs reservas_backend
```