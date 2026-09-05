import pytest
from database import init_db
import analytics

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_inventory_calculations():
    inv = analytics.get_inventory_summary()
    assert inv["total_skus"] > 0
    assert inv["total_stock_units"] >= 0
    assert inv["total_inventory_value"] >= 0.0

def test_stockout_logic():
    oos = analytics.get_out_of_stock()
    for item in oos:
        # Out of stock rule: current_stock == 0
        assert item["product_id"] == "PRD002"

def test_reorder_recommendation_math():
    reorders = analytics.get_reorder_recommendations()
    assert isinstance(reorders, list)
    for r in reorders:
        assert r["recommended_reorder_units"] > 0
        assert r["days_remaining"] < 10

def test_dead_stock():
    dead = analytics.get_dead_stock()
    assert len(dead) >= 2
    for d in dead:
        assert d["trapped_capital"] > 0
