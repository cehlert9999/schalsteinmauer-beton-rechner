"""
Schalsteinmauer Betonrechner
Streamlit Web-Anwendung

Berechnet Betonbedarf für Schalsteinmauern basierend auf FCN-Spezifikationen
"""

import streamlit as st
import yaml
from calculations import (
    load_config, calculate_all, validate_inputs,
    get_height_warnings, get_concrete_recommendation, get_disclaimer
)
from visualization import (
    create_2d_view, create_3d_view, create_top_view,
    should_show_performance_warning
)
from pdf_export import create_pdf_report

# Seiten-Konfiguration
st.set_page_config(
    page_title="MauerPlaner - Betonbedarfsrechner by LEANOFY",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://leanofy.de/impressum',
        'Report a bug': 'https://leanofy.de/impressum',
        'About': '''
        **MauerPlaner** - Betonbedarfsrechner für Schalsteinmauern
        
        Ein Service von LEANOFY
        
        Berechnet präzise den Materialbedarf für Ihre Schalsteinmauer.
        '''
    }
)

# Titel mit Branding
st.title("🧱 MauerPlaner")
st.markdown("**Betonbedarfsrechner für Schalsteinmauern** | *by LEANOFY*")
st.caption("Präzise Berechnung basierend auf FCN-Spezifikationen")

# Lade Konfiguration
config = load_config()

# Sidebar - Eingaben
st.sidebar.header("⚙️ Eingaben")

# Template-Auswahl (Niedrige Priorität)
st.sidebar.subheader("Vorlage auswählen (optional)")
template_options = ["Keine Vorlage"] + [
    f"{key}: {data['name']}" 
    for key, data in config['templates'].items()
]
selected_template = st.sidebar.selectbox(
    "Vorlage",
    template_options,
    help="Wählen Sie eine Vorlage für schnellen Start"
)

# Parse Template
template_data = None
if selected_template != "Keine Vorlage":
    template_key = selected_template.split(":")[0]
    template_data = config['templates'][template_key]
    st.sidebar.info(f"📋 {template_data['description']}")

# Stein-Auswahl ZUERST (für diskrete Höhenschritte)
st.sidebar.subheader("🧱 Schalstein-Typ")

# Finde Default-Stein oder aus Template
default_stone_key = None
if template_data:
    default_stone_key = template_data['stone_type']
else:
    for key, stone in config['stone_types'].items():
        if stone.get('default', False):
            default_stone_key = key
            break

# Radio-Buttons für Steintypen
stone_type_options = {}
for key, stone in config['stone_types'].items():
    label = f"{stone['name']}\n" \
            f"└ {stone['length_cm']} × {stone['width_cm']} × {stone['height_cm']} cm, " \
            f"{stone['weight_kg']} kg\n" \
            f"└ Füllvolumen: {stone['fill_volume_per_stone_liters']:.2f} L/Stein"
    stone_type_options[label] = key

selected_stone_label = st.sidebar.radio(
    "Schalstein auswählen:",
    list(stone_type_options.keys()),
    index=list(stone_type_options.values()).index(default_stone_key),
    help="Wählen Sie den FCN Schalstein-Typ"
)

selected_stone_type = stone_type_options[selected_stone_label]
selected_stone_data = config['stone_types'][selected_stone_type]

# Steinhöhe für diskrete Schritte
stone_height_m = selected_stone_data['height_cm'] / 100  # z.B. 0.248 m

st.sidebar.markdown("---")

# Wand-Dimensionen
st.sidebar.subheader("🏗️ Mauer-Dimensionen")

# Mauer-Typ Auswahl
wall_type = st.sidebar.radio(
    "Mauer-Typ",
    ["Einfach (durchgehend)", "Zweizonen (flach + variabel)"],
    help="Einfach: Gleichmäßige Mauer. Zweizonen: Flacher Bereich + ansteigender/abfallender Bereich"
)

if template_data:
    default_length = template_data['wall_length_m']
    default_start = template_data['wall_start_height_m']
    default_end = template_data['wall_end_height_m']
    default_width = template_data['wall_width_cm']
else:
    default_length = config['defaults']['wall_length_m']
    default_start = config['defaults']['wall_start_height_m']
    default_end = config['defaults']['wall_end_height_m']
    default_width = config['defaults']['wall_width_cm']

# Einfache Mauer (wie bisher)
if wall_type == "Einfach (durchgehend)":
    length = st.sidebar.number_input(
        "Länge (m)",
        min_value=0.1,
        max_value=100.0,
        value=float(default_length),
        step=0.5,
        help="Länge der Mauer in Metern"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_height = st.sidebar.number_input(
            "Anfangshöhe (m)",
            min_value=stone_height_m,
            max_value=5.0,
            value=round(float(default_start) / stone_height_m) * stone_height_m,
            step=stone_height_m,
            format="%.3f",
            help=f"Höhe in Steinreihen (1 Reihe = {stone_height_m:.3f} m)"
        )
        # Zeige Anzahl Reihen
        rows_start = int(round(start_height / stone_height_m))
        st.sidebar.caption(f"≈ {rows_start} Reihen")
    
    with col2:
        end_height = st.sidebar.number_input(
            "Endhöhe (m)",
            min_value=stone_height_m,
            max_value=5.0,
            value=round(float(default_end) / stone_height_m) * stone_height_m,
            step=stone_height_m,
            format="%.3f",
            help=f"Höhe in Steinreihen (1 Reihe = {stone_height_m:.3f} m)"
        )
        # Zeige Anzahl Reihen
        rows_end = int(round(end_height / stone_height_m))
        st.sidebar.caption(f"≈ {rows_end} Reihen")
    
    # Flags für Berechnung
    is_two_zone = False
    zone1_length = None
    zone1_height = None
    zone2_length = None
    zone2_end_height = None

# Zweizonen-Mauer
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📏 Zone 1 (Flacher Bereich)**")
    
    zone1_length = st.sidebar.number_input(
        "Länge Zone 1 (m)",
        min_value=0.1,
        max_value=100.0,
        value=float(default_length) / 2,
        step=0.5,
        help="Länge des flachen Bereichs"
    )
    
    zone1_height = st.sidebar.number_input(
        "Höhe Zone 1 (m)",
        min_value=stone_height_m,
        max_value=5.0,
        value=round(float(default_start) / stone_height_m) * stone_height_m,
        step=stone_height_m,
        format="%.3f",
        help=f"Konstante Höhe (1 Reihe = {stone_height_m:.3f} m)"
    )
    rows_z1 = int(round(zone1_height / stone_height_m))
    st.sidebar.caption(f"≈ {rows_z1} Reihen")
    
    st.sidebar.markdown("**📐 Zone 2 (Variabler Bereich)**")
    
    zone2_length = st.sidebar.number_input(
        "Länge Zone 2 (m)",
        min_value=0.1,
        max_value=100.0,
        value=float(default_length) / 2,
        step=0.5,
        help="Länge des ansteigenden/abfallenden Bereichs"
    )
    
    st.sidebar.info(f"💡 Zone 2 startet bei {zone1_height:.3f} m ({rows_z1} Reihen)")
    
    zone2_end_height = st.sidebar.number_input(
        "Endhöhe Zone 2 (m)",
        min_value=stone_height_m,
        max_value=5.0,
        value=round(float(default_end) / stone_height_m) * stone_height_m,
        step=stone_height_m,
        format="%.3f",
        help=f"Höhe am Ende (1 Reihe = {stone_height_m:.3f} m)"
    )
    rows_z2 = int(round(zone2_end_height / stone_height_m))
    st.sidebar.caption(f"≈ {rows_z2} Reihen")
    
    # Visuelle Hilfe
    total_length_zones = zone1_length + zone2_length
    st.sidebar.markdown("---")
    st.sidebar.caption(f"**Gesamtlänge:** {total_length_zones:.1f} m")
    
    # ASCII-Diagramm
    zone1_bars = int((zone1_length / total_length_zones) * 20) if total_length_zones > 0 else 10
    zone2_bars = 20 - zone1_bars
    
    if zone2_end_height > zone1_height:
        arrow = "↗"
    elif zone2_end_height < zone1_height:
        arrow = "↘"
    else:
        arrow = "→"
    
    st.sidebar.text(f"{'━' * zone1_bars}┃{'━' * zone2_bars}")
    st.sidebar.caption(f"{zone1_height:.1f}m (flach) → {arrow} {zone2_end_height:.1f}m")
    
    # Für Berechnungen: Kombinierte Werte
    length = total_length_zones
    start_height = zone1_height
    end_height = zone2_end_height
    is_two_zone = True

# Stein-Auswahl
# Breite wird automatisch aus Stein übernommen, kann aber überschrieben werden
st.sidebar.markdown("---")
st.sidebar.subheader("📏 Wandstärke")
width = st.sidebar.number_input(
    "Breite/Dicke (cm)",
    min_value=10.0,
    max_value=100.0,
    value=float(selected_stone_data['width_cm']),
    step=0.5,
    help="Wandstärke in cm (Standard: Dicke des gewählten Steins)"
)

# Kosten (Mittlere Priorität)
st.sidebar.subheader("💰 Materialpreise")
enable_costs = st.sidebar.checkbox("Kosten berechnen", value=True)

cement_price = None
gravel_price = None
stone_price = None

if enable_costs:
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        cement_price = st.sidebar.number_input(
            "Zement (25 kg) in €",
            min_value=0.0,
            max_value=50.0,
            value=float(config['prices']['cement_per_bag_eur']),
            step=0.5
        )
    
    with col2:
        gravel_price = st.sidebar.number_input(
            "Kies (pro Tonne) in €",
            min_value=0.0,
            max_value=200.0,
            value=float(config['prices']['gravel_per_ton_eur']),
            step=5.0
        )
    
    stone_price = st.sidebar.number_input(
        "Schalstein (pro Stück) in €",
        min_value=0.0,
        max_value=20.0,
        value=float(config['prices']['stone_per_piece_eur']),
        step=0.10,
        help="Preis ohne MwSt (19%)"
    )
    
    rebar_price = st.sidebar.number_input(
        "Bewehrungsstahl (6m Stab) in €",
        min_value=0.0,
        max_value=50.0,
        value=float(config['reinforcement_steel']['price_per_6m_rod_eur']),
        step=0.50,
        help="Preis pro 6m Stab (Ø 8mm), ab 1m Höhe"
    )
else:
    rebar_price = None

# Berechnung durchführen
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Neu berechnen", type="primary", use_container_width=True):
    st.rerun()

# Hauptbereich
st.markdown("---")

# Berechnung
result = calculate_all(
    length=length,
    start_height=start_height,
    end_height=end_height,
    width=width,
    stone_type=selected_stone_type,
    cement_price=cement_price,
    gravel_price=gravel_price,
    stone_price=stone_price,
    rebar_price=rebar_price,
    is_two_zone=is_two_zone,
    zone1_length=zone1_length,
    zone1_height=zone1_height,
    zone2_length=zone2_length,
    zone2_end_height=zone2_end_height
)

# Fehlerbehandlung (Mittlere Priorität)
if 'error' in result:
    st.error(f"❌ **Fehler:** {result['error']}")
    st.stop()

# Warnungen anzeigen (Mittlere Priorität)
if result['warnings']:
    for warning in result['warnings']:
        st.warning(warning)

# Ergebnisse in Tabs
tab_overview, tab_viz, tab_materials, tab_export = st.tabs([
    "📊 Übersicht", "🎨 Visualisierung", "📦 Materialien & Kosten", "📄 Export"
])

with tab_overview:
    st.header("Zusammenfassung")
    
    # Erste Zeile: Mauer-Daten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fläche", f"{result['area']} m²")
    
    with col2:
        st.metric("Anzahl Steine", f"{result['total_stones']} St.")
    
    with col3:
        st.metric("Reihen", f"{result['rows']}")
    
    with col4:
        st.metric("Betonvolumen", f"{result['volume_with_buffer_m3']} m³")
    
    # Zone-Breakdown (falls 2-Zonen-Mauer)
    if result.get('is_two_zone') and result.get('zone_breakdown'):
        st.markdown("---")
        st.subheader("📐 Zonen-Aufschlüsselung")
        
        col1, col2 = st.columns(2)
        
        zone1 = result['zone_breakdown']['zone1']
        zone2 = result['zone_breakdown']['zone2']
        
        with col1:
            st.markdown("**📏 Zone 1 (Flacher Bereich)**")
            st.write(f"- Länge: {zone1['length']:.1f} m")
            st.write(f"- Höhe: {zone1['height']:.2f} m")
            st.write(f"- Fläche: {zone1['area']} m²")
            st.write(f"- Steine: {zone1['stones']} St.")
            st.write(f"- Reihen: {zone1['rows']}")
        
        with col2:
            st.markdown("**📐 Zone 2 (Variabler Bereich)**")
            st.write(f"- Länge: {zone2['length']:.1f} m")
            st.write(f"- Höhe: {zone2['start_height']:.2f} m → {zone2['end_height']:.2f} m")
            st.write(f"- Ø Höhe: {zone2['avg_height']} m")
            st.write(f"- Fläche: {zone2['area']} m²")
            st.write(f"- Steine: {zone2['stones']} St.")
            st.write(f"- Reihen: {zone2['rows']}")
    
    # Kosten-Übersicht (falls aktiviert)
    if enable_costs and result['costs']:
        st.markdown("---")
        
        costs = result['costs']
        
        # Erste Zeile: Beton-Materialien
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💶 Zementkosten", f"{costs['cement_cost']:.2f} €")
        
        with col2:
            st.metric("💶 Kieskosten", f"{costs['gravel_cost']:.2f} €")
        
        # Zweite Zeile: Schalsteine + Gesamt
        col1, col2 = st.columns(2)
        
        with col1:
            if costs.get('stone_cost', 0) > 0:
                st.metric(
                    "🧱 Schalsteinkosten", 
                    f"{costs['stone_cost_with_vat']:.2f} €",
                    help=f"Netto: {costs['stone_cost']:.2f} € + {costs['stone_vat']:.2f} € MwSt (19%)"
                )
            else:
                st.metric("🧱 Schalsteinkosten", "—")
        
        with col2:
            st.metric(
                "💰 Gesamtkosten", 
                f"{costs['total_cost']:.2f} €", 
                help="Alle Materialien inkl. MwSt auf Steine"
            )
    
    st.markdown("---")
    
    # Volumen-Details
    st.subheader("🧮 Volumenberechnung")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Grundvolumen (Hohlräume):** {result['base_volume_m3']} m³")
    
    with col2:
        st.success(f"**Mit {result['buffer_percentage']}% Puffer:** {result['volume_with_buffer_m3']} m³")
    
    st.caption("Der Puffer berücksichtigt Verluste und Verschnitt bei der Verarbeitung.")
    
    # Stein-Details
    st.markdown("---")
    st.subheader("🧱 Gewählter Schalstein")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Name:** {result['stone_data']['name']}")
        st.write(f"**Maße:** {result['stone_data']['length_cm']} × {result['stone_data']['width_cm']} × {result['stone_data']['height_cm']} cm")
    
    with col2:
        st.write(f"**Gewicht:** {result['stone_data']['weight_kg']} kg")
        st.write(f"**Bedarf:** {result['stone_data']['stones_per_m2']} St./m²")
    
    with col3:
        st.write(f"**Füllvolumen:** {result['stone_data']['fill_volume_per_stone_liters']:.2f} L/Stein")
        st.write(f"**Gesamt-Füllvolumen:** {result['stone_data']['fill_volume_per_m2_liters']} L/m²")
    
    # Betonempfehlung
    st.markdown("---")
    st.subheader("🏗️ Betonempfehlung nach FCN")
    st.markdown(result['concrete_recommendation'])
    
    # Disclaimer
    st.markdown("---")
    st.markdown(result['disclaimer'])

with tab_viz:
    st.header("Visualisierung der Mauer")
    
    # Performance-Warnung
    show_warning, warning_msg = should_show_performance_warning(result['layout'])
    if show_warning:
        st.warning(warning_msg)
    
    # Tabs für 2D/3D
    viz_tab_2d, viz_tab_3d, viz_tab_top = st.tabs(["🖼️ 2D Seitenansicht", "🎮 3D Ansicht", "🗺️ Draufsicht"])
    
    with viz_tab_2d:
        st.subheader("Seitenansicht mit versetztem Mauerwerk")
        fig_2d = create_2d_view(result['layout'], width / 100)
        st.plotly_chart(fig_2d, use_container_width=True)
        
        st.caption(
            "Die 2D-Ansicht zeigt die Steine in versetzter Anordnung (halbsteinversetzt). "
            "Ungerade Reihen sind um einen halben Stein versetzt."
        )
    
    with viz_tab_3d:
        st.subheader("3D-Ansicht (interaktiv)")
        st.info("💡 Tipp: Ziehen Sie mit der Maus, um die Ansicht zu drehen. Scrollen zum Zoomen.")
        
        fig_3d = create_3d_view(result['layout'], width / 100)
        st.plotly_chart(fig_3d, use_container_width=True)
        
        st.caption(
            "Die 3D-Ansicht zeigt jeden Stein als einzelnen Quader. "
            "Bei sehr großen Mauern wird die Darstellung aus Performance-Gründen begrenzt."
        )
    
    with viz_tab_top:
        st.subheader("Draufsicht")
        fig_top = create_top_view(result['layout'], width / 100)
        st.plotly_chart(fig_top, use_container_width=True)

with tab_materials:
    st.header("Materialbedarf")
    
    materials = result['materials']
    
    # Materialien als Tabelle
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧱 Zement")
        st.metric("Benötigte Säcke", f"{materials['cement_bags']} Stück")
        st.caption(f"à {materials['cement_bag_size_kg']} kg = {materials['cement_kg']} kg gesamt")
    
    with col2:
        st.subheader("🪨 Kies (Rundkies 0-16 mm)")
        st.metric("Benötigte Menge", f"{materials['gravel_tons']} Tonnen")
        st.caption(f"= {materials['gravel_kg']} kg")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Wasser")
        st.metric("Benötigte Menge", f"{materials['water_liters']} Liter")
        st.caption("(vor Ort verfügbar)")
    
    with col2:
        st.subheader("📏 Mischverhältnis")
        st.write("**Volumenbasis:**")
        mix = config['concrete_mix']
        st.write(f"- {mix['cement_parts']} Teil Zement")
        st.write(f"- {mix['gravel_parts']} Teile Kies")
        st.write(f"- {mix['water_parts']} Teile Wasser")
    
    # Bewehrungsstahl (nur wenn vorhanden)
    if result['reinforcement']:
        st.markdown("---")
        st.subheader("🔩 Bewehrungsstahl")
        st.info("💡 Automatisch berechnet ab 1m Höhe gemäß FCN-Empfehlung")
        
        rebar = result['reinforcement']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Benötigte 6m Stäbe", f"{rebar['rods_6m_needed']} Stück")
            st.caption(f"Ø {rebar['diameter_mm']} mm, je {rebar['rod_length_m']:.0f}m")
            st.caption(f"Gesamtlänge: {rebar['total_length_m']} m")
        
        with col2:
            st.metric("Anzahl Lagen", f"{rebar['rows']}")
            st.caption(f"{rebar['rods_per_row']} Stäbe pro Reihe")
            st.caption(f"= {rebar['total_rods_needed']} Stäbe gesamt")
    
    # Kosten (falls aktiviert)
    if enable_costs and result['costs']:
        st.markdown("---")
        st.header("💰 Kostenschätzung")
        
        costs = result['costs']
        
        # Erste Zeile: Einzelposten
        if result['reinforcement']:
            # 4 Spalten wenn Bewehrung vorhanden
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🧱 Schalsteine", f"{costs['stone_cost_with_vat']:.2f} €")
                st.caption(f"{result['total_stones']} St. × {stone_price:.2f} € + 19% MwSt")
            
            with col2:
                st.metric("🧱 Zement", f"{costs['cement_cost']:.2f} €")
                st.caption(f"{materials['cement_bags']} Säcke × {cement_price:.2f} €")
            
            with col3:
                st.metric("🪨 Kies", f"{costs['gravel_cost']:.2f} €")
                st.caption(f"{materials['gravel_tons']} t × {gravel_price:.2f} €")
            
            with col4:
                st.metric("🔩 Bewehrung", f"{costs['reinforcement_cost']:.2f} €")
                st.caption(f"{result['reinforcement']['rods_6m_needed']} Stäbe × {result['reinforcement']['price_per_rod_eur']:.2f} €")
        else:
            # 3 Spalten ohne Bewehrung
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🧱 Schalsteine", f"{costs['stone_cost_with_vat']:.2f} €")
                st.caption(f"{result['total_stones']} St. × {stone_price:.2f} € + 19% MwSt")
            
            with col2:
                st.metric("🧱 Zement", f"{costs['cement_cost']:.2f} €")
                st.caption(f"{materials['cement_bags']} Säcke × {cement_price:.2f} €")
            
            with col3:
                st.metric("🪨 Kies", f"{costs['gravel_cost']:.2f} €")
                st.caption(f"{materials['gravel_tons']} t × {gravel_price:.2f} €")
        
        # Zweite Zeile: Summen
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Netto (ohne MwSt)", f"{costs['subtotal']:.2f} €",
                     help="Alle Materialien ohne MwSt")
        
        with col2:
            st.metric("MwSt (19%)", f"{costs['stone_vat']:.2f} €",
                     help="Nur auf Schalsteine")
        
        with col3:
            st.metric("💰 Gesamtkosten", f"{costs['total_cost']:.2f} €", 
                     help="Alle Materialien inkl. MwSt auf Steine")
        
        # Einkaufsliste
        st.markdown("---")
        st.subheader("🛒 Einkaufsliste")
        
        shopping_list = f"""
**Benötigte Materialien:**

1. **Schalsteine:** {result['total_stones']} Stück 
   → Kosten: {costs['stone_cost']:.2f} € (netto) + {costs['stone_vat']:.2f} € MwSt = {costs['stone_cost_with_vat']:.2f} €

2. **Zement:** {materials['cement_bags']} Säcke à {materials['cement_bag_size_kg']} kg 
   → Kosten: {costs['cement_cost']:.2f} €

3. **Rundkies (0-16 mm):** {materials['gravel_tons']} Tonnen
   → Kosten: {costs['gravel_cost']:.2f} €

4. **Wasser:** ca. {materials['water_liters']} Liter (vor Ort)
"""
        
        if result['reinforcement']:
            shopping_list += f"""
5. **Bewehrungsstahl:** {result['reinforcement']['rods_6m_needed']} Stäbe à 6m (Ø {result['reinforcement']['diameter_mm']} mm)
   → Kosten: {costs['reinforcement_cost']:.2f} €
   → Gesamtlänge: {result['reinforcement']['total_length_m']} m
"""
        
        shopping_list += f"""
---

**Zwischensumme (netto):** {costs['subtotal']:.2f} €  
**MwSt (19% auf Steine):** {costs['stone_vat']:.2f} €  
**Gesamtkosten:** {costs['total_cost']:.2f} €

**Hinweis:** Preise ohne Lieferkosten. MwSt nur auf Schalsteine berechnet.
        """
        
        st.markdown(shopping_list)
        
        # Download als Text
        st.download_button(
            label="📥 Einkaufsliste herunterladen",
            data=shopping_list,
            file_name="einkaufsliste_schalsteinmauer.txt",
            mime="text/plain"
        )

with tab_export:
    st.header("📄 Export & Dokumentation")
    
    st.subheader("PDF-Export")
    
    # PDF-Export-Button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Exportieren Sie alle Berechnungen als professionelles PDF-Dokument.")
        st.write("**Enthält:** Eingaben, Steinauswahl, Berechnungen, Materialien, Kosten, Empfehlungen")
    
    with col2:
        if st.button("📥 PDF erstellen", type="primary", use_container_width=True):
            with st.spinner("PDF wird erstellt..."):
                try:
                    # Erstelle 2D Figure für PDF
                    fig_2d_for_pdf = create_2d_view(result['layout'], width / 100)
                    
                    # Eingabedaten
                    inputs = {
                        'length': length,
                        'start_height': start_height,
                        'end_height': end_height,
                        'width': width
                    }
                    
                    # Generiere PDF
                    pdf_buffer = create_pdf_report(result, inputs, fig_2d_for_pdf)
                    
                    # Download-Button
                    st.download_button(
                        label="📄 PDF herunterladen",
                        data=pdf_buffer,
                        file_name="schalsteinmauer_berechnung.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF erfolgreich erstellt!")
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Erstellen des PDFs: {str(e)}")
                    st.info("💡 Tipp: Für PDF-Export mit Bildern wird 'kaleido' benötigt: `pip install kaleido`")
    
    # Workaround: Daten als Text exportieren
    st.markdown("---")
    st.subheader("Daten als Text exportieren")
    
    export_text = f"""
SCHALSTEINMAUER BETONRECHNER - ERGEBNISSE
==========================================

MAUER-DIMENSIONEN:
- Länge: {length} m
- Anfangshöhe: {start_height} m
- Endhöhe: {end_height} m
- Breite/Dicke: {width} cm

SCHALSTEIN:
- Typ: {result['stone_data']['name']}
- Maße: {result['stone_data']['length_cm']} × {result['stone_data']['width_cm']} × {result['stone_data']['height_cm']} cm
- Gewicht: {result['stone_data']['weight_kg']} kg
- Füllvolumen: {result['stone_data']['fill_volume_per_stone_liters']:.2f} L/Stein

BERECHNUNGSERGEBNISSE:
- Fläche: {result['area']} m²
- Anzahl Steine: {result['total_stones']} St.
- Reihen: {result['rows']}
- Grundvolumen: {result['base_volume_m3']} m³
- Volumen mit {result['buffer_percentage']}% Puffer: {result['volume_with_buffer_m3']} m³

MATERIALBEDARF:
- Zement: {materials['cement_bags']} Säcke à {materials['cement_bag_size_kg']} kg ({materials['cement_kg']} kg)
- Kies: {materials['gravel_tons']} Tonnen ({materials['gravel_kg']} kg)
- Wasser: {materials['water_liters']} Liter
"""
    
    if result['reinforcement']:
        rebar = result['reinforcement']
        export_text += f"""
BEWEHRUNGSSTAHL (ab 1m Höhe):
- Benötigte 6m Stäbe: {rebar['rods_6m_needed']} Stück (Ø {rebar['diameter_mm']} mm)
- Anzahl Lagen: {rebar['rows']}
- Stäbe pro Reihe: {rebar['rods_per_row']}
- Gesamtlänge: {rebar['total_length_m']} m
"""
    
    if enable_costs and result['costs']:
        export_text += f"""
KOSTEN:
- Schalsteine: {result['total_stones']} St. × {stone_price:.2f} € = {costs['stone_cost']:.2f} € (netto)
  + MwSt (19%): {costs['stone_vat']:.2f} €
  = Gesamt: {costs['stone_cost_with_vat']:.2f} €
- Zement: {materials['cement_bags']} Säcke × {cement_price:.2f} € = {costs['cement_cost']:.2f} €
- Kies: {materials['gravel_tons']} t × {gravel_price:.2f} € = {costs['gravel_cost']:.2f} €"""
        
        if result['reinforcement']:
            export_text += f"""
- Bewehrungsstahl: {result['reinforcement']['rods_6m_needed']} Stäbe × {result['reinforcement']['price_per_rod_eur']:.2f} € = {costs['reinforcement_cost']:.2f} €"""
        
        export_text += f"""
---
Zwischensumme (netto): {costs['subtotal']:.2f} €
MwSt (19% auf Steine): {costs['stone_vat']:.2f} €
GESAMTKOSTEN: {costs['total_cost']:.2f} €
"""
    
    export_text += f"""
BETONEMPFEHLUNG:
Empfohlener Beton: C25/30 mit max. 16 mm Korn (Rundkies 0-16), F3-Konsistenz.
Für Höhen >1 m oder tragende Wände Armierung empfohlen (z.B. 2 Ø 8 mm pro Lage).

WICHTIGER HINWEIS:
Dies ist eine Schätzung und berücksichtigt Verluste, aber keine statische Berechnung 
oder spezifische Bauvorschriften. Konsultieren Sie einen Fachmann für tragende oder hohe Mauern!

Erstellt mit: Schalsteinmauer Betonrechner
"""
    
    st.download_button(
        label="📥 Ergebnisse als Text herunterladen",
        data=export_text,
        file_name="schalsteinmauer_berechnung.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.markdown("---")

# Impressum und rechtliche Hinweise
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.caption("**MauerPlaner** - Betonbedarfsrechner für Schalsteinmauern")
    st.caption("Ein Service von **LEANOFY** | © 2025")

with col2:
    st.markdown("[📄 Impressum](https://leanofy.de/impressum)")

with col3:
    st.markdown("[ℹ️ Datenschutz](https://leanofy.de/datenschutz)")

# Erweiterter Disclaimer
with st.expander("⚖️ Rechtliche Hinweise & Haftungsausschluss"):
    st.markdown("""
    **Betreiber:** LEANOFY
    
    **Haftungsausschluss:**
    
    Diese Anwendung dient ausschließlich zu Informations- und Planungszwecken. Die Nutzung erfolgt 
    auf eigene Verantwortung und ist vollständig unverbindlich.
    
    **Keine Gewährleistung:**
    - Die Berechnungen basieren auf Standardannahmen und FCN-Spezifikationen
    - Wir übernehmen keine Haftung für die Richtigkeit, Vollständigkeit oder Aktualität der Angaben
    - Die Ergebnisse ersetzen KEINE fachliche Beratung oder statische Berechnung
    - Abweichungen durch lokale Gegebenheiten, Material-Chargen oder Verarbeitung sind möglich
    
    **Keine Assoziation:**
    - LEANOFY ist nicht assoziiert mit oder autorisiert durch FCN (Fels-Werke)
    - FCN-Spezifikationen werden als öffentlich verfügbare Referenzwerte verwendet
    - Alle Markennamen und Produktbezeichnungen sind Eigentum ihrer jeweiligen Inhaber
    
    **Haftung:**
    - Jegliche Haftung für Schäden, die durch die Nutzung dieser Anwendung entstehen, wird ausgeschlossen
    - Für Bau- und Statikfragen konsultieren Sie bitte einen zugelassenen Fachmann
    - LEANOFY übernimmt keine Verantwortung für Materialbestellungen oder Bauausführungen basierend auf diesen Berechnungen
    
    **Nutzungsbedingungen:**
    - Die Nutzung dieser Anwendung ist kostenlos und unverbindlich
    - Durch die Nutzung akzeptieren Sie diese Bedingungen
    - Wir behalten uns das Recht vor, die Anwendung jederzeit zu ändern oder einzustellen
    
    **Kontakt:** Für Fragen wenden Sie sich bitte an LEANOFY über das [Impressum](https://leanofy.de/impressum)
    """)


