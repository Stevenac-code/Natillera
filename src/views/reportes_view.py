# views/reportes_view.py
import os
import tkinter as tk
from datetime import datetime
from reportlab.lib import colors
from src.models.rifa import Rifa
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class ReportesView:
    def __init__(self, parent_frame, ahorrador_model, ahorro_model, prestamo_model):
        self.frame = parent_frame
        self.ahorrador_model = ahorrador_model
        self.ahorro_model = ahorro_model
        self.prestamo_model = prestamo_model
        self.rifa_model = Rifa(self.ahorro_model.db)
        
        # Crear carpeta 'reportes' si no existe
        self.reports_dir = 'reportes'
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        
        self.create_view()
    
    
    def create_view(self):
        # Frame principal para reportes
        ttk.Label(self.frame, text="Generación de Reportes", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Frame para selección de ahorrador
        selection_frame = ttk.LabelFrame(self.frame, text="Seleccionar Ahorrador")
        selection_frame.pack(padx=10, pady=5, fill='x')
        
        ttk.Label(selection_frame, text="Ahorrador:").pack(side=tk.LEFT, padx=5)
        self.ahorrador_combo = ttk.Combobox(selection_frame)
        self.ahorrador_combo.pack(side=tk.LEFT, padx=5)
        self.actualizar_lista_ahorradores()
        
        # Frame para botones de reportes
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Estado de Cuenta Detallado Por Persona", 
                command=self.generar_estado_cuenta_detallado).pack(pady=5)
        ttk.Button(buttons_frame, text="Estado de Cuenta Detallado Ahorradores", 
                command=self.generar_estado_cuenta_detallado_todos).pack(pady=5)
        ttk.Button(buttons_frame, text="Reporte Control de Rifas", 
               command=self.generar_reporte_rifas).pack(pady=5)
    
    
    def actualizar_lista_ahorradores(self):
        ahorradores = self.ahorrador_model.listar_ahorradores()
        self.ahorrador_combo['values'] = [f"{a[1]} - {a[2]}" for a in ahorradores]
        self.ahorradores_data = {f"{a[1]} - {a[2]}": a[0] for a in ahorradores}
    
    def get_ahorrador_seleccionado(self):
        seleccion = self.ahorrador_combo.get()
        if not seleccion:
            raise ValueError("Debe seleccionar un ahorrador")
        return self.ahorradores_data[seleccion]
    
    def seleccionar_ruta_guardado(self, default_name):
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{default_name}_{timestamp}.pdf"
        # Crear ruta completa en la carpeta reportes
        return os.path.join(self.reports_dir, filename)    


    def generar_estado_cuenta_detallado(self):
        try:
            ahorrador_id = self.get_ahorrador_seleccionado()
            ahorrador = self.ahorrador_model.obtener_ahorrador(ahorrador_id)
            
            filename = self.seleccionar_ruta_guardado(f"estado_cuenta_detallado_{ahorrador[1]}_{ahorrador[2]}.pdf")
            if not filename:
                return
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']
            
            elements.append(Paragraph(f"Estado de Cuenta Detallado - {ahorrador[1]}", title_style))
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("Información del Ahorrador", subtitle_style))
            elements.append(Paragraph(f"Documento: {ahorrador[2]}", normal_style))
            elements.append(Paragraph(f"Teléfono: {ahorrador[3] or 'No registrado'}", normal_style))
            elements.append(Paragraph(f"Email: {ahorrador[4] or 'No registrado'}", normal_style))
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("Detalle de Ahorros", subtitle_style))
            ahorros = self.ahorro_model.obtener_ahorros_ahorrador(ahorrador_id)
            if ahorros:
                data = [['Fecha', 'Tipo', 'Monto']]
                for ahorro in ahorros:
                    data.append([
                        str(ahorro[3]),
                        str(ahorro[4]).title(),
                        "${:,.2f}".format(float(ahorro[2]))
                    ])
                
                saldo = self.ahorro_model.calcular_saldo(ahorrador_id)
                data.append(['', 'Saldo Total:', "${:,.2f}".format(float(saldo))])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            else:
                elements.append(Paragraph("No hay registros de ahorros", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Detalle de préstamos y pagos
            elements.append(Paragraph("Detalle de Préstamos y Pagos", subtitle_style))
            prestamos = self.prestamo_model.listar_prestamos_ahorrador(ahorrador_id)
            if prestamos:
                for prestamo in prestamos:
                    elements.append(Paragraph(f"Préstamo ID: {prestamo[0]}", subtitle_style))
                    
                    # Tabla del préstamo
                    data = [['Fecha Préstamo', 'Monto Préstamo', 'Tasa', 'Estado', 'Saldo Actual']]
                    
                    try:
                        data.append([
                            str(prestamo[4]),  # fecha_prestamo
                            "${:,.2f}".format(float(prestamo[2])),  # monto
                            "{:.1f}%".format(float(prestamo[3])),  # tasa_interes
                            str(prestamo[5]).title(),  # estado
                            "${:,.2f}".format(float(prestamo[6])) if prestamo[6] is not None else "${:,.2f}".format(float(prestamo[2]))  # saldo_actual
                        ])
                        
                        table = Table(data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 10))
                        
                        # Historial de pagos
                        pagos = self.prestamo_model.obtener_historial_pagos(prestamo[0])
                        if pagos:
                            data = [['Fecha', 'Tipo de Pago', 'Monto', 'Saldo Restante']]
                            for pago in pagos:
                                data.append([
                                    str(pago[1]),  # fecha
                                    str(pago[2]).replace('interes', 'Interés').replace('abono', 'Abono'),  # tipo
                                    "${:,.2f}".format(float(pago[3])),  # monto
                                    "${:,.2f}".format(float(pago[4]))  # saldo_restante
                                ])
                            
                            table = Table(data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ]))
                            elements.append(table)
                        else:
                            elements.append(Paragraph("No se han realizado pagos para este préstamo", normal_style))
                        
                    except Exception as e:
                        print(f"Error procesando préstamo {prestamo[0]}: {str(e)}")
                        continue
                        
                    elements.append(Spacer(1, 20))
            else:
                elements.append(Paragraph("No hay registros de préstamos", normal_style))
            
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            
            doc.build(elements)
            messagebox.showinfo("Éxito", "Estado de cuenta detallado generado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def generar_estado_cuenta_detallado_todos(self):
        try:
            filename = self.seleccionar_ruta_guardado("estado_cuenta_detallado_todos.pdf")
            if not filename:
                return
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']
            
            elements.append(Paragraph("Estado de Cuenta Detallado - Todos los Ahorradores", title_style))
            elements.append(Spacer(1, 20))
            
            ahorradores = self.ahorrador_model.listar_ahorradores()
            
            for ahorrador in ahorradores:
                ahorrador_id = ahorrador[0]
                
                elements.append(Paragraph(f"Ahorrador: {ahorrador[1]}", subtitle_style))
                elements.append(Paragraph(f"Documento: {ahorrador[2]}", normal_style))
                elements.append(Paragraph(f"Teléfono: {ahorrador[3] or 'No registrado'}", normal_style))
                elements.append(Paragraph(f"Email: {ahorrador[4] or 'No registrado'}", normal_style))
                elements.append(Spacer(1, 20))
                
                elements.append(Paragraph("Detalle de Ahorros", subtitle_style))
                ahorros = self.ahorro_model.obtener_ahorros_ahorrador(ahorrador_id)
                if ahorros:
                    data = [['Fecha', 'Tipo', 'Monto']]
                    for ahorro in ahorros:
                        data.append([
                            str(ahorro[3]),
                            str(ahorro[4]).title(),
                            "${:,.2f}".format(float(ahorro[2]))
                        ])
                    
                    saldo = self.ahorro_model.calcular_saldo(ahorrador_id)
                    data.append(['', 'Saldo Total:', "${:,.2f}".format(float(saldo))])
                    
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    elements.append(table)
                else:
                    elements.append(Paragraph("No hay registros de ahorros", normal_style))
                
                elements.append(Spacer(1, 20))
                
                elements.append(Paragraph("Detalle de Préstamos y Pagos", subtitle_style))
                prestamos = self.prestamo_model.listar_prestamos_ahorrador(ahorrador_id)
                if prestamos:
                    for prestamo in prestamos:
                        elements.append(Paragraph(f"Préstamo ID: {prestamo[0]}", subtitle_style))
                        
                        # Tabla del préstamo
                        data = [['Fecha Préstamo', 'Monto Préstamo', 'Tasa', 'Estado', 'Saldo Actual']]
                        
                        try:
                            data.append([
                                str(prestamo[4]),  # fecha_prestamo
                                "${:,.2f}".format(float(prestamo[2])),  # monto
                                "{:.1f}%".format(float(prestamo[3])),  # tasa_interes
                                str(prestamo[5]).title(),  # estado
                                "${:,.2f}".format(float(prestamo[6])) if prestamo[6] is not None else "${:,.2f}".format(float(prestamo[2]))  # saldo_actual
                            ])
                            
                            table = Table(data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 10))
                            
                            # Historial de pagos
                            pagos = self.prestamo_model.obtener_historial_pagos(prestamo[0])
                            if pagos and len(pagos) > 0:
                                data = [['Fecha', 'Tipo de Pago', 'Monto', 'Saldo Restante']]
                                for pago in pagos:
                                    data.append([
                                        str(pago[0]),  # fecha
                                        str(pago[1]).replace('interes', 'Interés').replace('abono', 'Abono'),  # tipo
                                        "${:,.2f}".format(float(pago[2])),  # monto
                                        "${:,.2f}".format(float(pago[3]))  # saldo_restante
                                    ])
                                
                                table = Table(data)
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ]))
                                elements.append(table)
                            else:
                                elements.append(Paragraph("No se han realizado pagos para este préstamo", normal_style))
                            
                        except Exception as e:
                            print(f"Error procesando préstamo {prestamo[0]}: {str(e)}")
                            continue
                            
                        elements.append(Spacer(1, 20))
                else:
                    elements.append(Paragraph("No hay registros de préstamos", normal_style))
                
                elements.append(Spacer(1, 30))
                elements.append(Paragraph("_" * 50, normal_style))
                elements.append(Spacer(1, 30))
            
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            
            doc.build(elements)
            messagebox.showinfo("Éxito", "Estado de cuenta detallado de todos los ahorradores generado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def generar_reporte_rifas(self):
        try:
            # Crear nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join('reportes', f"reporte_rifas_{timestamp}.pdf")
            
            # Crear el documento
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Título
            elements.append(Paragraph(f"Control de Rifas {datetime.now().year}", title_style))
            elements.append(Spacer(1, 20))
            
            # Estadísticas generales
            stats = self.rifa_model.obtener_datos_reporte_general()
            if stats:
                elements.append(Paragraph("Estado Actual", subtitle_style))
                elements.append(Paragraph(f"Total de rifas programadas: {stats[0]}", normal_style))
                elements.append(Paragraph(f"Rifas realizadas: {stats[1]}", normal_style))
                elements.append(Paragraph(f"Rifas pendientes: {stats[2]}", normal_style))
                elements.append(Paragraph(f"Valor total en premios: ${stats[3]:,.2f}", normal_style))
                elements.append(Spacer(1, 20))
            
            # Calendario de Rifas
            elements.append(Paragraph("Calendario de Rifas", subtitle_style))
            fechas = self.rifa_model.obtener_fechas_rifa()
            if fechas:
                data = [['Fecha', 'Valor Premio', 'Estado', 'Ganador', 'Número']]
                for fecha in fechas:
                    data.append([
                        fecha[1],
                        f"${fecha[2]:,.2f}",
                        "Realizada" if fecha[3] else "Pendiente",
                        fecha[4] or "No asignado",
                        fecha[5] or "N/A"
                    ])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))
            
            # Lista de Participantes
            elements.append(Paragraph("Lista de Participantes", subtitle_style))
            participantes = self.rifa_model.obtener_participantes_numeros()
            if participantes:
                data = [['Ahorrador', 'Números Asignados', 'Pagos Realizados']]
                for part in participantes:
                    numeros = part[1].split(',') if part[1] else []
                    numeros_fmt = ' - '.join(numeros)
                    data.append([
                        part[0],
                        numeros_fmt,
                        str(part[2])
                    ])
                
                table = Table(data, colWidths=[120, 300, 100])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))
            
            # Historial de Ganadores
            elements.append(Paragraph("Historial de Ganadores", subtitle_style))
            ganadores = self.rifa_model.obtener_historial_ganadores()
            if ganadores:
                data = [['Fecha', 'Premio', 'Ganador', 'Número Ganador']]
                for gan in ganadores:
                    data.append([
                        str(gan[0]),
                        f"${gan[1]:,.2f}",
                        gan[2],
                        gan[3]
                    ])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            
            # Fecha de generación
            elements.append(Spacer(1, 30))
            elements.append(Paragraph(
                f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                normal_style))
            
            # Generar PDF
            doc.build(elements)
            messagebox.showinfo("Éxito", "Reporte generado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
