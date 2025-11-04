"""
Admin-Interface für Schalsteinmauer Betonrechner
Ermöglicht das Bearbeiten der config.yaml
"""

import streamlit as st
import yaml
from pathlib import Path

st.set_page_config(
    page_title="Admin - Konfiguration",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Admin-Bereich")
st.markdown("Verwaltung der Konfigurationsdatei")

# Warnung
st.warning("⚠️ **Vorsicht:** Änderungen hier wirken sich direkt auf die Berechnungen aus!")

# Passwortschutz (einfach)
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.subheader("🔒 Authentifizierung erforderlich")
    password = st.text_input("Admin-Passwort", type="password")
    
    if st.button("Anmelden"):
        # Einfaches Passwort - in Produktion durch echte Auth ersetzen!
        if password == "admin123":
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("❌ Falsches Passwort!")
    
    st.info("💡 Standard-Passwort für Demo: `admin123`")
    st.stop()

# Logout-Button
if st.button("🚪 Abmelden"):
    st.session_state.admin_authenticated = False
    st.rerun()

st.markdown("---")

# Lade Config
config_path = Path("config.yaml")

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except Exception as e:
    st.error(f"❌ Fehler beim Laden der Konfiguration: {e}")
    st.stop()

# Tabs für verschiedene Bereiche
tab_stones, tab_defaults, tab_concrete, tab_prices, tab_templates, tab_raw = st.tabs([
    "🧱 Schalsteine", "⚙️ Standardwerte", "🏗️ Betonmix", "💰 Preise", "📋 Vorlagen", "📝 Raw YAML"
])

# Schalsteine bearbeiten
with tab_stones:
    st.header("Schalstein-Typen verwalten")
    
    st.info("Hier können Sie die FCN Schalstein-Spezifikationen anpassen.")
    
    for stone_key, stone_data in config['stone_types'].items():
        with st.expander(f"**{stone_data['name']}** ({stone_key})", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                stone_data['name'] = st.text_input("Name", value=stone_data['name'], key=f"{stone_key}_name")
                stone_data['length_cm'] = st.number_input("Länge (cm)", value=float(stone_data['length_cm']), key=f"{stone_key}_length")
                stone_data['width_cm'] = st.number_input("Dicke/Breite (cm)", value=float(stone_data['width_cm']), key=f"{stone_key}_width")
                stone_data['height_cm'] = st.number_input("Höhe (cm)", value=float(stone_data['height_cm']), key=f"{stone_key}_height")
            
            with col2:
                stone_data['weight_kg'] = st.number_input("Gewicht (kg)", value=float(stone_data['weight_kg']), key=f"{stone_key}_weight")
                stone_data['stones_per_m2'] = st.number_input("Bedarf (St./m²)", value=int(stone_data['stones_per_m2']), key=f"{stone_key}_per_m2")
                stone_data['fill_volume_per_m2_liters'] = st.number_input("Füllvolumen (L/m²)", value=int(stone_data['fill_volume_per_m2_liters']), key=f"{stone_key}_fill_m2")
            
            with col3:
                stone_data['fill_volume_per_stone_liters'] = st.number_input("Füllvolumen (L/Stein)", value=float(stone_data['fill_volume_per_stone_liters']), key=f"{stone_key}_fill_stone")
                stone_data['default'] = st.checkbox("Als Standard setzen", value=bool(stone_data.get('default', False)), key=f"{stone_key}_default")

# Standardwerte
with tab_defaults:
    st.header("Standard-Dimensionen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config['defaults']['wall_length_m'] = st.number_input(
            "Standard-Länge (m)", 
            value=float(config['defaults']['wall_length_m']),
            min_value=0.1
        )
        config['defaults']['wall_start_height_m'] = st.number_input(
            "Standard-Anfangshöhe (m)", 
            value=float(config['defaults']['wall_start_height_m']),
            min_value=0.1
        )
    
    with col2:
        config['defaults']['wall_end_height_m'] = st.number_input(
            "Standard-Endhöhe (m)", 
            value=float(config['defaults']['wall_end_height_m']),
            min_value=0.1
        )
        config['defaults']['wall_width_cm'] = st.number_input(
            "Standard-Breite (cm)", 
            value=float(config['defaults']['wall_width_cm']),
            min_value=10.0
        )

# Betonmix
with tab_concrete:
    st.header("Beton-Mischverhältnis")
    
    st.subheader("Volumenverhältnis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        config['concrete_mix']['cement_parts'] = st.number_input(
            "Teile Zement", 
            value=int(config['concrete_mix']['cement_parts']),
            min_value=1
        )
    
    with col2:
        config['concrete_mix']['gravel_parts'] = st.number_input(
            "Teile Kies", 
            value=int(config['concrete_mix']['gravel_parts']),
            min_value=1
        )
    
    with col3:
        config['concrete_mix']['water_parts'] = st.number_input(
            "Teile Wasser", 
            value=float(config['concrete_mix']['water_parts']),
            min_value=0.1,
            step=0.1
        )
    
    st.markdown("---")
    st.subheader("Umrechnung für 1 m³ Beton")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        config['concrete_mix']['cement_kg_per_m3'] = st.number_input(
            "Zement (kg/m³)", 
            value=int(config['concrete_mix']['cement_kg_per_m3'])
        )
    
    with col2:
        config['concrete_mix']['gravel_kg_per_m3'] = st.number_input(
            "Kies (kg/m³)", 
            value=int(config['concrete_mix']['gravel_kg_per_m3'])
        )
    
    with col3:
        config['concrete_mix']['water_liters_per_m3'] = st.number_input(
            "Wasser (L/m³)", 
            value=int(config['concrete_mix']['water_liters_per_m3'])
        )
    
    config['concrete_mix']['cement_bag_size_kg'] = st.number_input(
        "Zementsack-Größe (kg)", 
        value=int(config['concrete_mix']['cement_bag_size_kg'])
    )
    
    st.markdown("---")
    st.subheader("Puffer für Verluste")
    
    config['buffer']['percentage'] = st.slider(
        "Puffer-Prozentsatz", 
        min_value=0,
        max_value=30,
        value=int(config['buffer']['percentage']),
        help="Puffer für Verschnitt und Verluste"
    )
    
    st.markdown("---")
    st.subheader("Betonempfehlung nach FCN")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config['concrete_recommendation']['quality'] = st.text_input(
            "Betonqualität", 
            value=config['concrete_recommendation']['quality']
        )
        config['concrete_recommendation']['max_grain_size_mm'] = st.number_input(
            "Max. Korngröße (mm)", 
            value=int(config['concrete_recommendation']['max_grain_size_mm'])
        )
    
    with col2:
        config['concrete_recommendation']['consistency'] = st.text_input(
            "Konsistenz", 
            value=config['concrete_recommendation']['consistency']
        )
    
    config['concrete_recommendation']['reinforcement_note'] = st.text_area(
        "Armierungshinweis", 
        value=config['concrete_recommendation']['reinforcement_note']
    )

# Preise
with tab_prices:
    st.header("Standard-Preise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config['prices']['cement_per_bag_eur'] = st.number_input(
            "Preis pro Zementsack (€)", 
            value=float(config['prices']['cement_per_bag_eur']),
            min_value=0.0,
            step=0.5
        )
    
    with col2:
        config['prices']['gravel_per_ton_eur'] = st.number_input(
            "Preis pro Tonne Kies (€)", 
            value=float(config['prices']['gravel_per_ton_eur']),
            min_value=0.0,
            step=5.0
        )

# Vorlagen
with tab_templates:
    st.header("Vorlagen verwalten")
    
    st.info("Hier können Sie Vorlagen für häufige Mauer-Konfigurationen verwalten.")
    
    for template_key, template_data in config['templates'].items():
        with st.expander(f"**{template_data['name']}** ({template_key})", expanded=False):
            template_data['name'] = st.text_input("Name", value=template_data['name'], key=f"tpl_{template_key}_name")
            template_data['description'] = st.text_input("Beschreibung", value=template_data['description'], key=f"tpl_{template_key}_desc")
            
            col1, col2 = st.columns(2)
            
            with col1:
                template_data['wall_length_m'] = st.number_input("Länge (m)", value=float(template_data['wall_length_m']), key=f"tpl_{template_key}_length")
                template_data['wall_start_height_m'] = st.number_input("Anfangshöhe (m)", value=float(template_data['wall_start_height_m']), key=f"tpl_{template_key}_start")
            
            with col2:
                template_data['wall_end_height_m'] = st.number_input("Endhöhe (m)", value=float(template_data['wall_end_height_m']), key=f"tpl_{template_key}_end")
                template_data['wall_width_cm'] = st.number_input("Breite (cm)", value=float(template_data['wall_width_cm']), key=f"tpl_{template_key}_width")
            
            template_data['stone_type'] = st.selectbox(
                "Steintyp", 
                options=list(config['stone_types'].keys()),
                index=list(config['stone_types'].keys()).index(template_data['stone_type']),
                key=f"tpl_{template_key}_stone"
            )

# Raw YAML
with tab_raw:
    st.header("Raw YAML Editor")
    st.warning("⚠️ **Achtung:** Direkte Bearbeitung erfordert gültiges YAML-Format!")
    
    yaml_text = st.text_area(
        "YAML Konfiguration",
        value=yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False),
        height=600
    )
    
    if st.button("YAML validieren"):
        try:
            test_config = yaml.safe_load(yaml_text)
            st.success("✅ YAML ist gültig!")
        except Exception as e:
            st.error(f"❌ YAML-Fehler: {e}")

# Speichern
st.markdown("---")
st.header("💾 Änderungen speichern")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("💾 Speichern", type="primary", use_container_width=True):
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            st.success("✅ Konfiguration erfolgreich gespeichert!")
            st.info("🔄 Laden Sie die Hauptseite neu, um die Änderungen zu übernehmen.")
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {e}")

with col2:
    if st.button("🔄 Zurücksetzen", use_container_width=True):
        st.rerun()

with col3:
    st.caption("Änderungen werden in config.yaml gespeichert")

# Backup-Hinweis
st.markdown("---")
st.info("💡 **Tipp:** Erstellen Sie vor größeren Änderungen ein Backup der config.yaml!")

# Download aktueller Config
st.download_button(
    label="📥 Aktuelle Config herunterladen (Backup)",
    data=yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False),
    file_name="config_backup.yaml",
    mime="text/yaml"
)



