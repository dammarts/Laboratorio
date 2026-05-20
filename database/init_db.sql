-- Datos de muestra para laboratorios.
-- Las tablas son creadas por SQLAlchemy (Base.metadata.create_all) al iniciar el backend.
-- Este script corre solo en el primer arranque cuando el volumen pg_data está vacío.

INSERT INTO "LABORATORIO" (nombre, ubicacion, capacidad_maxima, tipo_laboratorio, descripcion, estado)
VALUES
  ('Lab Informática 101', 'Bloque A, Piso 1', 30, 'INFORMATICA', 'Lab con 30 computadores', TRUE),
  ('Lab Electrónica 201', 'Bloque B, Piso 2', 20, 'ELECTRONICA', 'Lab con osciloscopios',    TRUE),
  ('Lab Química 301',     'Bloque C, Piso 3', 24, 'QUIMICA',     'Lab con campanas',          TRUE)
ON CONFLICT DO NOTHING;
