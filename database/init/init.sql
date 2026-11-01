-- Esquema compatible con los modelos SQLAlchemy Room y Booking.
-- IF NOT EXISTS permite que SQLAlchemy también cree las tablas al iniciar.
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    edificio VARCHAR(150) NOT NULL,
    capacidad INTEGER NOT NULL,
    equipamiento JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    aula_id INTEGER NOT NULL REFERENCES rooms (id),
    usuario VARCHAR(150) NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_rooms_id ON rooms (id);
CREATE INDEX IF NOT EXISTS ix_bookings_id ON bookings (id);
CREATE INDEX IF NOT EXISTS ix_bookings_aula_id ON bookings (aula_id);

INSERT INTO rooms (id, nombre, edificio, capacidad, equipamiento)
VALUES
    (1, 'Aula Magna', 'Edificio Central', 180, '["proyector", "sonido", "pizarra"]'),
    (2, 'Aula 101', 'Edificio de Ingenieria', 40, '["proyector", "pizarra"]'),
    (3, 'Laboratorio de Informatica', 'Edificio de Ingenieria', 32, '["ordenadores", "proyector"]'),
    (4, 'Aula 204', 'Edificio de Ciencias', 55, '["pantalla", "pizarra"]'),
    (5, 'Sala de Estudio Norte', 'Biblioteca Universitaria', 24, '["enchufes", "pantalla"]')
ON CONFLICT (id) DO NOTHING;

INSERT INTO bookings (id, aula_id, usuario, fecha, hora_inicio, hora_fin)
VALUES
    (1, 2, 'alumno001', DATE '2026-11-02', TIME '09:00:00', TIME '10:30:00'),
    (2, 3, 'docente001', DATE '2026-11-02', TIME '11:00:00', TIME '13:00:00'),
    (3, 5, 'alumno002', DATE '2026-11-03', TIME '15:00:00', TIME '16:00:00')
ON CONFLICT (id) DO NOTHING;

-- Alinea las secuencias tras insertar identificadores explícitos.
SELECT setval(
    pg_get_serial_sequence('rooms', 'id'),
    COALESCE((SELECT MAX(id) FROM rooms), 1),
    EXISTS (SELECT 1 FROM rooms)
);

SELECT setval(
    pg_get_serial_sequence('bookings', 'id'),
    COALESCE((SELECT MAX(id) FROM bookings), 1),
    EXISTS (SELECT 1 FROM bookings)
);
