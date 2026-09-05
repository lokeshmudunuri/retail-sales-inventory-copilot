"""
data.py
-------
Loads and cleans the four source CSVs.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
STORES_FILE = os.path.join(DATA_DIR, "stores.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")


def _load_csv(path: str, source_name: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{source_name} not found at: {path}")
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def load_products() -> pd.DataFrame:
    df = _load_csv(PRODUCTS_FILE, "products.csv")
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["product_name"] = df["product_name"].fillna("Unknown Product").astype(str).str.strip()
    df["category"] = df["category"].fillna("Uncategorized").astype(str).str.strip()
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0.0)
    df["reorder_level"] = pd.to_numeric(df["reorder_level"], errors="coerce").fillna(0.0)
    df["lead_time_days"] = pd.to_numeric(df["lead_time_days"], errors="coerce").fillna(7.0)
    return df.drop_duplicates(subset="product_id", keep="last").reset_index(drop=True)


def load_stores() -> pd.DataFrame:
    df = _load_csv(STORES_FILE, "stores.csv")
    df["store_id"] = df["store_id"].astype(str).str.strip()
    df["store_name"] = df["store_name"].fillna("Unknown Store").astype(str).str.strip()
    df["location"] = df["location"].fillna("Unknown").astype(str).str.strip()
    return df.drop_duplicates(subset="store_id", keep="last").reset_index(drop=True)


def load_sales() -> pd.DataFrame:
    df = _load_csv(SALES_FILE, "sales.csv")
    df["store_id"] = df["store_id"].astype(str).str.strip()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)
    df = df[df["date"].notna()].copy()
    return df.sort_values("date").reset_index(drop=True)


def load_inventory() -> pd.DataFrame:
    df = _load_csv(INVENTORY_FILE, "inventory.csv")
    df["store_id"] = df["store_id"].astype(str).str.strip()
    df["product_id"] = df["product_id"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0.0)
    df = df[df["date"].notna()].copy()
    return df.sort_values("date").reset_index(drop=True)


def get_current_inventory(inventory: pd.DataFrame = None) -> pd.DataFrame:
    if inventory is None:
        inventory = load_inventory()
    if inventory.empty:
        return inventory
    latest = (
        inventory.sort_values("date")
        .drop_duplicates(subset=["store_id", "product_id"], keep="last")
        .rename(columns={"date": "last_updated", "stock_quantity": "current_stock"})
        .reset_index(drop=True)
    )
    return latest


_CACHE = {}


def get_data(force_reload: bool = False) -> dict:
    if force_reload or not _CACHE:
        products = load_products()
        stores = load_stores()
        sales = load_sales()
        inventory_history = load_inventory()
        current_inventory = get_current_inventory(inventory_history)

        _CACHE.clear()
        _CACHE.update({
            "products": products,
            "stores": stores,
            "sales": sales,
            "inventory_history": inventory_history,
            "inventory": current_inventory,          # <-- important alias
            "current_inventory": current_inventory,
        })
    return _CACHE