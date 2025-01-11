# models/prestamo.py
from datetime import datetime

class Prestamo:
    def __init__(self, db):
        self.db = db
    
    def crear_prestamo(self, ahorrador_id, monto):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        fecha_prestamo = datetime.now()
        interes_prestamo = 3.0
        
        try:            
            cursor.execute('''
            INSERT INTO prestamos (
                ahorrador_id, monto, tasa_interes, 
                fecha_prestamo, estado, saldo_actual
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (ahorrador_id, monto, interes_prestamo, fecha_prestamo.date(), 
                  'activo', monto))
            
            prestamo_id = cursor.lastrowid
            conn.commit()
            return prestamo_id
        finally:
            conn.close()

    def listar_prestamos_ahorrador(self, ahorrador_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if ahorrador_id:
                cursor.execute('''
                SELECT p.id, p.ahorrador_id, p.monto, p.tasa_interes, 
                       p.fecha_prestamo, p.estado, p.saldo_actual 
                FROM prestamos p
                WHERE ahorrador_id = ?
                ORDER BY fecha_prestamo DESC
                ''', (ahorrador_id,))
            else:
                cursor.execute('''
                SELECT p.id, p.ahorrador_id, p.monto, p.tasa_interes, 
                       p.fecha_prestamo, p.estado, p.saldo_actual 
                FROM prestamos p
                ORDER BY fecha_prestamo DESC
                ''')
            
            prestamos = cursor.fetchall()
            return prestamos
        finally:
            conn.close()

    def registrar_pago_interes(self, prestamo_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT saldo_actual, tasa_interes 
            FROM prestamos 
            WHERE id = ?''', (prestamo_id,))
            
            prestamo = cursor.fetchone()
            if not prestamo:
                raise ValueError("Préstamo no encontrado")
            
            saldo_actual, tasa_interes = prestamo
            
            interes = (saldo_actual * tasa_interes) / 100
            
            cursor.execute('''
            INSERT INTO pagos_prestamo (
                prestamo_id, tipo, monto, saldo_restante
            )
            VALUES (?, 'interes', ?, ?)
            ''', (prestamo_id, interes, saldo_actual))
            
            conn.commit()
            return True
            
        except Exception as e:
            raise e
        finally:
            conn.close()

    def registrar_abono(self, prestamo_id, monto):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar si está al día con los intereses
            if not self.esta_al_dia_intereses(prestamo_id):
                raise ValueError("Debe estar al día con los intereses para realizar abonos")
            
            # Obtener saldo actual
            cursor.execute('SELECT saldo_actual FROM prestamos WHERE id = ?', (prestamo_id,))
            resultado = cursor.fetchone()
            if not resultado:
                raise ValueError("Préstamo no encontrado")
                
            saldo_actual = resultado[0]
            if saldo_actual is None:
                raise ValueError("El préstamo no tiene un saldo válido")
            
            if monto > saldo_actual:
                raise ValueError("El abono no puede ser mayor al saldo actual")
            
            nuevo_saldo = saldo_actual - monto
            
            # Registrar abono
            cursor.execute('''
            INSERT INTO pagos_prestamo (prestamo_id, tipo, monto, saldo_restante)
            VALUES (?, 'abono', ?, ?)
            ''', (prestamo_id, monto, nuevo_saldo))
            
            # Actualizar saldo en préstamo
            cursor.execute('''
            UPDATE prestamos 
            SET saldo_actual = ?,
                estado = CASE WHEN ? = 0 THEN 'pagado' ELSE estado END
            WHERE id = ?
            ''', (nuevo_saldo, nuevo_saldo, prestamo_id))
            
            conn.commit()
            return True
        finally:
            conn.close()

    def esta_al_dia_intereses(self, prestamo_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener fecha del último pago de intereses
            cursor.execute('''
            SELECT fecha FROM pagos_prestamo 
            WHERE prestamo_id = ? AND tipo = 'interes'
            ORDER BY fecha DESC LIMIT 1''', (prestamo_id,))
            
            ultimo_pago = cursor.fetchone()
            if not ultimo_pago:
                return False
            
            ultimo_pago_fecha = datetime.strptime(ultimo_pago[0], '%Y-%m-%d')
            dias_transcurridos = (datetime.now() - ultimo_pago_fecha).days
            
            return dias_transcurridos <= 30
        finally:
            conn.close()
    
    def obtener_historial_pagos(self, prestamo_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT fecha, tipo, monto, saldo_restante 
            FROM pagos_prestamo 
            WHERE prestamo_id = ?
            ORDER BY fecha DESC
            ''', (prestamo_id,))
            
            pagos = cursor.fetchall()
            return pagos
        finally:
            conn.close()
    
    def calcular_interes_pendiente(self, prestamo_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT saldo_actual, tasa_interes, fecha_prestamo
            FROM prestamos WHERE id = ?''', (prestamo_id,))
            
            prestamo = cursor.fetchone()
            if not prestamo:
                raise ValueError("El préstamo que intenta buscar no existe")
                
            saldo, tasa, fecha_prestamo = prestamo
            interes_mensual = (saldo * tasa) / 100
            return interes_mensual
        finally:
            conn.close()