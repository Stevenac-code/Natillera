# src/models/ahorrador.py
import sqlite3

class Ahorrador:
    def __init__(self, db):
        self.db = db
    
    def crear_ahorrador(self, nombre, documento, telefono=None, email=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO ahorradores (nombre, documento, telefono, email)
            VALUES (?, ?, ?, ?)
            ''', (nombre, documento, telefono, email))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("El documento ya existe en la base de datos")
        finally:
            conn.close()
    
    def obtener_ahorrador(self, id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM ahorradores WHERE id = ?', (id,))
        ahorrador = cursor.fetchone()
        conn.close()
        
        return ahorrador if ahorrador else None
    
    def listar_ahorradores(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM ahorradores ORDER BY nombre')
        ahorradores = cursor.fetchall()
        conn.close()
        
        return ahorradores

    def actualizar_ahorrador(self, id, nombre=None, telefono=None, email=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if nombre:
            updates.append("nombre = ?")
            values.append(nombre)
        if telefono:
            updates.append("telefono = ?")
            values.append(telefono)
        if email:
            updates.append("email = ?")
            values.append(email)
            
        if not updates:
            return False
            
        values.append(id)
        query = f"UPDATE ahorradores SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0