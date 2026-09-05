import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import get_connection

def load_frames():
    conn = get_connection()
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
    customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()

    if not sales_df.empty:
        sales_df["date"] = pd.to_datetime(sales_df["date"])
        sales_df["revenue"] = sales_df["quantity"] * sales_df["selling_price"]
    return products_df, sales_df, customers_df

# ----------------- REVENUE & SALES -----------------

def get_sales_by_range(days=0, start_date=None, end_date=None):
    products_df, sales_df, _ = load_frames()
    if sales_df.empty:
        return {"units": 0, "revenue": 0.0, "profit": 0.0, "count": 0}

    now = sales_df["date"].max()
    if start_date and end_date:
        mask = (sales_df["date"] >= pd.to_datetime(start_date)) & (sales_df["date"] <= pd.to_datetime(end_date))
    elif days == 0:
        # Today (latest date)
        mask = sales_df["date"] == now
    elif days == 1:
        # Yesterday
        mask = sales_df["date"] == (now - pd.Timedelta(days=1))
    else:
        mask = sales_df["date"] >= (now - pd.Timedelta(days=days))

    filtered = sales_df[mask].merge(products_df[["product_id", "cost_price"]], on="product_id", how="left")
    filtered["profit"] = (filtered["selling_price"] - filtered["cost_price"]) * filtered["quantity"]

    return {
        "units": int(filtered["quantity"].sum()),
        "revenue": round(float(filtered["revenue"].sum()), 2),
        "profit": round(float(filtered["profit"].sum()), 2),
        "transactions": len(filtered),
        "as_of_date": now.strftime("%Y-%m-%d")
    }

def get_sales_comparison():
    this_week = get_sales_by_range(days=7)
    now = datetime.strptime(this_week["as_of_date"], "%Y-%m-%d")
    last_week_start = now - timedelta(days=14)
    last_week_end = now - timedelta(days=8)
    last_week = get_sales_by_range(start_date=last_week_start, end_date=last_week_end)

    growth = 0.0
    if last_week["revenue"] > 0:
        growth = round(((this_week["revenue"] - last_week["revenue"]) / last_week["revenue"]) * 100, 1)

    return {
        "this_week_revenue": this_week["revenue"],
        "last_week_revenue": last_week["revenue"],
        "revenue_growth_pct": growth,
        "this_week_units": this_week["units"],
        "last_week_units": last_week["units"]
    }

# ----------------- INVENTORY & HEALTH -----------------

def get_inventory_summary():
    products_df, _, _ = load_frames()
    if products_df.empty:
        return {"total_skus": 0, "total_stock": 0, "inventory_value": 0.0}

    products_df["inventory_value"] = products_df["current_stock"] * products_df["cost_price"]
    return {
        "total_skus": len(products_df),
        "total_stock_units": int(products_df["current_stock"].sum()),
        "total_inventory_value": round(float(products_df["inventory_value"].sum()), 2)
    }

def get_low_stock():
    products_df, _, _ = load_frames()
    low = products_df[(products_df["current_stock"] <= products_df["reorder_level"]) & (products_df["current_stock"] > 0)]
    return low[["product_id", "product_name", "current_stock", "reorder_level", "supplier"]].to_dict(orient="records")

def get_out_of_stock():
    products_df, _, _ = load_frames()
    oos = products_df[products_df["current_stock"] == 0]
    return oos[["product_id", "product_name", "reorder_level", "supplier"]].to_dict(orient="records")

def get_stock_days_remaining():
    products_df, sales_df, _ = load_frames()
    if sales_df.empty:
        return []

    cutoff = sales_df["date"].max() - pd.Timedelta(days=30)
    recent = sales_df[sales_df["date"] >= cutoff]
    daily_velocity = (recent.groupby("product_id")["quantity"].sum() / 30.0).rename("daily_sales")

    merged = products_df.merge(daily_velocity, on="product_id", how="left").fillna({"daily_sales": 0.0})
    merged["days_remaining"] = np.where(
        merged["daily_sales"] > 0,
        (merged["current_stock"] / merged["daily_sales"]).round(1),
        999.0
    )
    return merged.sort_values(by="days_remaining")[
        ["product_id", "product_name", "current_stock", "daily_sales", "days_remaining"]
    ].to_dict(orient="records")

def get_reorder_recommendations(limit=5):
    items = get_stock_days_remaining()
    reorders = []
    for it in items:
        # Buffer recommendation: 14 days target stock
        if it["days_remaining"] < 10:
            suggested = int(max(0, (it["daily_sales"] * 14) - it["current_stock"]))
            if suggested > 0:
                reorders.append({
                    "product_id": it["product_id"],
                    "product_name": it["product_name"],
                    "current_stock": it["current_stock"],
                    "daily_velocity": round(it["daily_sales"], 1),
                    "days_remaining": it["days_remaining"],
                    "recommended_reorder_units": suggested
                })
    return reorders[:limit]

def get_dead_stock():
    products_df, sales_df, _ = load_frames()
    if sales_df.empty:
        return []

    cutoff = sales_df["date"].max() - pd.Timedelta(days=30)
    active_ids = set(sales_df[sales_df["date"] >= cutoff]["product_id"].unique())
    dead = products_df[~products_df["product_id"].isin(active_ids) & (products_df["current_stock"] > 0)].copy()
    dead["trapped_capital"] = dead["current_stock"] * dead["cost_price"]
    return dead[["product_id", "product_name", "current_stock", "cost_price", "trapped_capital"]].to_dict(orient="records")

def get_overstock():
    items = get_stock_days_remaining()
    # If remaining days > 60 and stock > 50 units
    overstocked = [it for it in items if it["days_remaining"] > 60 and it["current_stock"] > 40]
    return overstocked

# ----------------- PROFIT & MARGINS -----------------

def get_margin_analysis():
    products_df, _, _ = load_frames()
    products_df["profit_per_unit"] = products_df["selling_price"] - products_df["cost_price"]
    products_df["margin_pct"] = (products_df["profit_per_unit"] / products_df["selling_price"] * 100).round(1)

    highest_margin = products_df.sort_values(by="margin_pct", ascending=False).head(3)
    lowest_margin = products_df.sort_values(by="margin_pct", ascending=True).head(3)

    return {
        "highest_margin_products": highest_margin[["product_id", "product_name", "selling_price", "cost_price", "margin_pct"]].to_dict(orient="records"),
        "lowest_margin_products": lowest_margin[["product_id", "product_name", "selling_price", "cost_price", "margin_pct"]].to_dict(orient="records")
    }

def get_product_rankings(ascending=False, limit=5):
    products_df, sales_df, _ = load_frames()
    if sales_df.empty:
        return []

    cutoff = sales_df["date"].max() - pd.Timedelta(days=30)
    recent = sales_df[sales_df["date"] >= cutoff]
    merged = recent.groupby("product_id").agg(
        units_sold=("quantity", "sum"),
        revenue=("revenue", "sum")
    ).reset_index()

    full = products_df.merge(merged, on="product_id", how="left").fillna(0)
    full["profit"] = full["units_sold"] * (full["selling_price"] - full["cost_price"])
    full = full.sort_values(by="units_sold", ascending=ascending)

    return full.head(limit)[
        ["product_id", "product_name", "category", "units_sold", "revenue", "profit"]
    ].to_dict(orient="records")

# ----------------- SIMPLE DEMAND FORECASTING -----------------

def generate_demand_forecast(days_ahead=30):
    products_df, sales_df, _ = load_frames()
    if sales_df.empty:
        return {"error": "No sales data available to calculate forecast."}

    cutoff_30 = sales_df["date"].max() - pd.Timedelta(days=30)
    recent_30 = sales_df[sales_df["date"] >= cutoff_30]
    
    # 30-day moving average daily run rate
    velocity = recent_30.groupby("product_id")["quantity"].sum() / 30.0

    forecasts = []
    for _, row in products_df.iterrows():
        pid = row["product_id"]
        daily_rate = float(velocity.get(pid, 0.0))
        predicted = int(round(daily_rate * days_ahead))
        confidence = "High (Consistent Sales)" if daily_rate > 3.0 else ("Moderate" if daily_rate > 0 else "Low (No Recent Sales)")
        forecasts.append({
            "product_id": pid,
            "product_name": row["product_name"],
            "daily_sales_rate": round(daily_rate, 2),
            "predicted_demand_next_month": predicted,
            "current_stock": int(row["current_stock"]),
            "stock_gap": int(row["current_stock"] - predicted),
            "confidence": confidence
        })
        
    return {
        "forecast_period_days": days_ahead,
        "methodology": "30-Day Moving Average Daily Run Rate",
        "predictions": sorted(forecasts, key=lambda x: x["predicted_demand_next_month"], reverse=True)
    }

# ----------------- COMPLETE DASHBOARD DATA -----------------

def get_dashboard_data():
    today = get_sales_by_range(days=0)
    month = get_sales_by_range(days=30)
    inv = get_inventory_summary()
    low = get_low_stock()
    oos = get_out_of_stock()
    top = get_product_rankings(ascending=False, limit=5)
    
    # Last 7 days trend
    _, sales_df, _ = load_frames()
    trend = []
    if not sales_df.empty:
        cutoff_7 = sales_df["date"].max() - pd.Timedelta(days=6)
        daily = sales_df[sales_df["date"] >= cutoff_7].groupby(sales_df["date"].dt.strftime("%b %d"))["revenue"].sum().reset_index()
        trend = daily.to_dict(orient="records")

    return {
        "today_revenue": today["revenue"],
        "today_sales": today["units"],
        "month_revenue": month["revenue"],
        "month_sales": month["units"],
        "month_profit": month["profit"],
        "total_inventory_value": inv["total_inventory_value"],
        "total_stock_units": inv["total_stock_units"],
        "low_stock_count": len(low),
        "low_stock_items": low,
        "out_of_stock_count": len(oos),
        "out_of_stock_items": oos,
        "top_products": top,
        "sales_trend": trend
    }
