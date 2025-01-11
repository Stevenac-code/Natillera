# utils/pdf_generator.py
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class ReportGenerator:
    def __init__(self, db):
        self.db = db
        self.styles = getSampleStyleSheet()
        
    def generar_reporte_ahorrador(self, ahorrador_id, filename):
        from models.ahorrador import Ahorrador
        from models.ahorro import Ahorro
        from models.prestamo import Prestamo
        
        ahorrador_model = Ahorrador(self.db)
        ahorro_model = Ahorro(self.db)
        prestamo_model = Prestamo(self.db)
        
        # Obtener datos
        ahorrador = ahorrador_model.obtener_ahorrador(ahorrador_id)
        ahorros = ahorro_model.obtener_ahorros_ahorrador(ahorrador_id)
        prestamos = prestamo_model.listar_prestamos_ahorrador(ahorrador_id)
        saldo = ahorro_model.calcular_saldo(ahorrador_id)
        
        # Crear documento
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Reporte de Ahorrador - {ahorrador[1]}", title_style))
        
        # Información del ahorrador
        elements.append(Paragraph("Información Personal", self.styles['Heading2']))
        data = [
            ["Documento:", ahorrador[2]],
            ["Teléfono:", ahorrador[3]],
            ["Email:", ahorrador[4]],
            ["Fecha Registro:", ahorrador[5]],
            ["Saldo Actual:", f"${saldo:,.2f}"]
        ]
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Historial de ahorros
        if ahorros:
            elements.append(Paragraph("Historial de Ahorros", self.styles['Heading2']))
            data = [["Fecha", "Monto", "Tipo"]]
            for ahorro in ahorros:
                data.append([
                    ahorro[3],
                    f"${ahorro[2]:,.2f}",
                    ahorro[4].title()
                ])
            t = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))
        
        # Préstamos
        if prestamos:
            elements.append(Paragraph("Préstamos", self.styles['Heading2']))
            data = [["Fecha", "Monto", "Tasa", "Estado"]]
            for prestamo in prestamos:
                data.append([
                    prestamo[4],
                    f"${prestamo[2]:,.2f}",
                    f"{prestamo[3]}%",
                    prestamo[6].title()
                ])
            t = Table(data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            ]))
            elements.append(t)
        
        # Generar PDF
        doc.build(elements)
        return filename
    
    def generar_reporte_general(self, filename):
        from models.ahorrador import Ahorrador
        from models.ahorro import Ahorro
        from models.prestamo import Prestamo
        
        ahorrador_model = Ahorrador(self.db)
        ahorro_model = Ahorro(self.db)
        prestamo_model = Prestamo(self.db)
        
        # Obtener datos
        ahorradores = ahorrador_model.listar_ahorradores()
        
        # Crear documento
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Reporte General - {datetime.now().strftime('%Y-%m-%d')}", title_style))
        
        # Resumen por ahorrador
        elements.append(Paragraph("Resumen por Ahorrador", self.styles['Heading2']))
        data = [["Nombre", "Documento", "Saldo", "Préstamos Activos"]]
        
        total_ahorros = 0
        total_prestamos = 0
        
        for ahorrador in ahorradores:
            saldo = ahorro_model.calcular_saldo(ahorrador[0])
            prestamos = prestamo_model.listar_prestamos_ahorrador(ahorrador[0])
            prestamos_activos = sum(1 for p in prestamos if p[6] == 'activo')
            
            total_ahorros += saldo
            total_prestamos += prestamos_activos
            
            data.append([
                ahorrador[1],
                ahorrador[2],
                f"${saldo:,.2f}",
                prestamos_activos
            ])
        
        t = Table(data, colWidths=[2*inch, 2*inch, 2*inch, 1*inch])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Totales
        elements.append(Paragraph("Totales", self.styles['Heading2']))
        data = [
            ["Total Ahorradores:", len(ahorradores)],
            ["Total Ahorros:", f"${total_ahorros:,.2f}"],
            ["Total Préstamos Activos:", total_prestamos]
        ]
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(t)
        
        # Generar PDF
        doc.build(elements)
        return filename