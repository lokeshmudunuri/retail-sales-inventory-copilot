"""
generate_data.py
Deterministic synthetic retail data generator for Retail Sales & Inventory Copilot.
Outputs products.csv, stores.csv, sales.csv, and inventory.csv into data/
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Fix seed for strict reproducibility
SEED = 42
np.random.seed(SEED)

OUTPUT_DIR = "data"
START_DATE = datetime(2025, 1, 1)
DAYS_COUNT = 365
DATE_RANGE = [START_DATE + timedelta(days=d) for d in range(DAYS_COUNT)]

def generate_stores() -> pd.DataFrame:
    stores_data = [
        {"store_id": "ST01", "store_name": "Midtown Flagship", "location": "Manhattan, NY"},
        {"store_id": "ST02", "store_name": "Oakridge Galleria", "location": "San Jose, CA"},
        {"store_id": "ST03", "store_name": "Lakeside Commons", "location": "Chicago, IL"},
    ]
    return pd.DataFrame(stores_data)

def generate_products() -> pd.DataFrame:
    catalog = [
        # Beverages
        ("Sparkling Mineral Water 1L", "Beverages", 1.20, 2.49, 45, 3),
        ("Cold Brew Coffee 330ml", "Beverages", 1.80, 3.99, 40, 4),
        ("Organic Green Tea 500ml", "Beverages", 1.10, 2.29, 35, 3),
        ("Isotonic Sports Drink 750ml", "Beverages", 1.30, 2.79, 30, 5),
        ("Pressed Orange Juice 1L", "Beverages", 2.20, 4.49, 25, 2),
        ("Almond Milk Unsweetened 1L", "Beverages", 1.90, 3.89, 30, 4),
        ("Craft Ginger Beer 4-Pack", "Beverages", 3.50, 6.99, 20, 6),
        # Food & Snacks
        ("Artisan Sourdough Loaf", "Food", 2.10, 4.99, 20, 2),
        ("Roasted Almonds 200g", "Food", 3.20, 5.99, 30, 5),
        ("Dark Chocolate Sea Salt Bar", "Food", 1.50, 3.49, 40, 4),
        ("Gluten-Free Granola 400g", "Food", 3.40, 6.79, 25, 7),
        ("Organic Olive Oil 500ml", "Food", 6.20, 11.99, 15, 8),
        ("Organic Peanut Butter 350g", "Food", 2.60, 4.99, 25, 5),
        ("Sea Salt Potato Crisps 150g", "Food", 1.10, 2.49, 50, 3),
        # Electronics & Accessories
        ("USB-C Braided Cable 2m", "Electronics", 3.80, 12.99, 25, 10),
        ("Wireless Optical Mouse", "Electronics", 8.50, 24.99, 15, 14),
        ("Noise-Isolating Earbuds", "Electronics", 12.00, 29.99, 20, 12),
        ("Fast Wireless Charging Pad", "Electronics", 9.50, 22.99, 15, 14),
        ("Universal Travel Adapter", "Electronics", 6.00, 16.99, 20, 9),
        ("Power Bank 10000mAh", "Electronics", 11.50, 27.99, 15, 12),
        ("Bluetooth Portable Speaker", "Electronics", 16.00, 39.99, 10, 15),
        # Clothing
        ("Classic Crewneck T-Shirt White", "Clothing", 6.50, 18.00, 30, 7),
        ("Classic Crewneck T-Shirt Black", "Clothing", 6.50, 18.00, 30, 7),
        ("Slim-Fit Denim Jeans", "Clothing", 22.00, 58.00, 20, 12),
        ("Merino Wool Everyday Socks", "Clothing", 4.00, 12.00, 35, 6),
        ("Cotton Blend Hoodie Grey", "Clothing", 18.00, 45.00, 15, 10),
        ("Lighweight Windbreaker", "Clothing", 26.00, 65.00, 12, 14),
        ("Athletic Running Shorts", "Clothing", 11.00, 28.00, 20, 8),
        # Footwear
        ("Canvas Low-Top Sneakers", "Footwear", 19.00, 49.99, 15, 14),
        ("All-Weather Chelsea Boots", "Footwear", 42.00, 110.00, 10, 21),
        ("Cushioned Running Shoes", "Footwear", 38.00, 95.00, 15, 14),
        ("Indoor Comfort Slippers", "Footwear", 8.00, 22.00, 20, 7),
        ("Sport Slide Sandals", "Footwear", 9.00, 24.99, 20, 7),
        ("Leather Dress Loafers", "Footwear", 48.00, 125.00, 8, 21),
        ("Trail Walking Shoes", "Footwear", 35.00, 89.99, 12, 14),
        # Personal Care
        ("Hydrating Botanical Body Wash", "Personal Care", 3.20, 7.99, 25, 5),
        ("Gentle Daily Face Cleanser", "Personal Care", 4.50, 11.50, 20, 7),
        ("Mineral Sunscreen SPF 50", "Personal Care", 6.00, 14.99, 25, 7),
        ("Natural Deodorant Stick", "Personal Care", 3.80, 8.99, 30, 5),
        ("Moisturizing Shea Lotion", "Personal Care", 4.10, 9.99, 20, 6),
        ("Bamboo Charcoal Toothbrush 2pk", "Personal Care", 1.80, 4.99, 40, 4),
        ("Nourishing Argan Shampoo", "Personal Care", 4.80, 12.00, 20, 6),
        # Household Items
        ("Plant-Based Dish Soap 500ml", "Household", 1.90, 4.49, 35, 4),
        ("Microfiber Cleaning Cloths 4pk", "Household", 2.20, 5.99, 30, 5),
        ("All-Purpose Surface Cleaner", "Household", 2.10, 4.99, 30, 4),
        ("Soy Wax Aromatherapy Candle", "Household", 5.50, 15.00, 15, 8),
        ("Recycled Paper Towels 6-Roll", "Household", 4.50, 9.99, 25, 5),
        ("Concentrated Laundry Detergent", "Household", 7.00, 16.50, 20, 6),
        ("Silicone Food Storage Bags", "Household", 6.50, 16.99, 15, 10),
        ("Steel Insulated Water Tumbler", "Household", 8.00, 21.99, 15, 12),
    ]

    records = []
    for idx, (name, cat, cost, price, reorder, lead) in enumerate(catalog, start=1):
        records.append({
            "product_id": f"PRD{idx:03d}",
            "product_name": name,
            "category": cat,
            "price": price,
            "cost": cost,
            "reorder_level": reorder,
            "lead_time_days": lead
        })
    return pd.DataFrame(records)

def generate_sales_and_inventory(products_df: pd.DataFrame, stores_df: pd.DataFrame):
    """
    Synthesizes sales transactions and daily inventory snapshots with deliberate anomalies:
    - 5 High Stock-out Risk: PRD001, PRD002, PRD003, PRD004, PRD005
    - 5 Overstocked: PRD011, PRD012, PRD013, PRD014, PRD015
    - 5 Slow-Moving: PRD032, PRD033, PRD034, PRD035, PRD036
    - 3 Sales Spikes:
        * PRD018 at ST01 (Days 340-355: holiday demand surge)
        * PRD022 at ST02 (Days 180-192: summer promo flash)
        * PRD038 at ST03 (Days 200-215: local heatwave surge)
    - 3 Sales Drops:
        * PRD007 at ST01 (Days 330-364: sudden negative trend/drop)
        * PRD026 at ST02 (Days 150-180: unseasonal demand drop)
        * PRD048 at ST03 (Days 320-364: supply preference drop)
    """
    store_ids = stores_df["store_id"].tolist()
    product_rows = products_df.to_dict(orient="records")

    # Base daily demand rates (poisson lambda) per category
    cat_lambdas = {
        "Beverages": 4.5,
        "Food": 4.0,
        "Electronics": 1.2,
        "Clothing": 1.8,
        "Footwear": 1.1,
        "Personal Care": 2.2,
        "Household": 2.0
    }

    # Store traffic weights
    store_weights = {"ST01": 1.25, "ST02": 1.0, "ST03": 0.85}

    stock_out_pids = {"PRD001", "PRD002", "PRD003", "PRD004", "PRD005"}
    overstock_pids = {"PRD011", "PRD012", "PRD013", "PRD014", "PRD015"}
    slow_moving_pids = {"PRD032", "PRD033", "PRD034", "PRD035", "PRD036"}

    # Initialize current inventory levels
    inventory_state = {}
    for s_id in store_ids:
        for p in product_rows:
            p_id = p["product_id"]
            if p_id in overstock_pids:
                # Deliberately saturated stock
                inventory_state[(s_id, p_id)] = int(np.random.uniform(420, 550))
            elif p_id in stock_out_pids:
                # Moderate starting stock
                inventory_state[(s_id, p_id)] = int(np.random.uniform(60, 90))
            elif p_id in slow_moving_pids:
                inventory_state[(s_id, p_id)] = int(np.random.uniform(70, 110))
            else:
                inventory_state[(s_id, p_id)] = int(np.random.uniform(50, 120))

    sales_records = []
    inventory_records = []

    for day_idx, current_date in enumerate(DATE_RANGE):
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()
        is_weekend = day_of_week in [5, 6]

        for s_id in store_ids:
            s_weight = store_weights[s_id]

            for p in product_rows:
                p_id = p["product_id"]
                current_stock = inventory_state[(s_id, p_id)]
                base_lam = cat_lambdas[p["category"]] * s_weight
                if is_weekend:
                    base_lam *= 1.35

                # Apply deliberate structural anomalies
                if p_id in slow_moving_pids:
                    # Near-zero sales throughout the entire year (especially recent window)
                    lam = 0.05 if day_idx > 300 else 0.15
                elif p_id in overstock_pids:
                    # Minimal baseline demand
                    lam = 0.25
                elif p_id in stock_out_pids:
                    # Accelerate demand in last 25 days, creating critical stock-out risk
                    lam = base_lam * 2.8 if day_idx >= 340 else base_lam * 1.3
                else:
                    lam = base_lam

                # 3 Deliberate Sales Spikes
                if s_id == "ST01" and p_id == "PRD018" and (340 <= day_idx <= 355):
                    lam *= 4.5
                if s_id == "ST02" and p_id == "PRD022" and (180 <= day_idx <= 192):
                    lam *= 4.0
                if s_id == "ST03" and p_id == "PRD038" and (200 <= day_idx <= 215):
                    lam *= 3.8

                # 3 Deliberate Sales Drops
                if s_id == "ST01" and p_id == "PRD007" and (330 <= day_idx <= 364):
                    lam *= 0.12
                if s_id == "ST02" and p_id == "PRD026" and (150 <= day_idx <= 180):
                    lam *= 0.15
                if s_id == "ST03" and p_id == "PRD048" and (320 <= day_idx <= 364):
                    lam *= 0.10

                demand = np.random.poisson(lam)

                # Inventory Replenishment Logic
                # Overstocked products receive continuous excess restock
                if p_id in overstock_pids:
                    if day_idx % 25 == 0:
                        inventory_state[(s_id, p_id)] += int(np.random.randint(50, 90))
                # Stock-out scenario: freeze replenishment in the final 30 days
                elif p_id in stock_out_pids:
                    if day_idx < 335 and current_stock <= p["reorder_level"] and (day_idx % 7 == 0):
                        inventory_state[(s_id, p_id)] += int(np.random.randint(35, 60))
                elif p_id in slow_moving_pids:
                    if current_stock <= p["reorder_level"] and (day_idx % 45 == 0):
                        inventory_state[(s_id, p_id)] += int(np.random.randint(10, 20))
                else:
                    # Normal reorder arrival
                    if current_stock <= p["reorder_level"] and (day_idx % 7 == 0):
                        inventory_state[(s_id, p_id)] += int(np.random.randint(40, 80))

                current_stock = inventory_state[(s_id, p_id)]

                # Fulfill orders up to available physical stock
                quantity_sold = min(demand, current_stock)
                remaining_stock = current_stock - quantity_sold
                inventory_state[(s_id, p_id)] = remaining_stock

                # Record sales row if a purchase occurred
                if quantity_sold > 0:
                    revenue = round(quantity_sold * p["price"], 2)
                    sales_records.append({
                        "date": date_str,
                        "store_id": s_id,
                        "product_id": p_id,
                        "quantity": quantity_sold,
                        "unit_price": p["price"],
                        "revenue": revenue
                    })

                # Record daily inventory snapshot
                inventory_records.append({
                    "date": date_str,
                    "store_id": s_id,
                    "product_id": p_id,
                    "stock_quantity": remaining_stock
                })

    sales_df = pd.DataFrame(sales_records)
    inventory_df = pd.DataFrame(inventory_records)
    return sales_df, inventory_df

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stores_df = generate_stores()
    products_df = generate_products()
    sales_df, inventory_df = generate_sales_and_inventory(products_df, stores_df)

    stores_df.to_csv(os.path.join(OUTPUT_DIR, "stores.csv"), index=False)
    products_df.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    sales_df.to_csv(os.path.join(OUTPUT_DIR, "sales.csv"), index=False)
    inventory_df.to_csv(os.path.join(OUTPUT_DIR, "inventory.csv"), index=False)

    print(f"Generated data/stores.csv ({len(stores_df)} rows)")
    print(f"Generated data/products.csv ({len(products_df)} rows)")
    print(f"Generated data/sales.csv ({len(sales_df):,} rows)")
    print(f"Generated data/inventory.csv ({len(inventory_df):,} rows)")

if __name__ == "__main__":
    main()