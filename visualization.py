"""
Visualisierung der Schalsteinmauer mit Plotly (2D und 3D)
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import numpy as np


def create_2d_view(layout: Dict, stone_width_m: float) -> go.Figure:
    """
    Erstellt eine 2D-Ansicht der Mauer (Seitenansicht mit versetztem Mauerwerk)
    
    Args:
        layout: Layout-Dictionary von get_stone_layout()
        stone_width_m: Breite/Dicke des Steins in Metern
        
    Returns:
        Plotly Figure
    """
    stone_length = layout['stone_length_m']
    stone_height = layout['stone_height_m']
    stones_per_row = layout['stones_per_row']
    rows_start = layout['rows_start']
    rows_end = layout['rows_end']
    total_length = layout['total_length']
    
    # Berechne Gefälle pro Meter
    height_diff = layout['start_height'] - layout['end_height']
    slope = height_diff / total_length if total_length > 0 else 0
    
    # Erstelle Rechtecke für jeden Stein
    shapes = []
    annotations = []
    
    stone_count = 0
    
    # Für jede Position entlang der Länge
    for row in range(max(rows_start, rows_end)):
        # Berechne Höhe dieser Reihe am Anfang
        current_height_at_start = row * stone_height
        
        # Prüfe ob diese Reihe am Ende noch existiert
        current_height_at_end = row * stone_height
        
        # Versatz für ungerade Reihen (halbsteinversetzt)
        offset = stone_length / 2 if row % 2 == 1 else 0
        
        # Steine in dieser Reihe
        for stone_idx in range(stones_per_row + 1):  # +1 für Versatz
            x_start = stone_idx * stone_length - offset
            x_end = x_start + stone_length
            
            # Prüfe ob Stein außerhalb der Mauer liegt
            if x_start >= total_length or x_end < 0:
                continue
            
            # Clip an Mauergrenzen
            x_start = max(0, x_start)
            x_end = min(total_length, x_end)
            
            # Berechne Höhe an dieser Position
            x_mid = (x_start + x_end) / 2
            max_height_at_position = layout['start_height'] - slope * x_mid
            
            # Prüfe ob diese Reihe an dieser Position existiert
            if current_height_at_start >= max_height_at_position:
                continue
            
            y_bottom = row * stone_height
            y_top = y_bottom + stone_height
            
            # Stein als Rechteck hinzufügen
            shapes.append({
                'type': 'rect',
                'x0': x_start,
                'y0': y_bottom,
                'x1': x_end,
                'y1': y_top,
                'line': {'color': 'black', 'width': 1},
                'fillcolor': 'lightgray',
                'opacity': 0.8
            })
            
            stone_count += 1
    
    # Erstelle Figure
    fig = go.Figure()
    
    # Füge unsichtbare Trace hinzu für Achsen
    fig.add_trace(go.Scatter(
        x=[0, total_length],
        y=[0, max(layout['start_height'], layout['end_height'])],
        mode='markers',
        marker={'size': 0.1, 'color': 'rgba(0,0,0,0)'},
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Füge Shapes hinzu
    fig.update_layout(
        shapes=shapes,
        title={
            'text': f'Seitenansicht der Mauer (versetztes Mauerwerk)<br><sub>ca. {stone_count} Steine sichtbar</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': 'Länge (m)',
            'showgrid': True,
            'zeroline': True,
            'range': [-0.1, total_length + 0.1]
        },
        yaxis={
            'title': 'Höhe (m)',
            'showgrid': True,
            'zeroline': True,
            'scaleanchor': 'x',
            'scaleratio': 1,
            'range': [-0.1, max(layout['start_height'], layout['end_height']) + 0.1]
        },
        width=900,
        height=500,
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig


def create_3d_view(layout: Dict, stone_width_m: float) -> go.Figure:
    """
    Erstellt eine 3D-Ansicht der Mauer mit einzelnen Steinen als Quader
    
    Args:
        layout: Layout-Dictionary von get_stone_layout()
        stone_width_m: Breite/Dicke des Steins in Metern
        
    Returns:
        Plotly Figure
    """
    stone_length = layout['stone_length_m']
    stone_height = layout['stone_height_m']
    stone_width = stone_width_m
    stones_per_row = layout['stones_per_row']
    rows_start = layout['rows_start']
    rows_end = layout['rows_end']
    total_length = layout['total_length']
    
    # Berechne Gefälle
    height_diff = layout['start_height'] - layout['end_height']
    slope = height_diff / total_length if total_length > 0 else 0
    
    # Performance-Warnung
    max_stones = max(rows_start, rows_end) * (stones_per_row + 1)
    
    # Sammle alle Quader
    all_vertices = []
    all_faces_i = []
    all_faces_j = []
    all_faces_k = []
    
    vertex_offset = 0
    stone_count = 0
    
    # Begrenze Anzahl für Performance
    max_stones_to_render = 800
    
    for row in range(max(rows_start, rows_end)):
        current_height = row * stone_height
        
        # Versatz für ungerade Reihen
        offset = stone_length / 2 if row % 2 == 1 else 0
        
        for stone_idx in range(stones_per_row + 1):
            if stone_count >= max_stones_to_render:
                break
                
            x_start = stone_idx * stone_length - offset
            x_end = x_start + stone_length
            
            # Prüfe Grenzen
            if x_start >= total_length or x_end < 0:
                continue
            
            x_start = max(0, x_start)
            x_end = min(total_length, x_end)
            
            # Höhe an dieser Position
            x_mid = (x_start + x_end) / 2
            max_height_at_position = layout['start_height'] - slope * x_mid
            
            if current_height >= max_height_at_position:
                continue
            
            # Quader-Eckpunkte
            z_bottom = current_height
            z_top = z_bottom + stone_height
            
            # 8 Eckpunkte des Quaders
            vertices = [
                [x_start, 0, z_bottom],           # 0: vorne unten links
                [x_end, 0, z_bottom],              # 1: vorne unten rechts
                [x_end, stone_width, z_bottom],    # 2: hinten unten rechts
                [x_start, stone_width, z_bottom],  # 3: hinten unten links
                [x_start, 0, z_top],               # 4: vorne oben links
                [x_end, 0, z_top],                 # 5: vorne oben rechts
                [x_end, stone_width, z_top],       # 6: hinten oben rechts
                [x_start, stone_width, z_top]      # 7: hinten oben links
            ]
            
            all_vertices.extend(vertices)
            
            # Definiere die 6 Flächen des Quaders (als Dreiecke)
            # Jede Fläche besteht aus 2 Dreiecken
            base = vertex_offset
            
            faces = [
                # Unterseite (z-)
                [base+0, base+1, base+2], [base+0, base+2, base+3],
                # Oberseite (z+)
                [base+4, base+6, base+5], [base+4, base+7, base+6],
                # Vorderseite (y-)
                [base+0, base+4, base+5], [base+0, base+5, base+1],
                # Rückseite (y+)
                [base+2, base+6, base+7], [base+2, base+7, base+3],
                # Linke Seite (x-)
                [base+0, base+3, base+7], [base+0, base+7, base+4],
                # Rechte Seite (x+)
                [base+1, base+5, base+6], [base+1, base+6, base+2]
            ]
            
            for face in faces:
                all_faces_i.append(face[0])
                all_faces_j.append(face[1])
                all_faces_k.append(face[2])
            
            vertex_offset += 8
            stone_count += 1
        
        if stone_count >= max_stones_to_render:
            break
    
    # Konvertiere zu numpy arrays
    vertices_array = np.array(all_vertices)
    
    # Erstelle 3D Mesh
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices_array[:, 0],
            y=vertices_array[:, 1],
            z=vertices_array[:, 2],
            i=all_faces_i,
            j=all_faces_j,
            k=all_faces_k,
            color='lightgray',
            opacity=0.9,
            flatshading=True,
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                specular=0.2,
                roughness=0.5
            ),
            lightposition=dict(x=100, y=200, z=300),
            hoverinfo='skip'
        )
    ])
    
    # Layout
    max_height = max(layout['start_height'], layout['end_height'])
    
    title_text = f'3D-Ansicht der Mauer (versetztes Mauerwerk)'
    if stone_count >= max_stones_to_render:
        title_text += f'<br><sub>Zeigt {stone_count} Steine (begrenzt für Performance)</sub>'
    else:
        title_text += f'<br><sub>{stone_count} Steine</sub>'
    
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center'
        },
        scene=dict(
            xaxis=dict(title='Länge (m)', backgroundcolor="white", gridcolor="lightgray"),
            yaxis=dict(title='Breite (m)', backgroundcolor="white", gridcolor="lightgray"),
            zaxis=dict(title='Höhe (m)', backgroundcolor="white", gridcolor="lightgray"),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


def create_top_view(layout: Dict, stone_width_m: float) -> go.Figure:
    """
    Erstellt eine Draufsicht der Mauer (optional, zusätzlich)
    
    Args:
        layout: Layout-Dictionary
        stone_width_m: Breite des Steins
        
    Returns:
        Plotly Figure
    """
    stone_length = layout['stone_length_m']
    total_length = layout['total_length']
    
    fig = go.Figure()
    
    # Mauer als Rechteck von oben
    fig.add_trace(go.Scatter(
        x=[0, total_length, total_length, 0, 0],
        y=[0, 0, stone_width_m, stone_width_m, 0],
        fill='toself',
        fillcolor='lightgray',
        line={'color': 'black', 'width': 2},
        mode='lines',
        name='Mauer',
        hoverinfo='text',
        text=f'Mauer: {total_length:.2f} m × {stone_width_m:.2f} m'
    ))
    
    fig.update_layout(
        title={
            'text': 'Draufsicht der Mauer',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': 'Länge (m)',
            'showgrid': True,
            'scaleanchor': 'y',
            'scaleratio': 1
        },
        yaxis={
            'title': 'Breite (m)',
            'showgrid': True
        },
        width=900,
        height=300,
        plot_bgcolor='white'
    )
    
    return fig


def should_show_performance_warning(layout: Dict) -> Tuple[bool, str]:
    """
    Prüft ob eine Performance-Warnung angezeigt werden soll
    
    Returns:
        (show_warning, message)
    """
    stones_per_row = layout['stones_per_row']
    rows = max(layout['rows_start'], layout['rows_end'])
    estimated_stones = stones_per_row * rows
    
    if estimated_stones > 500:
        return True, (
            f"⚠️ **Performance-Hinweis:** Die Mauer hat ca. {estimated_stones} Steine. "
            "Die 3D-Ansicht kann bei sehr großen Mauern langsam laden. "
            "Die 2D-Ansicht ist deutlich schneller."
        )
    
    return False, ""


