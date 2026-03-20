from app.services.inventory_service import inventory_service
import math

def test_calculate_reorder_decision_reorder_needed():
    result = inventory_service.calculate_reorder_decision(
        forecast=100.0, lead_time=2, service_level_z=1.65, error_std=15.0, current_inventory=100.0
    )
    # Expected RP (from manual math) = 235.0
    # Gap = RP - inventory = 235 - 100 = 135
    assert result["action"] == "REORDER"
    assert result["inventory_gap"] > 0
    assert result["recommended_reorder_qty"] > 0

def test_calculate_reorder_decision_overstock():
    result = inventory_service.calculate_reorder_decision(
        forecast=100.0, lead_time=2, service_level_z=1.65, error_std=15.0, current_inventory=1000.0
    )
    # WOI = 1000 / 100 = 10 > 8 -> OVERSTOCK
    assert result["action"] == "OVERSTOCK"
    assert result["inventory_gap"] < 0
    assert result["weeks_of_inventory"] == 10.0
    assert result["recommended_reorder_qty"] == 0

def test_calculate_reorder_decision_ok():
    result = inventory_service.calculate_reorder_decision(
        forecast=100.0, lead_time=2, service_level_z=1.65, error_std=15.0, current_inventory=300.0
    )
    # WOI = 300 / 100 = 3 <= 6 -> OK
    assert result["action"] == "OK"
    assert result["recommended_reorder_qty"] == 0
    assert result["inventory_gap"] < 0

def test_calculate_reorder_decision_critical():
    result = inventory_service.calculate_reorder_decision(
        forecast=100.0, lead_time=2, service_level_z=1.65, error_std=15.0, current_inventory=0
    )
    assert result["action"] == "REORDER"
