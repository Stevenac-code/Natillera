# src/models/ahorro.py

class Ahorro:
    def __init__(self, db):
        self.db = db
    
    def registrar_ahorro(self, ahorrador_id, monto, tipo='ingreso'):
        if tipo not in ('ingreso', 'retiro'):
            raise ValueError("El tipo debe ser 'ingreso' o 'retiro'")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO ahorros (ahorrador_id, monto, tipo)
            VALUES (?, ?, ?)
            ''', (ahorrador_id, monto, tipo))
            conn.commit()
            id_insertado = cursor.lastrowid
            return id_insertado
        except Exception as e:
            print(f"Error en registro: {str(e)}")
            raise
        finally:
            conn.close()
    
    def obtener_ahorros_ahorrador(self, ahorrador_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM ahorros 
        WHERE ahorrador_id = ?
        ORDER BY fecha DESC
        ''', (ahorrador_id,))
        
        ahorros = cursor.fetchall()
        conn.close()
        
        return ahorros
    
    def calcular_saldo(self, ahorrador_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE -monto END) 
        FROM ahorros 
        WHERE ahorrador_id = ?
        ''', (ahorrador_id,))
        
        saldo = cursor.fetchone()[0] or 0
        conn.close()
        
        return saldo