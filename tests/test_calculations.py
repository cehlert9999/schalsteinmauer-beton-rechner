"""
Unit Tests für die Berechnungslogik des Schalsteinmauer Betonrechners
"""

import pytest
import sys
from pathlib import Path

# Füge parent directory zum path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculations import (
    calculate_wall_area,
    calculate_stone_count,
    calculate_fill_volume,
    calculate_materials,
    calculate_costs,
    validate_inputs,
    get_height_warnings,
    get_stone_layout,
    calculate_all,
    calculate_two_zone_wall
)


class TestWallArea:
    """Tests für calculate_wall_area()"""
    
    def test_rectangular_wall(self):
        """Test für Mauer ohne Gefälle"""
        area = calculate_wall_area(length=10.0, start_height=2.0, end_height=2.0)
        assert area == 20.0
    
    def test_trapezoidal_wall(self):
        """Test für Mauer mit Gefälle"""
        area = calculate_wall_area(length=10.0, start_height=2.0, end_height=1.0)
        # Durchschnittshöhe = (2.0 + 1.0) / 2 = 1.5
        # Fläche = 10.0 * 1.5 = 15.0
        assert area == 15.0
    
    def test_small_wall(self):
        """Test für kleine Mauer"""
        area = calculate_wall_area(length=1.0, start_height=0.5, end_height=0.5)
        assert area == 0.5


class TestStoneCount:
    """Tests für calculate_stone_count()"""
    
    def test_standard_stone_straight_wall(self):
        """Test mit Standard-Stein (Abmessung 1) ohne Gefälle"""
        total_stones, rows, area = calculate_stone_count(
            length=5.0,
            start_height=1.0,
            end_height=1.0,
            stone_type="abmessung_1"
        )
        
        # Fläche = 5 * 1 = 5 m²
        assert area == 5.0
        
        # Steine = 5 m² * 11 St./m² = 55
        assert total_stones == 55
        
        # Reihen = 1.0 m / 0.248 m ≈ 4.03 → 5 Reihen
        assert rows == 5
    
    def test_stone_type_2(self):
        """Test mit Stein-Typ 2"""
        total_stones, rows, area = calculate_stone_count(
            length=10.0,
            start_height=2.0,
            end_height=2.0,
            stone_type="abmessung_2"
        )
        
        # Fläche = 10 * 2 = 20 m²
        assert area == 20.0
        
        # Steine = 20 m² * 11 St./m² = 220
        assert total_stones == 220
    
    def test_stone_type_4(self):
        """Test mit Stein-Typ 4 (andere Steine pro m²)"""
        total_stones, rows, area = calculate_stone_count(
            length=8.0,
            start_height=1.5,
            end_height=1.5,
            stone_type="abmessung_4"
        )
        
        # Fläche = 8 * 1.5 = 12 m²
        assert area == 12.0
        
        # Steine = 12 m² * 8 St./m² = 96
        assert total_stones == 96
    
    def test_wall_with_slope(self):
        """Test für Mauer mit Gefälle"""
        total_stones, rows, area = calculate_stone_count(
            length=8.0,
            start_height=2.0,
            end_height=1.0,
            stone_type="abmessung_1"
        )
        
        # Durchschnittshöhe = 1.5 m, Fläche = 8 * 1.5 = 12 m²
        assert area == 12.0
        
        # Steine = 12 m² * 11 St./m² = 132
        assert total_stones == 132


class TestFillVolume:
    """Tests für calculate_fill_volume()"""
    
    def test_volume_with_buffer(self):
        """Test Volumenberechnung mit Puffer"""
        base_volume, volume_with_buffer = calculate_fill_volume(
            total_stones=100,
            stone_type="abmessung_1"
        )
        
        # Füllvolumen pro Stein = 20.91 L
        # Grundvolumen = 100 * 20.91 / 1000 = 2.091 m³
        assert abs(base_volume - 2.091) < 0.001
        
        # Mit 15% Puffer = 2.091 * 1.15 = 2.40465 m³
        assert abs(volume_with_buffer - 2.40465) < 0.001
    
    def test_different_stone_types(self):
        """Test mit verschiedenen Steintypen"""
        base_volume_2, _ = calculate_fill_volume(50, "abmessung_2")
        base_volume_3, _ = calculate_fill_volume(50, "abmessung_3")
        base_volume_4, _ = calculate_fill_volume(50, "abmessung_4")
        
        # Abmessung 2: 50 * 15.55 / 1000 = 0.7775
        assert abs(base_volume_2 - 0.7775) < 0.001
        
        # Abmessung 3: 50 * 12.09 / 1000 = 0.6045
        assert abs(base_volume_3 - 0.6045) < 0.001
        
        # Abmessung 4: 50 * 11.0 / 1000 = 0.55
        assert abs(base_volume_4 - 0.55) < 0.001


class TestMaterials:
    """Tests für calculate_materials()"""
    
    def test_materials_for_1_cubic_meter(self):
        """Test Materialberechnung für 1 m³"""
        materials = calculate_materials(1.0)
        
        # Für 1 m³ laut Mischverhältnis:
        # Zement: 300 kg → 12 Säcke (à 25 kg)
        # Kies: 1200 kg → 1.2 t
        # Wasser: 150 L
        
        assert materials['cement_kg'] == 300.0
        assert materials['cement_bags'] == 12
        assert materials['gravel_kg'] == 1200.0
        assert materials['gravel_tons'] == 1.2
        assert materials['water_liters'] == 150.0
    
    def test_materials_for_half_cubic_meter(self):
        """Test für 0.5 m³"""
        materials = calculate_materials(0.5)
        
        # Zement: 150 kg → 6 Säcke
        assert materials['cement_kg'] == 150.0
        assert materials['cement_bags'] == 6
        
        # Kies: 600 kg → 0.6 t
        assert materials['gravel_kg'] == 600.0
        assert materials['gravel_tons'] == 0.6
        
        # Wasser: 75 L
        assert materials['water_liters'] == 75.0
    
    def test_cement_bag_rounding(self):
        """Test dass Zementsäcke aufgerundet werden"""
        # 2.1 m³ → 630 kg Zement → 25.2 Säcke → 26 Säcke
        materials = calculate_materials(2.1)
        assert materials['cement_bags'] == 26


class TestCosts:
    """Tests für calculate_costs()"""
    
    def test_cost_calculation(self):
        """Test Kostenberechnung"""
        materials = {
            'cement_bags': 12,
            'gravel_tons': 1.5
        }
        
        costs = calculate_costs(
            materials=materials,
            cement_price=5.0,
            gravel_price=50.0
        )
        
        # Zement: 12 * 5 = 60 €
        assert costs['cement_cost'] == 60.0
        
        # Kies: 1.5 * 50 = 75 €
        assert costs['gravel_cost'] == 75.0
        
        # Gesamt: 135 €
        assert costs['total_cost'] == 135.0
    
    def test_different_prices(self):
        """Test mit verschiedenen Preisen"""
        materials = {
            'cement_bags': 10,
            'gravel_tons': 2.0
        }
        
        costs = calculate_costs(
            materials=materials,
            cement_price=7.5,
            gravel_price=45.0
        )
        
        assert costs['cement_cost'] == 75.0
        assert costs['gravel_cost'] == 90.0
        assert costs['total_cost'] == 165.0
    
    def test_with_stone_costs(self):
        """Test Kostenberechnung mit Schalstein-Kosten"""
        materials = {
            'cement_bags': 12,
            'gravel_tons': 1.5
        }
        
        costs = calculate_costs(
            materials=materials,
            cement_price=5.0,
            gravel_price=50.0,
            stone_count=100,
            stone_price=2.50
        )
        
        # Schalsteine: 100 * 2.50 = 250 € (netto)
        assert costs['stone_cost'] == 250.0
        
        # MwSt: 250 * 0.19 = 47.50 €
        assert costs['stone_vat'] == 47.50
        
        # Schalsteine inkl. MwSt: 297.50 €
        assert costs['stone_cost_with_vat'] == 297.50
        
        # Zement: 12 * 5 = 60 €
        assert costs['cement_cost'] == 60.0
        
        # Kies: 1.5 * 50 = 75 €
        assert costs['gravel_cost'] == 75.0
        
        # Netto-Summe: 250 + 60 + 75 = 385 €
        assert costs['subtotal'] == 385.0
        
        # Gesamt: 60 + 75 + 297.50 = 432.50 €
        assert costs['total_cost'] == 432.50


class TestValidation:
    """Tests für validate_inputs()"""
    
    def test_valid_inputs(self):
        """Test mit gültigen Eingaben"""
        is_valid, error = validate_inputs(
            length=5.0,
            start_height=1.5,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert is_valid is True
        assert error is None
    
    def test_negative_length(self):
        """Test mit negativer Länge"""
        is_valid, error = validate_inputs(
            length=-5.0,
            start_height=1.5,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert is_valid is False
        assert "Länge" in error
    
    def test_zero_height(self):
        """Test mit Höhe = 0"""
        is_valid, error = validate_inputs(
            length=5.0,
            start_height=0.0,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert is_valid is False
        assert "Anfangshöhe" in error
    
    def test_end_height_greater_than_start(self):
        """Test wenn Endhöhe > Anfangshöhe"""
        is_valid, error = validate_inputs(
            length=5.0,
            start_height=1.0,
            end_height=2.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert is_valid is False
        assert "Gefälle" in error
    
    def test_width_too_small(self):
        """Test mit zu kleiner Breite"""
        is_valid, error = validate_inputs(
            length=5.0,
            start_height=1.5,
            end_height=1.0,
            width=5.0,  # Unter Minimum (10 cm)
            stone_type="abmessung_1"
        )
        
        assert is_valid is False
        assert "Breite" in error
    
    def test_invalid_stone_type(self):
        """Test mit ungültigem Steintyp"""
        is_valid, error = validate_inputs(
            length=5.0,
            start_height=1.5,
            end_height=1.0,
            width=36.5,
            stone_type="invalid_type"
        )
        
        assert is_valid is False
        assert "Steintyp" in error


class TestHeightWarnings:
    """Tests für get_height_warnings()"""
    
    def test_no_warnings_low_wall(self):
        """Test für niedrige Mauer ohne Warnungen"""
        warnings = get_height_warnings(0.8, 0.8, is_backfilled=False)
        assert len(warnings) == 0
    
    def test_warning_above_1m(self):
        """Test für Warnung bei Höhe > 1m"""
        warnings = get_height_warnings(1.5, 1.0, is_backfilled=False)
        assert len(warnings) == 1
        assert "Armierung" in warnings[0]
    
    def test_warning_freestanding_above_2m(self):
        """Test für Warnung bei freistehend > 2m"""
        warnings = get_height_warnings(2.5, 2.0, is_backfilled=False)
        assert len(warnings) == 2  # Armierung + Statik
        assert any("2" in w and "m" in w for w in warnings)
    
    def test_warning_backfilled_above_1_3m(self):
        """Test für Warnung bei hinterfüllt > 1.3m"""
        warnings = get_height_warnings(1.5, 1.2, is_backfilled=True)
        assert len(warnings) == 2
        assert any("1.3" in w for w in warnings)


class TestStoneLayout:
    """Tests für get_stone_layout()"""
    
    def test_layout_straight_wall(self):
        """Test Layout für gerade Mauer"""
        layout = get_stone_layout(
            length=10.0,
            start_height=2.0,
            end_height=2.0,
            stone_type="abmessung_1"
        )
        
        assert layout['total_length'] == 10.0
        assert layout['start_height'] == 2.0
        assert layout['end_height'] == 2.0
        assert layout['stone_length_m'] == 0.36
        assert layout['stone_height_m'] == 0.248
        
        # Steine pro Reihe = ceil(10 / 0.36) = 28
        assert layout['stones_per_row'] == 28
        
        # Reihen = ceil(2.0 / 0.248) = 9
        assert layout['rows_start'] == 9
        assert layout['rows_end'] == 9


class TestCalculateAll:
    """Integration Tests für calculate_all()"""
    
    def test_complete_calculation(self):
        """Test vollständige Berechnung"""
        result = calculate_all(
            length=5.0,
            start_height=1.0,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert result['valid'] is True
        assert 'area' in result
        assert 'total_stones' in result
        assert 'base_volume_m3' in result
        assert 'volume_with_buffer_m3' in result
        assert 'materials' in result
        assert 'layout' in result
        assert 'stone_data' in result
        
        # Puffer sollte angewendet sein
        assert result['volume_with_buffer_m3'] > result['base_volume_m3']
    
    def test_calculation_with_costs(self):
        """Test Berechnung mit Kosten"""
        result = calculate_all(
            length=5.0,
            start_height=1.0,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1",
            cement_price=5.0,
            gravel_price=50.0
        )
        
        assert result['valid'] is True
        assert result['costs'] is not None
        assert 'cement_cost' in result['costs']
        assert 'gravel_cost' in result['costs']
        assert 'total_cost' in result['costs']
    
    def test_invalid_input_returns_error(self):
        """Test dass ungültige Eingaben Fehler zurückgeben"""
        result = calculate_all(
            length=-5.0,  # Ungültig
            start_height=1.0,
            end_height=1.0,
            width=36.5,
            stone_type="abmessung_1"
        )
        
        assert 'error' in result
        assert result['error'] is not None


class TestTwoZoneWall:
    """Tests für 2-Zonen-Mauer"""
    
    def test_two_zone_flat_and_rising(self):
        """Test für flache Zone + ansteigende Zone"""
        area, total_stones, rows, _, zone_breakdown = calculate_two_zone_wall(
            zone1_length=5.0,
            zone1_height=1.0,
            zone2_length=5.0,
            zone2_end_height=2.0,
            stone_type="abmessung_1"
        )
        
        # Zone 1: 5m × 1m = 5 m²
        assert zone_breakdown['zone1']['area'] == 5.0
        assert zone_breakdown['zone1']['stones'] == 55  # 5 m² * 11 St./m²
        
        # Zone 2: 5m × 1.5m (Durchschnitt) = 7.5 m²
        assert zone_breakdown['zone2']['area'] == 7.5
        assert zone_breakdown['zone2']['avg_height'] == 1.5
        
        # Gesamt: 5 + 7.5 = 12.5 m²
        assert area == 12.5
    
    def test_two_zone_flat_and_falling(self):
        """Test für flache Zone + abfallende Zone"""
        area, total_stones, rows, _, zone_breakdown = calculate_two_zone_wall(
            zone1_length=3.0,
            zone1_height=2.0,
            zone2_length=2.0,
            zone2_end_height=1.0,
            stone_type="abmessung_1"
        )
        
        # Zone 1: 3m × 2m = 6 m²
        assert zone_breakdown['zone1']['area'] == 6.0
        
        # Zone 2: 2m × 1.5m (Durchschnitt von 2m und 1m) = 3 m²
        assert zone_breakdown['zone2']['area'] == 3.0
        
        # Gesamt
        assert area == 9.0
    
    def test_two_zone_equal_heights(self):
        """Test wenn beide Zonen gleiche Höhe haben"""
        area, total_stones, rows, _, zone_breakdown = calculate_two_zone_wall(
            zone1_length=4.0,
            zone1_height=1.5,
            zone2_length=4.0,
            zone2_end_height=1.5,
            stone_type="abmessung_1"
        )
        
        # Beide Zonen: 4m × 1.5m = 6 m²
        assert zone_breakdown['zone1']['area'] == 6.0
        assert zone_breakdown['zone2']['area'] == 6.0
        
        # Durchschnittshöhe Zone 2
        assert zone_breakdown['zone2']['avg_height'] == 1.5
    
    def test_calculate_all_with_two_zones(self):
        """Test calculate_all() mit 2-Zonen-Parameter"""
        result = calculate_all(
            length=10.0,  # Gesamt
            start_height=1.0,
            end_height=2.0,
            width=36.5,
            stone_type="abmessung_1",
            is_two_zone=True,
            zone1_length=5.0,
            zone1_height=1.0,
            zone2_length=5.0,
            zone2_end_height=2.0
        )
        
        assert result['valid'] is True
        assert result['is_two_zone'] is True
        assert 'zone_breakdown' in result
        assert result['zone_breakdown']['zone1']['length'] == 5.0
        assert result['zone_breakdown']['zone2']['length'] == 5.0
    
    def test_two_zone_layout_info(self):
        """Test dass Layout-Info für 2-Zonen korrekt ist"""
        result = calculate_all(
            length=8.0,
            start_height=1.3,
            end_height=3.3,
            width=36.5,
            stone_type="abmessung_1",
            is_two_zone=True,
            zone1_length=3.5,
            zone1_height=1.3,
            zone2_length=4.5,
            zone2_end_height=3.3
        )
        
        layout = result['layout']
        assert layout['is_two_zone'] is True
        assert layout['zone1_length'] == 3.5
        assert layout['zone2_length'] == 4.5
        assert layout['zone1_height'] == 1.3
        assert layout['zone2_end_height'] == 3.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



