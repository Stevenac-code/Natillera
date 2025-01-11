# src/models/database.py
import sqlite3

class Database:
    def __init__(self, db_name="natillera.db"):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de Ahorradores
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ahorradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT UNIQUE NOT NULL,
            telefono TEXT,
            email TEXT,
            fecha_registro DATE DEFAULT CURRENT_DATE
        )
        ''')
        
        # Tabla de Ahorros
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ahorros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ahorrador_id INTEGER,
            monto REAL NOT NULL,
            fecha DATE DEFAULT CURRENT_DATE,
            tipo TEXT CHECK(tipo IN ('ingreso', 'retiro')),
            FOREIGN KEY (ahorrador_id) REFERENCES ahorradores (id)
        )
        ''')
        
        # Tabla de Préstamos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ahorrador_id INTEGER,
            monto REAL NOT NULL,
            tasa_interes REAL NOT NULL,
            fecha_prestamo DATE DEFAULT CURRENT_DATE,
            estado TEXT CHECK(estado IN ('activo', 'pagado', 'vencido')),
            FOREIGN KEY (ahorrador_id) REFERENCES ahorradores (id)
        )
        ''')

        # Tabla de Pagos de Préstamos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos_prestamo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prestamo_id INTEGER,
            fecha DATE DEFAULT CURRENT_DATE,
            tipo TEXT CHECK(tipo IN ('interes', 'abono')),
            monto REAL NOT NULL,
            saldo_restante REAL NOT NULL,
            FOREIGN KEY (prestamo_id) REFERENCES prestamos (id)
        )
        ''')

         # Tabla de Rifas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rifas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ahorrador_id INTEGER,
            fecha_pago DATE DEFAULT CURRENT_DATE,
            monto REAL NOT NULL,
            FOREIGN KEY (ahorrador_id) REFERENCES ahorradores (id)
        )
        ''')

        # Tabla de Números de Rifa
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS numeros_rifa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ahorrador_id INTEGER,
            numero INTEGER,
            FOREIGN KEY (ahorrador_id) REFERENCES ahorradores (id),
            UNIQUE(numero)  -- Asegura que no se repitan números
        )
        ''')

        # Tabla de Fechas de Rifas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fechas_rifa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL,
            ganador_id INTEGER NULL,
            numero_ganador TEXT NULL,
            valor REAL NOT NULL,
            realizada BOOLEAN DEFAULT 0,
            FOREIGN KEY (ganador_id) REFERENCES ahorradores (id)
        )
        ''')

        try:
            cursor.execute('ALTER TABLE prestamos ADD COLUMN saldo_actual REAL')
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Columna ya existe
                    
        conn.commit()
        conn.close()