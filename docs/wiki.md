# Wiki — Sistema de Reservas de Laboratorios Universitarios

## Tabla de contenidos
1. [Contexto del problema](#contexto-del-problema)
2. [Usuario final](#usuario-final)
3. [Caso de uso principal](#caso-de-uso-principal)
4. [Alcance del proyecto](#alcance-del-proyecto)
5. [Casos de prueba y evidencias](#casos-de-prueba-y-evidencias)
6. [API REST documentada](#api-rest-documentada)
7. [Diseño de pantallas](#diseño-de-pantallas)
8. [Monetización](#monetización)
9. [Estrategia de visibilidad](#estrategia-de-visibilidad)
10. [Riesgos y mitigaciones](#riesgos-y-mitigaciones)
11. [Estudio de mercado](#estudio-de-mercado)
12. [Roadmap y mejoras futuras](#roadmap-y-mejoras-futuras)

---

## Contexto del problema

Una universidad con múltiples programas académicos presenta conflictos frecuentes en la asignación de laboratorios especializados (informática, electrónica, química y multimedia). Las reservas se gestionan mediante correos electrónicos y hojas de cálculo, generando:

- Solapamientos de horarios
- Baja trazabilidad de uso
- Dificultad para medir la utilización real
- Imposibilidad de generar reportes estadísticos

El sistema centraliza la gestión de disponibilidad, reservas, control de horarios y generación de reportes que apoyen la planeación académica.

---

## Usuario final

| Rol | Descripción |
|---|---|
| **Administrador** | Gestiona todo el sistema, usuarios y configuración |
| **Coordinador Académico** | Gestiona laboratorios, horarios y genera reportes |
| **Docente** | Crea, cancela y reprograma sus propias reservas |
| **Consulta** | Solo puede consultar disponibilidad y horarios |

---

## Caso de uso principal

**Reservar un laboratorio:**

1. El docente inicia sesión con sus credenciales
2. Consulta la disponibilidad de laboratorios por fecha y hora
3. Selecciona el laboratorio y el horario disponible
4. Crea la reserva indicando curso y número de estudiantes
5. El sistema valida que no haya solapamiento ni supere la capacidad
6. La reserva queda confirmada y se registra en auditoría
7. El docente puede cancelar o reprogramar con motivo

---

## Alcance del proyecto

### Incluye
- CRUD completo de laboratorios
- Configuración de horarios disponibles por laboratorio
- Bloqueo de fechas especiales (mantenimiento, festivos)
- Gestión de reservas con validaciones de negocio
- Control de acceso por roles (JWT)
- Historial y auditoría de cambios
- Reportes de uso por laboratorio, docente y periodo
- Exportación CSV/PDF
- API REST documentada con Swagger
- Pruebas unitarias con cobertura ≥ 60%
- Dockerización completa
- CI/CD con GitHub Actions
- Análisis de calidad con SonarQube

### No incluye
- Aplicación móvil nativa
- Integración con sistema académico externo
- Notificaciones por email/SMS
- Pagos o facturación

### Supuestos técnicos
- Los laboratorios ya existen físicamente en la universidad
- Un docente solo puede tener una reserva activa por horario
- La capacidad máxima del laboratorio es un límite estricto

---

## Casos de prueba y evidencias

### Módulo Gestión de Horarios

| ID | Descripción | Tipo | Resultado |
|---|---|---|---|
| TC-H01 | Crear horario con laboratorio activo | Positivo |  Pasa |
| TC-H02 | Crear horario con laboratorio inexistente | Negativo |  Pasa |
| TC-H03 | Crear horario con laboratorio inactivo | Negativo |  Pasa |
| TC-H04 | Crear horario duplicado mismo día | Negativo |  Pasa |
| TC-H05 | Bloquear fecha especial exitosamente | Positivo |  Pasa |
| TC-H06 | Bloquear fecha ya bloqueada | Negativo |  Pasa |
| TC-H07 | Desbloquear horario bloqueado | Positivo |  Pasa |
| TC-H08 | Desbloquear horario ya disponible | Negativo |  Pasa |
| TC-H09 | Listar horarios de laboratorio activo | Positivo |  Pasa |
| TC-H10 | Listar horarios de laboratorio inexistente | Negativo |  Pasa |

### Módulo Gestión de Laboratorios

| ID | Descripción | Tipo | Resultado |
|---|---|---|---|
| TC-L01 | Obtener todos los laboratorios | Positivo | Pasa |
| TC-L02 | Obtener laboratorio por ID existente | Positivo | Pasa |
| TC-L03 | Obtener laboratorio por ID inexistente | Negativo | Pasa |
| TC-L04 | Crear laboratorio con datos válidos | Positivo |  Pasa |
| TC-L05 | Crear laboratorio sin recursos | Positivo |  Pasa |
| TC-L06 | Actualizar nombre de laboratorio | Positivo |  Pasa |
| TC-L07 | Actualizar laboratorio inexistente | Negativo |  Pasa |
| TC-L08 | Desactivar laboratorio existente | Positivo |  Pasa |

### Resumen de cobertura

| Módulo | Pruebas | Cobertura |
|---|---|---|
| horario_service | 20 | 79% |
| laboratorio_service | 17 | 100% |
| horario_repository | 10 | 100% |
| laboratorio_repository | 6 | 100% |
| **Total** | **83** | **90%** |

---

## API REST documentada

La documentación completa está disponible en Swagger UI al levantar el proyecto:

**Local:** http://localhost:8000/docs

### Endpoints principales

#### Horarios
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | /horarios/ | Crear horario disponible | Admin, Coordinador |
| GET | /horarios/laboratorio/{id} | Listar horarios de un laboratorio | Todos |
| GET | /horarios/{id} | Obtener horario por ID | Todos |
| PUT | /horarios/{id} | Actualizar horario | Admin, Coordinador |
| PATCH | /horarios/{id}/bloquear | Bloquear fecha especial | Admin, Coordinador |
| PATCH | /horarios/{id}/disponible | Desbloquear horario | Admin, Coordinador |

#### Laboratorios
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| GET | /laboratorios/ | Listar laboratorios | Todos |
| POST | /laboratorios/ | Crear laboratorio | Admin, Coordinador |
| GET | /laboratorios/{id} | Obtener laboratorio | Todos |
| PUT | /laboratorios/{id} | Actualizar laboratorio | Admin, Coordinador |
| DELETE | /laboratorios/{id} | Desactivar laboratorio | Admin |

#### Reservas
| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| POST | /reservas/ | Crear reserva | Docente |
| GET | /reservas/ | Listar reservas | Todos |
| GET | /reservas/{id} | Obtener reserva | Todos |
| PATCH | /reservas/{id}/cancelar | Cancelar reserva | Docente |

---

## Diseño de pantallas

Los mockups del sistema están diseñados en Figma/Miro cubriendo:

- Pantalla de login
- Dashboard principal por rol
- Listado y filtro de laboratorios
- Calendario de disponibilidad
- Formulario de reserva
- Gestión de horarios
- Reportes y estadísticas

---

## Monetización

Para mantener la aplicación activa se proponen los siguientes modelos:

| Modelo | Descripción |
|---|---|
| **SaaS institucional** | Licencia anual por universidad — precio según número de laboratorios |
| **Freemium** | Hasta 5 laboratorios gratis, pago por funciones avanzadas (reportes, exportación) |
| **Soporte y mantenimiento** | Contrato de soporte técnico mensual por institución |
| **Implementación** | Cobro por instalación, configuración e integración con sistemas existentes |

---

## Estrategia de visibilidad

- Presentación en ferias académicas y congresos de tecnología educativa
- Alianzas con universidades piloto para casos de éxito
- Publicación en repositorios académicos y GitHub
- Demo pública accesible desde URL producción
- Documentación completa en GitHub Wiki
- SEO enfocado en términos como "sistema reservas laboratorios universitarios"

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Solapamiento de reservas por concurrencia | Media | Alto | Transacciones atómicas en BD + validación en service |
| Pérdida de datos | Baja | Alto | Backups automáticos de SQL Server + volúmenes Docker |
| Acceso no autorizado | Media | Alto | JWT + control de roles + HTTPS en producción |
| Baja adopción por docentes | Alta | Medio | UX simple + capacitación + guías de usuario |
| Caída del servidor en producción | Baja | Alto | Docker restart policy + monitoreo con alertas |
| Cambios en requerimientos | Media | Medio | Arquitectura por capas + roadmap definido |

---

## Estudio de mercado

### Sistemas similares existentes

| Sistema | Fortalezas | Diferencias con nuestro sistema |
|---|---|---|
| **EMS Campus** | Completo, integrado con ERP | Muy costoso, complejo de implementar |
| **Skedda** | Interfaz moderna, fácil uso | No especializado en laboratorios universitarios |
| **Resource Guru** | Buena gestión de recursos | No tiene control de roles académicos |
| **Google Calendar** | Gratuito, conocido | Sin validaciones de negocio ni reportes |
| **Hojas de cálculo** | Cero costo | Sin validaciones, solapamientos frecuentes |

### Diferenciadores de nuestro sistema
- Especializado en contexto universitario colombiano
- Control de roles académicos (Coordinador, Docente, Consulta)
- Validaciones de negocio específicas (capacidad, solapamiento, horarios)
- Open source y desplegable en nube o servidor propio
- Arquitectura moderna (FastAPI + Docker) de bajo costo operativo
- Auditoría completa de todas las acciones

---

## Roadmap y mejoras futuras

### Versión 1.0 (actual)
- CRUD laboratorios, horarios y reservas
- Control de roles con JWT
- Auditoría de cambios
- API REST documentada
- Pruebas unitarias 90% cobertura
- Dockerización
- CI/CD con GitHub Actions

### Versión 1.1
- [ ] Notificaciones por email al crear/cancelar reserva
- [ ] Reportes exportables en PDF y CSV
- [ ] Dashboard con estadísticas de uso

### Versión 1.2
- [ ] Integración con calendario institucional
- [ ] App móvil (React Native)
- [ ] Reservas recurrentes (mismo laboratorio cada semana)

### Versión 2.0
- [ ] Integración con sistema académico (SIA)
- [ ] IA para sugerir horarios óptimos
- [ ] Multi-tenancy (varias universidades en una instancia)