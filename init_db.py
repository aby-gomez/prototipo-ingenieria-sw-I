import sqlite3

def init_db():
    conn = sqlite3.connect('prestamos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipo (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            gama TEXT,
            stock INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitud (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            docente_cargo TEXT,
            fecha_retiro TEXT,
            fecha_devolucion TEXT,
            materia_proyecto TEXT,
            estado TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
