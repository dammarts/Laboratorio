# Diagrama de Secuencia — Flujo Principal: Crear Reserva

mermaid
sequenceDiagram
  actor U as Usuario (Docente)
  participant C as Controller
  participant S as Service
  participant R as Repository
  participant DB as SQL Server

  U->>C: POST /reservas/ + JWT Token
  C->>C: Validar JWT + verificar rol
  C->>S: crear_reserva(datos)
  S->>R: obtener_laboratorio(id)
  R->>DB: SELECT * FROM LABORATORIO WHERE id=?
  DB-->>R: Laboratorio activo
  R-->>S: Laboratorio OK
  S->>R: verificar_solapamiento(lab_id, fecha, hora)
  R->>DB: SELECT solapamiento FROM RESERVA
  DB-->>R: Sin conflicto
  R-->>S: Sin solapamiento
  S->>R: crear_reserva(datos_validados)
  R->>DB: INSERT INTO RESERVA
  R->>DB: INSERT INTO AUDITORIA_RESERVA
  DB-->>R: reserva_id generado
  R-->>S: ReservaResponse
  S-->>C: ReservaResponse
  C-->>U: 201 Created + JSON

  alt Solapamiento detectado
    S-->>C: 409 Conflict
    C-->>U: Error solapamiento de horario
  end

  alt Laboratorio inactivo o no existe
    S-->>C: 404 / 400 Error
    C-->>U: Error laboratorio no disponible
  end
