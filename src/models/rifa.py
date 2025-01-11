# models/rifa.py
import random
from datetime import datetime

class Rifa:
    def __init__(self, db):
        self.db = db
    
    def registrar_pago(self, ahorrador_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO rifas (ahorrador_id, monto)
            VALUES (?, ?)
            ''', (ahorrador_id, 10000))
            
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def obtener_pagos_ahorrador(self, ahorrador_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT r.id, a.nombre, r.fecha_pago, r.monto 
            FROM rifas r
            JOIN ahorradores a ON r.ahorrador_id = a.id
            WHERE r.ahorrador_id = ?
            ORDER BY r.fecha_pago DESC
            ''', (ahorrador_id,))
            
            return cursor.fetchall()
        finally:
            conn.close()
    
    def obtener_todos_pagos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT r.id, a.nombre, r.fecha_pago, r.monto 
            FROM rifas r
            JOIN ahorradores a ON r.ahorrador_id = a.id
            ORDER BY r.fecha_pago DESC
            ''')
            
            return cursor.fetchall()
        finally:
            conn.close()
    
    def buscar_pagos(self, nombre):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT r.id, a.nombre, r.fecha_pago, r.monto 
            FROM rifas r
            JOIN ahorradores a ON r.ahorrador_id = a.id
            WHERE a.nombre LIKE ?
            ORDER BY r.fecha_pago DESC
            ''', (f'%{nombre}%',))
            
            return cursor.fetchall()
        finally:
            conn.close()

    def repartir_numeros(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Primero, obtener todos los ahorradores
            cursor.execute('SELECT id, nombre FROM ahorradores')
            ahorradores = cursor.fetchall()
            
            # Limpiar tabla actual
            cursor.execute('DELETE FROM numeros_rifa')
            
            # Generar lista de números disponibles (00-99)
            numeros_disponibles = list(range(100))
            random.shuffle(numeros_disponibles)
            
            # Asignar 3 números a cada ahorrador que no sea NATILLERA
            index = 0
            for ahorrador in ahorradores:
                if ahorrador[1] != 'NATILLERA':
                    for _ in range(3):  # 3 números por ahorrador
                        if index < len(numeros_disponibles):
                            cursor.execute('''
                            INSERT INTO numeros_rifa (ahorrador_id, numero)
                            VALUES (?, ?)
                            ''', (ahorrador[0], numeros_disponibles[index]))
                            index += 1
            
            # Buscar o crear el ahorrador NATILLERA
            cursor.execute('SELECT id FROM ahorradores WHERE nombre = "NATILLERA"')
            natillera = cursor.fetchone()
            if not natillera:
                cursor.execute('''
                INSERT INTO ahorradores (nombre, documento) 
                VALUES ("NATILLERA", "NATILLERA")
                ''')
                natillera_id = cursor.lastrowid
            else:
                natillera_id = natillera[0]
            
            # Asignar números restantes a NATILLERA
            while index < len(numeros_disponibles):
                cursor.execute('''
                INSERT INTO numeros_rifa (ahorrador_id, numero)
                VALUES (?, ?)
                ''', (natillera_id, numeros_disponibles[index]))
                index += 1
            
            conn.commit()
            return True
        finally:
            conn.close()

    
    def obtener_numeros_asignados(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener primero los ahorradores normales
            cursor.execute('''
            SELECT a.nombre, GROUP_CONCAT(PRINTF('%02d', nr.numero)) as numeros
            FROM ahorradores a
            LEFT JOIN numeros_rifa nr ON a.id = nr.ahorrador_id
            WHERE a.nombre != 'NATILLERA'
            GROUP BY a.id, a.nombre
            ORDER BY a.nombre
            ''')
            resultados = cursor.fetchall()
            
            # Obtener números de NATILLERA separadamente
            cursor.execute('''
            SELECT nr.numero
            FROM ahorradores a
            JOIN numeros_rifa nr ON a.id = nr.ahorrador_id
            WHERE a.nombre = 'NATILLERA'
            ORDER BY RANDOM()
            ''')
            numeros_natillera = cursor.fetchall()
            
            # Procesar números de NATILLERA en grupos de 5
            if numeros_natillera:
                numeros = [str(n[0]).zfill(2) for n in numeros_natillera]  # Formatear a 2 dígitos
                grupos = [numeros[i:i + 5] for i in range(0, len(numeros), 5)]  # Dividir en grupos de 5
                
                # Añadir cada grupo como una fila separada, siempre con el nombre NATILLERA
                for grupo in grupos:
                    resultados.append(('NATILLERA', ', '.join(grupo)))
            
            return resultados
        finally:
            conn.close()


    def asignar_numeros_nuevo_ahorrador(self, ahorrador_id):
        """
        Asigna 3 números aleatorios de NATILLERA al nuevo ahorrador
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener ID de NATILLERA
            cursor.execute('SELECT id FROM ahorradores WHERE nombre = "NATILLERA"')
            natillera = cursor.fetchone()
            if not natillera:
                raise ValueError("No se encontró NATILLERA")
            
            # Obtener números disponibles de NATILLERA
            cursor.execute('''
            SELECT id, numero 
            FROM numeros_rifa 
            WHERE ahorrador_id = ? 
            ORDER BY RANDOM() 
            LIMIT 3''', (natillera[0],))
            
            numeros = cursor.fetchall()
            if len(numeros) < 3:
                raise ValueError("No hay suficientes números disponibles en NATILLERA")
            
            # Reasignar números al nuevo ahorrador
            for num_id, _ in numeros:
                cursor.execute('''
                UPDATE numeros_rifa 
                SET ahorrador_id = ? 
                WHERE id = ?''', (ahorrador_id, num_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def registrar_fecha_rifa(self, fecha, valor):
        """Registra una nueva fecha de rifa"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO fechas_rifa (fecha, valor)
            VALUES (?, ?)
            ''', (fecha, valor))
            
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def obtener_fechas_rifa(self):
        """Obtiene todas las fechas de rifa ordenadas por fecha"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT 
                fr.id,
                fr.fecha,
                fr.valor,
                fr.realizada,
                a.nombre as ganador,
                fr.numero_ganador
            FROM fechas_rifa fr
            LEFT JOIN ahorradores a ON fr.ganador_id = a.id
            ORDER BY fr.fecha
            ''')
            return cursor.fetchall()
        finally:
            conn.close()


    def registrar_ganador(self, fecha_id, ganador_id, numero_ganador):
        """
        Registra el ganador de una rifa específica
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que el número pertenezca al ganador
            cursor.execute('''
            SELECT COUNT(*) 
            FROM numeros_rifa 
            WHERE ahorrador_id = ? AND numero = ?
            ''', (ganador_id, int(numero_ganador)))
            
            if cursor.fetchone()[0] == 0:
                raise ValueError("El número ganador no pertenece al ahorrador seleccionado")
            
            # Registrar ganador
            cursor.execute('''
            UPDATE fechas_rifa 
            SET ganador_id = ?, 
                numero_ganador = ?,
                realizada = 1
            WHERE id = ?
            ''', (ganador_id, numero_ganador, fecha_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


    def obtener_datos_reporte_general(self):
        """Obtiene estadísticas generales para el reporte"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total rifas y estadísticas
            cursor.execute('''
            SELECT 
                COUNT(*) as total_rifas,
                SUM(CASE WHEN realizada = 1 THEN 1 ELSE 0 END) as rifas_realizadas,
                SUM(CASE WHEN realizada = 0 THEN 1 ELSE 0 END) as rifas_pendientes,
                SUM(valor) as total_premios
            FROM fechas_rifa
            ''')
            
            return cursor.fetchone()
        finally:
            conn.close()

    def obtener_historial_ganadores(self):
        """Obtiene el historial de todas las rifas con ganadores"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT 
                fr.fecha,
                fr.valor,
                a.nombre as ganador,
                fr.numero_ganador
            FROM fechas_rifa fr
            JOIN ahorradores a ON fr.ganador_id = a.id
            WHERE fr.realizada = 1
            ORDER BY fr.fecha DESC
            ''')
            
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_participantes_numeros(self):
        """Obtiene la lista de participantes con sus números y pagos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener ahorradores con sus números
            cursor.execute('''
            SELECT 
                a.nombre,
                GROUP_CONCAT(PRINTF('%02d', nr.numero)) as numeros,
                (SELECT COUNT(*) FROM rifas r WHERE r.ahorrador_id = a.id) as pagos_realizados
            FROM ahorradores a
            LEFT JOIN numeros_rifa nr ON a.id = nr.ahorrador_id
            WHERE a.nombre != 'NATILLERA'
            GROUP BY a.id
            ORDER BY a.nombre
            ''')
            
            return cursor.fetchall()
        finally:
            conn.close()