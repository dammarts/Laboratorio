# Sistema de Reservas de Laboratorios Universitarios

Sistema centralizado para gestionar disponibilidad, reservas, control de horarios y generación de reportes en laboratorios universitarios.

**Equipo:** Valeria Caro · Daniel Montoya · Juan Pablo Acevedo

---

## URLs de producción

| Componente | URL |
|---|---|
| Frontend | https://laboratorio-theta.vercel.app |
| Backend API | https://laboratorio-uakf.onrender.com |
| Swagger UI | https://laboratorio-uakf.onrender.com/docs |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18 + Vite + React Router |
| Backend | Python 3.11 + FastAPI + SQLAlchemy |
| Base de datos | PostgreSQL 16 (Neon en producción, Docker en local) |
| Auth | JWT (python-jose) + bcrypt (cost 12) |
| CI/CD | GitHub Actions + SonarCloud |
| Despliegue | Vercel (frontend) · Render (backend) · Neon (BD) |
| Pruebas | pytest · Playwright · Locust |

---

## Levantar el proyecto localmente

### Prerrequisitos

- Docker Desktop instalado y corriendo
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/valeriacaro23/Laboratorio.git
cd Laboratorio
```

### 2. Crear el archivo de variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores reales (ver tabla de variables más abajo).

### 3. Levantar el stack completo

```bash
docker-compose up --build
```

Esto levanta:
- **PostgreSQL** en `localhost:5432`
- **Backend FastAPI** en `localhost:8000`

### 4. Crear el primer usuario administrador (solo la primera vez)

```bash
# Linux/Mac
SEED_EMAIL=admin@universidad.edu SEED_PASSWORD=Admin123! python backend/seed.py

# Windows PowerShell
$env:SEED_EMAIL="admin@universidad.edu"; $env:SEED_PASSWORD="Admin123!"; python backend/seed.py

# O dentro del contenedor
docker exec -e SEED_EMAIL="admin@universidad.edu" -e SEED_PASSWORD="Admin123!" reservas_backend python seed.py
```

### 5. Levantar el frontend (opcional, solo para desarrollo)

```bash
cd frontend
npm install
npm run dev
# Disponible en http://localhost:5173
```

---

## Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DB_SERVER` | Host de la BD (usar `db` en Docker) | `db` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `DB_USER` | Usuario de BD | `postgres` |
| `DB_PASSWORD` | Contraseña de BD | `Admin123!` |
| `DB_NAME` | Nombre de la base de datos | `reservas` |
| `JWT_SECRET_KEY` | Clave secreta para JWT (mín. 32 chars) | `clave_muy_larga_y_segura` |
| `APP_ENV` | Entorno (`development` / `production`) | `development` |
| `CORS_ORIGIN` | Origen permitido para CORS | `http://localhost:5173` |
| `SEED_EMAIL` | Email del admin inicial (solo seed) | `admin@uni.edu` |
| `SEED_PASSWORD` | Contraseña del admin inicial (solo seed) | `Admin123!` |

---

## Ejecutar pruebas

```bash
cd backend

# Todas las pruebas
pytest tests/ --ignore=tests/load --ignore=tests/stress -v

# Con reporte de cobertura
pytest tests/ --ignore=tests/load --ignore=tests/stress --cov=app --cov-report=term-missing

# Solo pruebas de humo
pytest tests/smoke/ -m smoke -v

# Pruebas e2e (Playwright — desde la raíz)
cd ..
npx playwright test

# Pruebas de carga (Locust — backend debe estar corriendo)
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## Estructura del proyecto

```
Laboratorio/
├── backend/               # API FastAPI
│   ├── app/
│   │   ├── config/        # Configuración BD y variables de entorno
│   │   ├── controller/    # Routers FastAPI (endpoints)
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── repositories/  # Acceso a base de datos
│   │   ├── schemas/       # Schemas Pydantic (request/response)
│   │   ├── security/      # JWT y control de roles
│   │   └── services/      # Lógica de negocio
│   └── tests/             # Pirámide de pruebas completa
├── frontend/              # App React + Vite
│   └── src/
│       ├── components/    # Componentes reutilizables
│       ├── context/       # Context de autenticación
│       ├── pages/         # Páginas de la aplicación
│       └── services/      # Llamadas a la API
├── database/              # Scripts SQL iniciales
├── docs/                  # Wiki, diagramas y evidencias
│   ├── diagramas/         # ER, secuencia, componentes (Mermaid)
│   └── evidencias/        # Capturas y reportes de pruebas
└── .github/workflows/     # CI/CD con GitHub Actions
```

---

## Documentación completa

La documentación del proyecto (contexto, casos de prueba, API, diagramas, mockups, roadmap) está en [`docs/wiki.md`](docs/wiki.md).

---

## Roles del sistema

| Rol | Permisos |
|---|---|
| **ADMIN** | Acceso total — gestiona usuarios, labs, horarios, reservas y reportes |
| **COORDINADOR** | Gestiona labs, horarios y puede ver reportes |
| **DOCENTE** | Crea, cancela y reprograma sus propias reservas |
| **CONSULTA** | Solo lectura — consulta disponibilidad |

---

## CI/CD

Cada push dispara el pipeline en GitHub Actions:

1. **Tests** — pytest con cobertura reportada a SonarCloud
2. **Lint** — ruff en PRs hacia main

Badge de estado: ver pestaña **Actions** en GitHub.
