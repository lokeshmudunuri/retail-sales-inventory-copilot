# Project Context: Retail Sales & Inventory AI Copilot
**Track ID:** PS03  

## Objective
Provide an auditable, proactive decision copilot for retail managers to monitor inventory, identify stock risks, and analyze product performance.

## Operational Rules & Guardrails
- **Zero-Hallucination Policy:** The LLM does not generate or estimate numerical metrics.
- **Deterministic Analytics First:** Python (Pandas/NumPy) handles all aggregations, stock velocity, runway, and trapped capital calculations.
- **Data Inadequacy Handling:** If data for a requested parameter or period is missing, explicitly report insufficient data rather than inferring.
- **Output Structure:** Every operational response must follow: Direct Answer → Key Numbers → Actionable Recommendation → Analytical Reason.

## Key Formulas
- **Daily Sales Velocity:** Units sold (last 30 days) / 30
- **Stock Runway (Days):** Current Stock / Daily Velocity
- **Restock Threshold:** Triggered when Runway < 7 days
- **Target Restock PO:** max(0, (Daily Velocity * 14) - Current Stock)
- **Dead Stock:** Units sold (last 30 days) == 0 AND Current Stock > 0
- **Trapped Capital:** Current Stock * Unit Cost