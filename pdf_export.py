"""
PDF-Export Funktionalität für Schalsteinmauer Betonrechner
Erstellt professionelle PDF-Berichte mit allen Berechnungen
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from io import BytesIO
import plotly.graph_objects as go
from typing import Dict
import tempfile
import os


def create_pdf_report(result: Dict, inputs: Dict, fig_2d: go.Figure = None) -> BytesIO:
    """
    Erstellt einen PDF-Bericht mit allen Berechnungsergebnissen
    
    Args:
        result: Berechnungsergebnisse von calculate_all()
        inputs: Dictionary mit Eingabewerten
        fig_2d: Optional Plotly 2D Figure für Visualisierung
        
    Returns:
        BytesIO mit PDF-Daten
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Container für Elemente
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Titel
    elements.append(Paragraph("🧱 Schalsteinmauer Betonrechner", title_style))
    elements.append(Paragraph("Berechnungsbericht", styles['Heading3']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Eingabedaten
    elements.append(Paragraph("Mauer-Dimensionen", heading_style))
    
    input_data = [
        ['Parameter', 'Wert'],
        ['Länge', f"{inputs['length']} m"],
        ['Anfangshöhe', f"{inputs['start_height']} m"],
        ['Endhöhe', f"{inputs['end_height']} m"],
        ['Breite/Dicke', f"{inputs['width']} cm"],
    ]
    
    input_table = Table(input_data, colWidths=[8*cm, 8*cm])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(input_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Schalstein-Daten
    elements.append(Paragraph("Gewählter Schalstein", heading_style))
    
    stone_data = result['stone_data']
    stone_info = [
        ['Eigenschaft', 'Wert'],
        ['Typ', stone_data['name']],
        ['Maße (L × B × H)', f"{stone_data['length_cm']} × {stone_data['width_cm']} × {stone_data['height_cm']} cm"],
        ['Gewicht', f"{stone_data['weight_kg']} kg"],
        ['Bedarf', f"{stone_data['stones_per_m2']} St./m²"],
        ['Füllvolumen pro Stein', f"{stone_data['fill_volume_per_stone_liters']:.2f} L"],
    ]
    
    stone_table = Table(stone_info, colWidths=[8*cm, 8*cm])
    stone_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(stone_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Berechnungsergebnisse
    elements.append(Paragraph("Berechnungsergebnisse", heading_style))
    
    calc_data = [
        ['Kennwert', 'Wert'],
        ['Mauerfläche', f"{result['area']} m²"],
        ['Anzahl Steine', f"{result['total_stones']} St."],
        ['Anzahl Reihen', f"{result['rows']}"],
        ['Grundvolumen (Hohlräume)', f"{result['base_volume_m3']} m³"],
        ['Puffer', f"{result['buffer_percentage']}%"],
        ['Volumen mit Puffer', f"{result['volume_with_buffer_m3']} m³"],
    ]
    
    calc_table = Table(calc_data, colWidths=[10*cm, 6*cm])
    calc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(calc_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Materialien
    elements.append(Paragraph("Materialbedarf", heading_style))
    
    materials = result['materials']
    mat_data = [
        ['Material', 'Menge', 'Einheit'],
        ['Zement', f"{materials['cement_bags']}", f"Säcke à {materials['cement_bag_size_kg']} kg"],
        ['', f"{materials['cement_kg']}", 'kg'],
        ['Kies (Rundkies 0-16 mm)', f"{materials['gravel_tons']}", 'Tonnen'],
        ['', f"{materials['gravel_kg']}", 'kg'],
        ['Wasser', f"{materials['water_liters']}", 'Liter'],
    ]
    
    mat_table = Table(mat_data, colWidths=[8*cm, 4*cm, 4*cm])
    mat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (0, 3), (0, 4)),
    ]))
    
    elements.append(mat_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Kosten (falls verfügbar)
    if result.get('costs'):
        elements.append(Paragraph("Kostenschätzung", heading_style))
        
        costs = result['costs']
        cost_data = [
            ['Position', 'Kosten'],
            ['Zement', f"{costs['cement_cost']:.2f} €"],
            ['Kies', f"{costs['gravel_cost']:.2f} €"],
            ['Gesamt', f"{costs['total_cost']:.2f} €"],
        ]
        
        cost_table = Table(cost_data, colWidths=[10*cm, 6*cm])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe4b5')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffd700')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(cost_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # Visualisierung (falls bereitgestellt)
    if fig_2d:
        try:
            # Speichere Plotly Figure als Bild
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                fig_2d.write_image(tmp_file.name, width=800, height=400)
                tmp_filename = tmp_file.name
            
            elements.append(PageBreak())
            elements.append(Paragraph("Visualisierung", heading_style))
            elements.append(Image(tmp_filename, width=16*cm, height=8*cm))
            elements.append(Spacer(1, 0.5*cm))
            
            # Lösche temporäre Datei
            try:
                os.unlink(tmp_filename)
            except:
                pass
        except Exception as e:
            # Falls Plotly-Export fehlschlägt, ignorieren
            elements.append(Paragraph(f"Visualisierung konnte nicht exportiert werden.", normal_style))
    
    # Betonempfehlung
    elements.append(PageBreak())
    elements.append(Paragraph("Betonempfehlung nach FCN", heading_style))
    rec_text = result['concrete_recommendation'].replace('**', '')
    elements.append(Paragraph(rec_text, normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Disclaimer
    elements.append(Paragraph("Wichtiger Hinweis", heading_style))
    disclaimer_text = result['disclaimer'].replace('⚠️ **Wichtiger Hinweis:**', '').replace('**', '').strip()
    disclaimer_para = Paragraph(disclaimer_text, normal_style)
    elements.append(disclaimer_para)
    
    # Footer
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Erstellt mit Schalsteinmauer Betonrechner | Basierend auf FCN-Spezifikationen", footer_style))
    
    # Generiere PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def get_pdf_button_html() -> str:
    """
    Gibt HTML für einen schönen PDF-Button zurück
    
    Returns:
        HTML string
    """
    return """
    <style>
    .pdf-button {
        background-color: #e74c3c;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .pdf-button:hover {
        background-color: #c0392b;
    }
    </style>
    """


