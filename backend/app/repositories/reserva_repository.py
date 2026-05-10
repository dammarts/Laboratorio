from app.config.db import get_connection

def guardar_reserva(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reservas (docente, fecha)
        VALUES (?, ?)
    """, data["docente"], data["fecha"])

    conn.commit()

    return {"message": "Reserva creada"} 