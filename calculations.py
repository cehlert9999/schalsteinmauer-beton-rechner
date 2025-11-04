"""
Berechnungslogik für Schalsteinmauer-Betonrechner
Basierend auf FCN-Spezifikationen
"""

import yaml
from typing import Dict, Tuple, Optional
import math


def load_config() -> Dict:
    """Lädt die Konfigurationsdatei"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_inputs(
    length: float,
    start_height: float,
    end_height: float,
    width: float,
    stone_type: str
) -> Tuple[bool, Optional[str]]:
    """
    Validiert die Benutzereingaben
    
    Returns:
        (is_valid, error_message)
    """
    config = load_config()
    
    # Positive Zahlen prüfen
    if length <= 0:
        return False, "Länge muss größer als 0 sein!"
    
    if start_height <= 0:
        return False, "Anfangshöhe muss größer als 0 sein!"
    
    if end_height <= 0:
        return False, "Endhöhe muss größer als 0 sein!"
    
    if width <= 0:
        return False, "Breite muss größer als 0 sein!"
    
    # Breite Mindestmaß
    min_width = config['warnings']['min_width_cm']
    if width < min_width:
        return False, f"Breite muss mindestens {min_width} cm betragen!"
    
    # Steintyp existiert?
    if stone_type not in config['stone_types']:
        return False, f"Ungültiger Steintyp: {stone_type}"
    
    return True, None


def get_height_warnings(start_height: float, end_height: float, is_backfilled: bool = False) -> list:
    """
    Gibt Warnungen für zu hohe Mauern zurück
    
    Args:
        start_height: Anfangshöhe in Metern
        end_height: Endhöhe in Metern
        is_backfilled: Ob die Mauer hinterfüllt ist
        
    Returns:
        Liste von Warnmeldungen
    """
    config = load_config()
    warnings = []
    
    max_height = max(start_height, end_height)
    
    if is_backfilled:
        limit = config['warnings']['max_height_backfilled_m']
        if max_height > limit:
            warnings.append(
                f"⚠️ Maximale Höhe für hinterfüllte Mauern ({limit} m) überschritten! "
                "Statische Berechnung erforderlich!"
            )
    else:
        limit = config['warnings']['max_height_freestanding_m']
        if max_height > limit:
            warnings.append(
                f"⚠️ Maximale Höhe für freistehende Mauern ({limit} m) überschritten! "
                "Statische Berechnung erforderlich!"
            )
    
    if max_height > 1.0:
        warnings.append(
            "💡 Bei Höhen über 1 m wird eine Armierung empfohlen. "
            "Konsultieren Sie einen Fachmann!"
        )
    
    return warnings


def calculate_wall_area(length: float, start_height: float, end_height: float) -> float:
    """
    Berechnet die Mauerfläche unter Berücksichtigung des Gefälles (trapezförmig)
    
    Args:
        length: Länge in Metern
        start_height: Anfangshöhe in Metern
        end_height: Endhöhe in Metern
        
    Returns:
        Fläche in m²
    """
    # Bei trapezförmiger Mauer: Durchschnittshöhe verwenden
    avg_height = (start_height + end_height) / 2
    area = length * avg_height
    return area


def calculate_stone_count(
    length: float,
    start_height: float,
    end_height: float,
    stone_type: str
) -> Tuple[int, int, float]:
    """
    Berechnet die Anzahl der benötigten Steine
    
    Args:
        length: Länge in Metern
        start_height: Anfangshöhe in Metern
        end_height: Endhöhe in Metern
        stone_type: Typ des Steins (z.B. "abmessung_1")
        
    Returns:
        (total_stones, rows, area)
    """
    config = load_config()
    stone_data = config['stone_types'][stone_type]
    
    # Fläche berechnen
    area = calculate_wall_area(length, start_height, end_height)
    
    # Steinanzahl basierend auf Bedarf pro m²
    stones_per_m2 = stone_data['stones_per_m2']
    total_stones = math.ceil(area * stones_per_m2)
    
    # Anzahl Reihen berechnen
    stone_height_m = stone_data['height_cm'] / 100
    avg_height = (start_height + end_height) / 2
    rows = math.ceil(avg_height / stone_height_m)
    
    return total_stones, rows, area


def calculate_fill_volume(
    total_stones: int,
    stone_type: str
) -> Tuple[float, float]:
    """
    Berechnet das Hohlraumvolumen ohne und mit Puffer
    
    Args:
        total_stones: Anzahl der Steine
        stone_type: Typ des Steins
        
    Returns:
        (base_volume_m3, volume_with_buffer_m3)
    """
    config = load_config()
    stone_data = config['stone_types'][stone_type]
    
    # Füllvolumen pro Stein in Litern
    fill_per_stone_liters = stone_data['fill_volume_per_stone_liters']
    
    # Gesamtvolumen in Kubikmetern
    base_volume_m3 = (total_stones * fill_per_stone_liters) / 1000
    
    # Mit Puffer
    buffer_percentage = config['buffer']['percentage']
    volume_with_buffer_m3 = base_volume_m3 * (1 + buffer_percentage / 100)
    
    return base_volume_m3, volume_with_buffer_m3


def calculate_materials(volume_m3: float) -> Dict[str, float]:
    """
    Berechnet die benötigten Materialien basierend auf dem Volumen
    
    Args:
        volume_m3: Volumen in Kubikmetern (inkl. Puffer)
        
    Returns:
        Dictionary mit Materialmengen
    """
    config = load_config()
    mix = config['concrete_mix']
    
    # Berechnung basierend auf Mischverhältnis für gegebenes Volumen
    cement_kg = volume_m3 * mix['cement_kg_per_m3']
    gravel_kg = volume_m3 * mix['gravel_kg_per_m3']
    water_liters = volume_m3 * mix['water_liters_per_m3']
    
    # Zement in Säcke umrechnen (aufgerundet)
    cement_bag_size = mix['cement_bag_size_kg']
    cement_bags = math.ceil(cement_kg / cement_bag_size)
    
    # Kies in Tonnen (aufgerundet auf 0.1 t)
    gravel_tons = math.ceil(gravel_kg / 100) / 10
    
    return {
        'water_liters': round(water_liters, 1),
        'gravel_kg': round(gravel_kg, 1),
        'gravel_tons': gravel_tons,
        'cement_kg': round(cement_kg, 1),
        'cement_bags': cement_bags,
        'cement_bag_size_kg': cement_bag_size
    }


def calculate_costs(materials: Dict[str, float], cement_price: float, gravel_price: float) -> Dict[str, float]:
    """
    Berechnet die Materialkosten
    
    Args:
        materials: Dictionary mit Materialmengen
        cement_price: Preis pro Zementsack in €
        gravel_price: Preis pro Tonne Kies in €
        
    Returns:
        Dictionary mit Kosten
    """
    cement_cost = materials['cement_bags'] * cement_price
    gravel_cost = materials['gravel_tons'] * gravel_price
    total_cost = cement_cost + gravel_cost
    
    return {
        'cement_cost': round(cement_cost, 2),
        'gravel_cost': round(gravel_cost, 2),
        'total_cost': round(total_cost, 2)
    }


def get_stone_layout(
    length: float,
    start_height: float,
    end_height: float,
    stone_type: str
) -> Dict:
    """
    Berechnet das Layout der Steine für die Visualisierung
    
    Args:
        length: Länge in Metern
        start_height: Anfangshöhe in Metern
        end_height: Endhöhe in Metern
        stone_type: Typ des Steins
        
    Returns:
        Dictionary mit Layout-Informationen
    """
    config = load_config()
    stone_data = config['stone_types'][stone_type]
    
    stone_length_m = stone_data['length_cm'] / 100
    stone_width_m = stone_data['width_cm'] / 100
    stone_height_m = stone_data['height_cm'] / 100
    
    # Anzahl Steine pro Reihe (in Längsrichtung)
    stones_per_row = math.ceil(length / stone_length_m)
    
    # Anzahl Reihen am Anfang und Ende
    rows_start = math.ceil(start_height / stone_height_m)
    rows_end = math.ceil(end_height / stone_height_m)
    
    # Layout-Informationen für Visualisierung
    layout = {
        'stone_length_m': stone_length_m,
        'stone_width_m': stone_width_m,
        'stone_height_m': stone_height_m,
        'stones_per_row': stones_per_row,
        'rows_start': rows_start,
        'rows_end': rows_end,
        'total_length': length,
        'start_height': start_height,
        'end_height': end_height
    }
    
    return layout


def get_concrete_recommendation() -> str:
    """
    Gibt die Betonempfehlung nach FCN zurück
    
    Returns:
        Empfehlungstext
    """
    config = load_config()
    rec = config['concrete_recommendation']
    
    text = (
        f"**Empfohlener Beton:** {rec['quality']} mit max. {rec['max_grain_size_mm']} mm Korn "
        f"(Rundkies 0-{rec['max_grain_size_mm']}), {rec['consistency']}-Konsistenz.\n\n"
        f"**Armierung:** {rec['reinforcement_note']}"
    )
    
    return text


def get_disclaimer() -> str:
    """
    Gibt den Disclaimer zurück
    
    Returns:
        Disclaimer-Text
    """
    return (
        "⚠️ **Wichtiger Hinweis:** Dies ist eine Schätzung und berücksichtigt Verluste, "
        "aber keine statische Berechnung oder spezifische Bauvorschriften. "
        "Konsultieren Sie einen Fachmann für tragende oder hohe Mauern!"
    )


def calculate_all(
    length: float,
    start_height: float,
    end_height: float,
    width: float,
    stone_type: str,
    cement_price: Optional[float] = None,
    gravel_price: Optional[float] = None
) -> Dict:
    """
    Führt alle Berechnungen durch und gibt ein vollständiges Ergebnis zurück
    
    Args:
        length: Länge in Metern
        start_height: Anfangshöhe in Metern
        end_height: Endhöhe in Metern
        width: Breite in cm
        stone_type: Typ des Steins
        cement_price: Preis pro Zementsack (optional)
        gravel_price: Preis pro Tonne Kies (optional)
        
    Returns:
        Dictionary mit allen Berechnungsergebnissen
    """
    config = load_config()
    
    # Validierung
    is_valid, error = validate_inputs(length, start_height, end_height, width, stone_type)
    if not is_valid:
        return {'error': error}
    
    # Warnungen
    warnings = get_height_warnings(start_height, end_height)
    
    # Steinanzahl
    total_stones, rows, area = calculate_stone_count(length, start_height, end_height, stone_type)
    
    # Volumen
    base_volume, volume_with_buffer = calculate_fill_volume(total_stones, stone_type)
    
    # Materialien
    materials = calculate_materials(volume_with_buffer)
    
    # Kosten (falls Preise angegeben)
    costs = None
    if cement_price is not None and gravel_price is not None:
        costs = calculate_costs(materials, cement_price, gravel_price)
    
    # Layout für Visualisierung
    layout = get_stone_layout(length, start_height, end_height, stone_type)
    
    # Steininfo
    stone_data = config['stone_types'][stone_type]
    
    return {
        'valid': True,
        'warnings': warnings,
        'area': round(area, 2),
        'total_stones': total_stones,
        'rows': rows,
        'base_volume_m3': round(base_volume, 3),
        'volume_with_buffer_m3': round(volume_with_buffer, 3),
        'buffer_percentage': config['buffer']['percentage'],
        'materials': materials,
        'costs': costs,
        'layout': layout,
        'stone_data': stone_data,
        'concrete_recommendation': get_concrete_recommendation(),
        'disclaimer': get_disclaimer()
    }


