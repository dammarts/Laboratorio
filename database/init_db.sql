USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'reservas')
BEGIN
    CREATE DATABASE reservas;
END
GO

USE reservas;
GO

-- TABLA USUARIO (necesaria por las relaciones)
IF OBJECT_ID('HORARIO_LABORATORIO', 'U') IS NOT NULL DROP TABLE HORARIO_LABORATORIO;
IF OBJECT_ID('LABORATORIO', 'U') IS NOT NULL DROP TABLE LABORATORIO;
GO

CREATE TABLE LABORATORIO (
    laboratorio_id      INT IDENTITY(1,1) PRIMARY KEY,
    nombre              NVARCHAR(150) NOT NULL,
    ubicacion           NVARCHAR(200) NOT NULL,
    capacidad_maxima    INT NOT NULL,
    tipo_laboratorio    NVARCHAR(50) NOT NULL,
    descripcion         NVARCHAR(500) NULL,
    estado              BIT NOT NULL DEFAULT 1,
    created_at          DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT CHK_TIPO CHECK (tipo_laboratorio IN ('INFORMATICA','ELECTRONICA','QUIMICA','MULTIMEDIA')),
    CONSTRAINT CHK_CAP  CHECK (capacidad_maxima > 0)
);
GO

CREATE TABLE HORARIO_LABORATORIO (
    horario_id      INT IDENTITY(1,1) PRIMARY KEY,
    laboratorio_id  INT NOT NULL,
    dia_semana      TINYINT NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    disponible      BIT NOT NULL DEFAULT 1,
    fecha_bloqueo   DATE NULL,
    motivo_bloqueo  NVARCHAR(300) NULL,
    CONSTRAINT FK_HORARIO_LAB   FOREIGN KEY (laboratorio_id) REFERENCES LABORATORIO(laboratorio_id),
    CONSTRAINT CHK_DIA          CHECK (dia_semana BETWEEN 1 AND 7),
    CONSTRAINT CHK_HORAS        CHECK (hora_fin > hora_inicio)
);
GO

-- Datos de prueba
INSERT INTO LABORATORIO (nombre, ubicacion, capacidad_maxima, tipo_laboratorio, descripcion) VALUES
('Lab Informática 101', 'Bloque A, Piso 1', 30, 'INFORMATICA', 'Lab con 30 computadores'),
('Lab Electrónica 201', 'Bloque B, Piso 2', 20, 'ELECTRONICA', 'Lab con osciloscopios'),
('Lab Química 301',     'Bloque C, Piso 3', 24, 'QUIMICA',     'Lab con campanas');
GO

PRINT 'Base de datos inicializada correctamente';
GO