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


def calculate_reinforcement(
    rows: int,
    wall_length: float,
    max_height: float
) -> Optional[Dict[str, float]]:
    """
    Berechnet Bewehrungsstahl-Bedarf ab 1m Höhe
    
    Args:
        rows: Anzahl der Steinreihen
        wall_length: Länge der Mauer in Metern
        max_height: Maximale Höhe der Mauer in Metern
        
    Returns:
        Dictionary mit Bewehrungsdaten oder None wenn nicht benötigt
    """
    config = load_config()
    rebar = config['reinforcement_steel']
    
    # Nur ab Mindesthöhe berechnen
    if max_height < rebar['min_height_for_reinforcement_m']:
        return None
    
    # Stäbe pro Reihe (z.B. 2 Stück)
    rods_per_row = rebar['rods_per_row']
    
    # Gesamtanzahl Stäbe (jede Reihe bekommt 2 Stäbe)
    total_rods_needed = rows * rods_per_row
    
    # Gesamtlänge in Metern (Länge der Mauer × Anzahl Lagen × Stäbe pro Lage)
    total_length_m = wall_length * rows * rods_per_row
    
    # Anzahl 6m Stäbe (aufgerundet)
    rod_length_m = rebar['rod_length_m']
    rods_6m_needed = math.ceil(total_length_m / rod_length_m)
    
    # Kosten
    price_per_rod = rebar['price_per_6m_rod_eur']
    total_cost = rods_6m_needed * price_per_rod
    
    return {
        'rows': rows,
        'rods_per_row': rods_per_row,
        'total_rods_needed': total_rods_needed,
        'total_length_m': round(total_length_m, 1),
        'rod_length_m': rod_length_m,
        'rods_6m_needed': rods_6m_needed,
        'price_per_rod_eur': price_per_rod,
        'total_cost': round(total_cost, 2),
        'diameter_mm': rebar['diameter_mm']
    }


def calculate_costs(
    materials: Dict[str, float], 
    cement_price: float, 
    gravel_price: float,
    stone_count: int = 0,
    stone_price: float = 0.0,
    reinforcement_cost: float = 0.0
) -> Dict[str, float]:
    """
    Berechnet die Materialkosten
    
    Args:
        materials: Dictionary mit Materialmengen
        cement_price: Preis pro Zementsack in €
        gravel_price: Preis pro Tonne Kies in €
        stone_count: Anzahl Schalsteine
        stone_price: Preis pro Schalstein in €
        reinforcement_cost: Kosten für Bewehrungsstahl in €
        
    Returns:
        Dictionary mit Kosten
    """
    cement_cost = materials['cement_bags'] * cement_price
    gravel_cost = materials['gravel_tons'] * gravel_price
    stone_cost = stone_count * stone_price if stone_price > 0 else 0
    
    # Gesamt ohne MwSt
    subtotal = cement_cost + gravel_cost + stone_cost + reinforcement_cost
    
    # MwSt auf Schalsteine (19%)
    stone_vat = stone_cost * 0.19 if stone_cost > 0 else 0
    stone_cost_with_vat = stone_cost + stone_vat
    
    # Gesamtkosten mit MwSt auf Steine
    total_cost = cement_cost + gravel_cost + stone_cost_with_vat + reinforcement_cost
    
    return {
        'cement_cost': round(cement_cost, 2),
        'gravel_cost': round(gravel_cost, 2),
        'stone_cost': round(stone_cost, 2),
        'stone_cost_with_vat': round(stone_cost_with_vat, 2),
        'stone_vat': round(stone_vat, 2),
        'reinforcement_cost': round(reinforcement_cost, 2),
        'subtotal': round(subtotal, 2),
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


def calculate_two_zone_wall(
    zone1_length: float,
    zone1_height: float,
    zone2_length: float,
    zone2_end_height: float,
    stone_type: str
) -> Tuple[float, int, int, float, Dict]:
    """
    Berechnet für 2-Zonen-Mauer
    
    Args:
        zone1_length: Länge der flachen Zone in Metern
        zone1_height: Höhe der flachen Zone in Metern
        zone2_length: Länge der variablen Zone in Metern
        zone2_end_height: Endhöhe der variablen Zone in Metern
        stone_type: Typ des Steins
        
    Returns:
        (total_area, total_stones, rows, zone1_area, zone_breakdown)
    """
    config = load_config()
    stone_data = config['stone_types'][stone_type]
    stones_per_m2 = stone_data['stones_per_m2']
    stone_height_m = stone_data['height_cm'] / 100
    
    # Zone 1: Rechteckige Fläche (flach)
    zone1_area = zone1_length * zone1_height
    zone1_stones = math.ceil(zone1_area * stones_per_m2)
    zone1_rows = math.ceil(zone1_height / stone_height_m)
    
    # Zone 2: Trapezförmige Fläche (von zone1_height bis zone2_end_height)
    zone2_avg_height = (zone1_height + zone2_end_height) / 2
    zone2_area = zone2_length * zone2_avg_height
    zone2_stones = math.ceil(zone2_area * stones_per_m2)
    zone2_rows = math.ceil(max(zone1_height, zone2_end_height) / stone_height_m)
    
    # Gesamt
    total_area = zone1_area + zone2_area
    total_stones = zone1_stones + zone2_stones
    max_rows = max(zone1_rows, zone2_rows)
    
    zone_breakdown = {
        'zone1': {
            'length': zone1_length,
            'height': zone1_height,
            'area': round(zone1_area, 2),
            'stones': zone1_stones,
            'rows': zone1_rows
        },
        'zone2': {
            'length': zone2_length,
            'start_height': zone1_height,
            'end_height': zone2_end_height,
            'avg_height': round(zone2_avg_height, 2),
            'area': round(zone2_area, 2),
            'stones': zone2_stones,
            'rows': zone2_rows
        }
    }
    
    return total_area, total_stones, max_rows, total_area, zone_breakdown


def calculate_all(
    length: float,
    start_height: float,
    end_height: float,
    width: float,
    stone_type: str,
    cement_price: Optional[float] = None,
    gravel_price: Optional[float] = None,
    stone_price: Optional[float] = None,
    is_two_zone: bool = False,
    zone1_length: Optional[float] = None,
    zone1_height: Optional[float] = None,
    zone2_length: Optional[float] = None,
    zone2_end_height: Optional[float] = None
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
    
    # Spezialfall: 2-Zonen-Mauer
    zone_breakdown = None
    if is_two_zone and all([zone1_length, zone1_height, zone2_length, zone2_end_height]):
        # 2-Zonen-Berechnung
        area, total_stones, rows, _, zone_breakdown = calculate_two_zone_wall(
            zone1_length, zone1_height, zone2_length, zone2_end_height, stone_type
        )
        
        # Layout für Visualisierung (2 Zonen)
        layout = {
            'stone_length_m': config['stone_types'][stone_type]['length_cm'] / 100,
            'stone_width_m': config['stone_types'][stone_type]['width_cm'] / 100,
            'stone_height_m': config['stone_types'][stone_type]['height_cm'] / 100,
            'is_two_zone': True,
            'zone1_length': zone1_length,
            'zone1_height': zone1_height,
            'zone2_length': zone2_length,
            'zone2_start_height': zone1_height,
            'zone2_end_height': zone2_end_height,
            'total_length': length,
            'start_height': start_height,
            'end_height': end_height,
            'rows_start': zone_breakdown['zone1']['rows'],
            'rows_end': zone_breakdown['zone2']['rows'],
            'stones_per_row': math.ceil(length / (config['stone_types'][stone_type]['length_cm'] / 100))
        }
    else:
        # Standard-Berechnung (einfach)
        total_stones, rows, area = calculate_stone_count(length, start_height, end_height, stone_type)
        layout = get_stone_layout(length, start_height, end_height, stone_type)
    
    # Volumen
    base_volume, volume_with_buffer = calculate_fill_volume(total_stones, stone_type)
    
    # Materialien
    materials = calculate_materials(volume_with_buffer)
    
    # Bewehrungsstahl (automatisch ab 1m Höhe)
    max_height = max(start_height, end_height)
    reinforcement = calculate_reinforcement(rows, length, max_height)
    
    # Kosten (falls Preise angegeben)
    costs = None
    if cement_price is not None and gravel_price is not None:
        reinforcement_cost = reinforcement['total_cost'] if reinforcement else 0.0
        costs = calculate_costs(
            materials, 
            cement_price, 
            gravel_price,
            stone_count=total_stones,
            stone_price=stone_price if stone_price is not None else 0.0,
            reinforcement_cost=reinforcement_cost
        )
    
    # Steininfo
    stone_data = config['stone_types'][stone_type]
    
    result = {
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
        'reinforcement': reinforcement,
        'layout': layout,
        'stone_data': stone_data,
        'concrete_recommendation': get_concrete_recommendation(),
        'disclaimer': get_disclaimer(),
        'is_two_zone': is_two_zone
    }
    
    # Füge Zone-Breakdown hinzu, wenn vorhanden
    if zone_breakdown:
        result['zone_breakdown'] = zone_breakdown
    
    return result


