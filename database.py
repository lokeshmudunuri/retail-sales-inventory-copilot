import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "retail.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        selling_price REAL NOT NULL,
        cost_price REAL NOT NULL,
        current_stock INTEGER NOT NULL,
        reorder_level INTEGER NOT NULL,
        supplier TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        purchase_history TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        selling_price REAL NOT NULL,
        date TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );
    """)
    conn.commit()

    # Seed initial data if table is empty
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        seed_data(conn)
    conn.close()

def seed_data(conn):
    cur = conn.cursor()
    products = [
        ("PRD001", "Espresso Dark Roast (1kg)", "Coffee", 1200.0, 650.0, 4, 15, "BeanSupplier Co"),     # Low stock
        ("PRD002", "Classic Filter Powder (500g)", "Coffee", 450.0, 220.0, 0, 10, "Southern Roasts"),     # Out of stock
        ("PRD003", "Oat Milk Barista Edition (1L)", "Dairy-Alt", 320.0, 180.0, 140, 30, "GreenLife Ltd"), # High volume
        ("PRD004", "Vanilla Syrup (750ml)", "Beverages", 580.0, 310.0, 65, 10, "FlavorWorks"),
        ("PRD005", "Caramel Sauce (1kg)", "Beverages", 620.0, 340.0, 3, 8, "FlavorWorks"),               # Low stock
        ("PRD006", "Artisan Sourdough Loaf", "Bakery", 220.0, 90.0, 2, 6, "DailyCrust Bakery"),           # Low stock
        ("PRD007", "Butter Croissant (Box of 10)", "Bakery", 550.0, 280.0, 20, 8, "DailyCrust Bakery"),
        ("PRD008", "Cranberry Hibiscus Tea (50 bags)", "Tea", 420.0, 210.0, 50, 10, "HerbalValley"),      # Dead stock
        ("PRD009", "Decaf Colombian Beans (1kg)", "Coffee", 1350.0, 700.0, 35, 10, "BeanSupplier Co"),     # Dead stock
        ("PRD010", "Biodegradable Paper Cups (Pack 100)", "Supplies", 260.0, 140.0, 180, 25, "EcoPack")    # Overstock
    ]
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", products)

    customers = [
        ("CUST001", "Aarav Sharma", "Regular morning espresso customer"),
        ("CUST002", "Riya Patel", "Bakery and matcha bulk buyer"),
        ("CUST003", "Vikram Malhotra", "Weekly office supply orders"),
        ("CUST004", "Ananya Iyer", "Occasional specialty tea buyer")
    ]
    cur.executemany("INSERT INTO customers VALUES (?,?,?)", customers)

    # 45 days of sales records
    sales = []
    today = datetime.now()
    sale_idx = 1
    
    # Active products with varied velocity
    product_weights = {
        "PRD001": (8, 16),   # Fast
        "PRD003": (10, 20),  # Fast
        "PRD004": (1, 3),    # Medium
        "PRD005": (1, 4),    # Medium
        "PRD006": (3, 7),    # Fast
        "PRD007": (2, 5),    # Medium
        "PRD010": (1, 2)     # Slow
        # PRD002 out of stock recently; PRD008 & PRD009 have 0 sales (dead stock)
    }

    cust_ids = ["CUST001", "CUST002", "CUST003", "CUST004"]

    for d in range(45, -1, -1):
        sale_date = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        for pid, (min_q, max_q) in product_weights.items():
            qty = random.randint(min_q, max_q)
            # Fetch price
            cur.execute("SELECT selling_price FROM products WHERE product_id = ?", (pid,))
            price = cur.fetchone()[0]
            cid = random.choice(cust_ids)
            sales.append((f"SALE{sale_idx:05d}", pid, qty, price, sale_date, cid))
            sale_idx += 1

    cur.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?)", sales)
    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")
