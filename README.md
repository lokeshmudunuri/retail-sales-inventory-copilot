TRACK_ID=PS03

# Retail Sales & Inventory Copilot

AI-powered copilot that helps retail store managers understand sales,
inventory, stockout risks, overstock, and unusual sales activity.
# Retail Sales & Inventory AI Copilot

## 📹 Demo Video Walkthrough
[![Watch the Demo Video]
https://youtu.be/bf_dRJUs9sY?si=nrb72j-hBDLWkpNJ
## System Architecture & Detailed Approach

Our solution for **Track PS03 (Retail Sales & Inventory Copilot)** is engineered around one foundational principle: **decoupling deterministic business arithmetic from natural language reasoning**. In commercial operations, language models cannot be trusted to perform multi-step math because they tend to approximate, round incorrectly, or hallucinate numbers. To guarantee 100% auditability and trust, we implemented a single-directional data pipeline where Python is the sole source of truth for every figure, and Gemini is restricted exclusively to intent parsing and grounded semantic explanation.

---

### Pipeline Flow

[ Local CSV Data Layer ]
(stores, products, inventory, sales)
│
▼
[ DataLoader & Validation Layer ]
(Schema validation, missing values, date handling)
│
▼
[ Deterministic Analytics Engine ] (src/analytics.py)
(Pandas / NumPy calculations: velocity, runway, capital, margins)
│
▼
[ Deterministic Attention Engine ] (src/rules.py)
(Heuristic rule scoring: stock-outs, dead stock, spikes, drops)
│
▼
[ FastAPI Backend Layer ] (app.py)
(Mounts REST endpoints & static frontend on port 8000)
│
▼
[ Grounded Gemini Reasoning ] (src/copilot.py)
(Structured JSON evidence in ──► Grounded business directive out)


---

### 1. The Data Layer & Validation (`src/data.py` / `data/`)
* **Local Source of Truth:** The system operates over four committed relational CSV datasets: `stores.csv`, `products.csv`, `inventory.csv`, and `sales.csv` (covering 90 days of transactions across multiple retail locations).
* **Defensive Data Ingestion:** The `DataLoader` verifies schema types, handles date parsing, catches missing records, and replaces null values before data reaches calculation modules.

### 2. Deterministic Analytics Engine (`src/analytics.py`)
* **Python as the Sole Arithmetic Authority:** All inventory and financial mathematics are executed deterministically using Pandas and NumPy.
* **Core Metrics Computed:**
  * **Daily Sales Velocity:** Rolling daily unit sales based on historical windows.
  * **Inventory Runway (Days Remaining):** $\text{Current Stock} \div \text{Average Daily Velocity}$.
  * **Dead-Stock Trapped Capital:** Isolates items with zero sales in the last 30 days and calculates unrecovered working capital ($\text{Current Stock} \times \text{Unit Cost}$).
  * **Period-over-Period Growth:** Compares trailing 30-day velocity to prior intervals to identify macro trajectory.
* **Edge-Case Resilience:** The engine natively handles division-by-zero, negative inventory counts, intermittent sales intervals, and products with zero transactions without crashing.

### 3. Rule-Based Attention Engine (`src/rules.py`)
* **Heuristic Anomaly Detection:** Rather than relying on fuzzy prompts to detect problems, deterministic rules flag inventory issues into categorized attention items:
  * **Stock-Out Risk:** Triggered when stock runway drops below 7 days based on current velocity.
  * **Overstock & Dead Stock:** Triggered when runway exceeds safe bounds (>60 days) or has 0 sales in 30 days.
  * **Demand Spikes & Drops:** Statistical flags for sudden shifts in volume across specific stores.
* **Traceable Audit Payloads:** Every generated alert attaches an exact evidence payload: product ID, store ID, current stock, velocity, calculated risk level, and baseline business assumptions.

### 4. Grounded Gemini AI Copilot
* **Zero-Math Prompt Architecture:** Gemini is never permitted to calculate sums, project runway, or estimate prices. It receives a pre-computed structured JSON payload containing only verified metrics from Python.
* **Strict Seven-Part Structured Output:** When answering operational questions, Gemini synthesizes the evidence into an executive format:
  1. **Answer:** Direct executive summary.
  2. **Key Points:** Bulleted core findings.
  3. **Supporting Numbers:** Explicit, verified figures extracted directly from the payload.
  4. **Evidence Source:** Internal module origin (e.g., `Inventory Analysis`, `Attention Engine`).
  5. **Actionable Recommendation:** Commercial advice (e.g., reorder quantities, clearance bundling).
  6. **Assumptions:** Transparent baselines used during calculation.
  7. **Data Sufficiency:** Explicit confirmation whether historical data depth is complete or limited.

### 5. Resilient Offline-First Fallback
* **No Single Point of Failure:** If `GEMINI_API_KEY` is not provided or the Gemini API is unreachable, ShelfIQ does not crash.
* **Direct Evidence Passthrough:** The system gracefully bypasses LLM narration and delivers the deterministic analytics and attention records directly to the dashboard, preserving complete functionality.

### 6. Single-Command Turnkey Deployment (`app.py`)
* **Zero-Configuration Run:** Complies strictly with evaluation criteria by bundling the FastAPI backend and static frontend dashboard together under `python app.py` on `http://localhost:8000`.
* **Zero Build Steps:** No Node.js build pipelines, external database servers, secondary terminals, or background workers required.
