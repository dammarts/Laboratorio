# Diagrama de Componentes — Arquitectura del Sistema

mermaid
graph TD
  subgraph Frontend["Frontend (React/Vue)"]
    UI[Interfaz de usuario]
    SW[Swagger UI /docs]
  end

  subgraph Backend["Backend — FastAPI Python 3.11"]
    subgraph Capa1["Capa 1 — Controller"]
      HC[horario_controller]
      LC[laboratorio_controller]
      RC[reserva_controller]
    end

    subgraph Capa2["Capa 2 — Service"]
      HS[horario_service]
      LS[laboratorio_service]
      RS[reserva_service]
    end

    subgraph Capa3["Capa 3 — Repository"]
      HR[horario_repository]
      LR[laboratorio_repository]
      RR[reserva_repository]
      AR[auditoria_repository]
    end

    subgraph Capa4["Capa 4 — Models / Schemas"]
      M[SQLAlchemy Models]
      SCH[Pydantic Schemas]
    end

    subgraph Capa5["Capa 5 — Infraestructura"]
      DB_CFG[config/db.py]
      JWT[security/jwt_handler]
      DEP[security/dependencies]
      SET[config/settings]
    end
  end

  subgraph Base_Datos["Base de Datos — SQL Server 2022"]
    T1[(USUARIO)]
    T2[(LABORATORIO)]
    T3[(HORARIO_LABORATORIO)]
    T4[(RESERVA)]
    T5[(AUDITORIA_RESERVA)]
  end

  subgraph DevOps["DevOps"]
    DOC[Docker Compose]
    GHA[GitHub Actions CI/CD]
    SON[SonarQube]
  end

  UI -->|HTTP REST JSON| HC
  UI -->|HTTP REST JSON| LC
  UI -->|HTTP REST JSON| RC
  SW -->|HTTP| HC

  HC --> HS
  LC --> LS
  RC --> RS

  HS --> HR
  LS --> LR
  RS --> RR
  RS --> AR

  HR --> M
  LR --> M
  RR --> M
  AR --> M

  M --> DB_CFG
  DB_CFG --> T1
  DB_CFG --> T2
  DB_CFG --> T3
  DB_CFG --> T4
  DB_CFG --> T5

  DOC -.->|orquesta| Backend
  DOC -.->|orquesta| Base_Datos
  GHA -.->|ejecuta pruebas| Backend
  SON -.->|analiza calidad| Backend
