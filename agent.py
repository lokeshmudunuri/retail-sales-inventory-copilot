import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
import analytics

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """You are the Retail Store Operations AI Copilot (TRACK_ID=PS03).
You assist store managers using verified database analytics.
When the user asks any operational question, always call the appropriate analytical tool function.

FORMATTING RULE:
Present your final response cleanly with:
Answer:
[Direct, clear explanation in plain business language]

Key numbers:
• [Exact metric 1]
• [Exact metric 2]

Recommendation:
[Actionable commercial decision for the manager]

Reason:
[Business explanation backed by the numbers]

If the user simply greets you (e.g., 'hi', 'hello'), greet them warmly and list what you can analyze.
"""

# Tool function declarations for Gemini Automatic Tool Calling
def get_low_stock_products():
    """Returns products that are currently below or at their reorder threshold."""
    return analytics.get_low_stock()

def get_out_of_stock_products():
    """Returns products that have 0 inventory on hand."""
    return analytics.get_out_of_stock()

def get_dead_and_unsold_stock():
    """Returns stagnant products that have had zero sales in the last 30 days and have idle stock."""
    return analytics.get_dead_stock()

def get_best_selling_products():
    """Returns top-selling products by volume, revenue, and gross profit over the last 30 days."""
    return analytics.get_product_rankings(ascending=False, limit=5)

def get_lowest_selling_products():
    """Returns the worst or lowest performing active products with minimal sales volume."""
    return analytics.get_product_rankings(ascending=True, limit=5)

def get_reorder_recommendations():
    """Calculates stockout horizon and returns exact reorder unit recommendations for items running low."""
    return analytics.get_reorder_recommendations(limit=5)

def get_store_sales_and_revenue(days: int = 30):
    """Returns total volume, revenue, and profit for a specified period (e.g. today=0, yesterday=1, week=7, month=30)."""
    return analytics.get_sales_by_range(days=days)

def get_demand_forecast():
    """Provides moving average demand forecasts for the next 30 days based on recent sales velocity."""
    return analytics.generate_demand_forecast(days_ahead=30)

def get_profit_and_margin_analysis():
    """Returns the highest and lowest margin products with markup percentages."""
    return analytics.get_margin_analysis()

def get_full_store_summary():
    """Returns complete store health: total inventory value, monthly revenue, profit, and stock alerts."""
    return analytics.get_dashboard_data()

TOOLS = [
    get_low_stock_products,
    get_out_of_stock_products,
    get_dead_and_unsold_stock,
    get_best_selling_products,
    get_lowest_selling_products,
    get_reorder_recommendations,
    get_store_sales_and_revenue,
    get_demand_forecast,
    get_profit_and_margin_analysis,
    get_full_store_summary
]

def direct_fallback(query: str) -> str:
    """Robust offline fallback if Gemini hits quota/network limits."""
    q = query.lower()
    if any(w in q for w in ["low", "running out", "shortage"]):
        items = analytics.get_low_stock()
        res = ["Answer:\nHere are the products currently low in stock:\n"]
        for it in items:
            res.append(f"• {it['product_name']} — Only {it['current_stock']} left (Reorder level: {it['reorder_level']})")
        res.append("\nKey numbers:\n• Total low-stock items: " + str(len(items)))
        res.append("\nRecommendation:\nIssue replenishment orders to suppliers today.")
        res.append("\nReason:\nStock is below safety thresholds.")
        return "\n".join(res)
    elif any(w in q for w in ["dead", "not sold", "stagnant", "unsold", "sitting"]):
        dead = analytics.get_dead_stock()
        total_cash = sum(x["trapped_capital"] for x in dead)
        res = ["Answer:\nThe following products have not sold at all in the past 30 days and are sitting in inventory:\n"]
        for it in dead:
            res.append(f"• {it['product_name']} — {it['current_stock']} units untouched (₹{it['trapped_capital']:,.2f} trapped)")
        res.append(f"\nKey numbers:\n• Trapped capital: ₹{total_cash:,.2f}\n• Inactive SKUs: {len(dead)}")
        res.append("\nRecommendation:\nStop new purchase orders and bundle these items with your top sellers at 20% off.")
        res.append("\nReason:\nClearing stagnant items frees up working capital.")
        return "\n".join(res)
    elif any(w in q for w in ["least", "worst", "lowest", "slow"]):
        worst = analytics.get_product_rankings(ascending=True, limit=3)
        res = ["Answer:\nHere are your lowest-selling active products:\n"]
        for it in worst:
            res.append(f"• {it['product_name']} — Only {it['units_sold']:.0f} units sold (₹{it['revenue']:,.2f} revenue)")
        res.append("\nKey numbers:\n• Lowest active volume: " + str(int(worst[0]['units_sold'] if worst else 0)) + " units")
        res.append("\nRecommendation:\nRe-evaluate shelf placement or test smaller promotional discounts.")
        res.append("\nReason:\nThese products are lagging behind overall store sales velocity.")
        return "\n".join(res)
    elif any(w in q for w in ["best", "top", "highest", "most"]):
        top = analytics.get_product_rankings(ascending=False, limit=3)
        res = ["Answer:\nHere are your top-performing products over the last 30 days:\n"]
        for it in top:
            res.append(f"• {it['product_name']} — {it['units_sold']:.0f} units sold (₹{it['revenue']:,.2f} revenue)")
        res.append(f"\nKey numbers:\n• Revenue from top product: ₹{top[0]['revenue']:,.2f}")
        res.append("\nRecommendation:\nPrioritize shelf space and maintain inventory for these items.")
        res.append("\nReason:\nThese are your core revenue and foot-traffic drivers.")
        return "\n".join(res)
    else:
        d = analytics.get_dashboard_data()
        return f"Answer:\nStore summary: 30-day revenue is ₹{d['month_revenue']:,.2f} across {d['month_sales']} units sold.\n\nKey numbers:\n• Net Profit: ₹{d['month_profit']:,.2f}\n• Low Stock SKUs: {d['low_stock_count']}\n• Out of Stock SKUs: {d['out_of_stock_count']}\n\nRecommendation:\nReorder the {d['low_stock_count']} low-stock items immediately.\n\nReason:\nProtects healthy sales momentum."

def chat(user_message: str) -> str:
    msg = user_message.lower().strip()
    if any(msg == g or msg.startswith(g + " ") for g in ["hi", "hello", "hey", "good morning"]):
        return "Answer:\nHello! I am your Retail Sales & Inventory Copilot.\n\nKey numbers:\n• Database: Live SQLite\n• Monitored SKUs: 10\n\nRecommendation:\nAsk me about low stock, products not selling, best or worst sales, reorder plans, or store profit.\n\nReason:\nAutomated analytics keep you ahead of inventory issues."

    if client:
        try:
            # Gemini with Automatic Function Calling
            res = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=TOOLS,
                    temperature=0.1
                )
            )
            if res.text:
                return res.text.strip()
        except Exception:
            pass

    return direct_fallback(user_message)
