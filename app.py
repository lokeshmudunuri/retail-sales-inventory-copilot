from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from database import init_db
import analytics
import agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Retail Sales & Inventory AI Copilot", lifespan=lifespan)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Retail Sales & Inventory AI Copilot</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen">
  <header class="border-b border-slate-800 bg-slate-900/90 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
    <div class="flex items-center space-x-3">
      <span class="bg-emerald-500 text-slate-950 font-black text-xs px-2.5 py-1 rounded">PS03</span>
      <h1 class="text-base md:text-lg font-bold">Retail Operations & Merchandising Copilot</h1>
    </div>
    <div class="text-xs text-slate-400">Database: <span class="text-emerald-400 font-semibold">SQLite Live</span></div>
  </header>

  <main class="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
    <div id="stats-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">30-Day Revenue</div>
        <div id="stat-revenue" class="text-2xl font-bold text-white mt-1">₹3,805,770.00</div>
        <div class="text-xs text-emerald-400 mt-2">Volume: 5,640 units</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">30-Day Net Profit</div>
        <div id="stat-profit" class="text-2xl font-bold text-emerald-400 mt-1">₹1,940,250.00</div>
        <div class="text-xs text-slate-400 mt-2">Margin: 51.0%</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Inventory Value</div>
        <div id="stat-inv" class="text-2xl font-bold text-white mt-1">₹168,870.00</div>
        <div class="text-xs text-slate-400 mt-2">484 units on hand</div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
        <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Stock Alerts</div>
        <div class="flex items-center space-x-4 mt-1">
          <div><span class="text-xl font-bold text-amber-400">3</span> <span class="text-xs text-slate-400">Low</span></div>
          <div><span class="text-xl font-bold text-rose-500">1</span> <span class="text-xs text-slate-400">Out</span></div>
        </div>
        <div class="text-xs text-rose-400 mt-2">Emergency PO Needed</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="lg:col-span-7 space-y-6">
        <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-200 mb-3 flex items-center justify-between">
            <span>Critical Inventory Actions</span>
            <span class="text-xs bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded">4 Attention Items</span>
          </h2>
          <table class="w-full text-xs text-left text-slate-300">
            <thead class="text-slate-400 border-b border-slate-800">
              <tr><th class="py-2">Product</th><th class="py-2">Stock</th><th class="py-2">Min Buffer</th><th class="py-2">Status</th></tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              <tr class="text-rose-400 font-medium"><td class="py-2">Classic Filter Powder</td><td class="py-2">0</td><td class="py-2">10</td><td class="py-2">Out of Stock</td></tr>
              <tr class="text-amber-300"><td class="py-2">Espresso Dark Roast (1kg)</td><td class="py-2">4</td><td class="py-2">15</td><td class="py-2">Low Stock</td></tr>
              <tr class="text-amber-300"><td class="py-2">Caramel Sauce (1kg)</td><td class="py-2">3</td><td class="py-2">8</td><td class="py-2">Low Stock</td></tr>
              <tr class="text-amber-300"><td class="py-2">Artisan Sourdough Loaf</td><td class="py-2">2</td><td class="py-2">6</td><td class="py-2">Low Stock</td></tr>
            </tbody>
          </table>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-200 mb-3">Top Products (Last 30 Days)</h2>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between border-b border-slate-800 pb-2">
              <div><span class="font-bold text-white">Espresso Dark Roast (1kg)</span><span class="text-slate-400 block">Coffee • 1,713 sold</span></div>
              <div class="text-right"><span class="text-emerald-400 font-semibold">₹2,055,600.00</span><span class="text-slate-400 block">₹942,150.00 profit</span></div>
            </div>
            <div class="flex justify-between border-b border-slate-800 pb-2">
              <div><span class="font-bold text-white">Oat Milk Barista Edition (1L)</span><span class="text-slate-400 block">Dairy-Alt • 1,407 sold</span></div>
              <div class="text-right"><span class="text-emerald-400 font-semibold">₹450,240.00</span><span class="text-slate-400 block">₹196,980.00 profit</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-5 flex flex-col bg-slate-900 border border-slate-800 rounded-lg h-[580px]">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 class="text-sm font-bold uppercase tracking-wider text-white">Operational Copilot</h2>
          <span class="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded">Deterministic</span>
        </div>

        <div class="p-3 bg-slate-950/60 border-b border-slate-800 flex flex-wrap gap-2 text-xs">
          <button onclick="askPrompt('What should I focus on today?')" class="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-slate-300">⚡ Daily Focus</button>
          <button onclick="askPrompt('Which products should I reorder?')" class="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-slate-300">📦 Reorders</button>
          <button onclick="askPrompt('Show dead stock')" class="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-slate-300">🛑 Dead Stock</button>
          <button onclick="askPrompt('What will my sales look like next month?')" class="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-slate-300">🔮 Forecast</button>
        </div>

        <div id="chat-box" class="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
          <div class="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
            <span class="font-bold text-emerald-400 block mb-1">AI Copilot</span>
            <pre class="whitespace-pre-wrap font-sans text-slate-200 leading-relaxed">Answer:
Ready to assist you with sales audits, restocking calculations, profit margin inspections, and demand forecasts.

Key numbers:
• Active SKUs Monitored: 10
• Store Health Status: Online

Recommendation:
Click any prompt button above or type any inventory/sales question.

Reason:
Real-time deterministic calculations prevent retail stockouts and free up trapped capital.</pre>
          </div>
        </div>

        <div class="p-3 border-t border-slate-800 flex space-x-2">
          <input id="user-input" type="text" placeholder="Ask about sales, profits, stock, reorders..." 
                 class="flex-1 bg-slate-950 border border-slate-700 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                 onkeydown="if(event.key === 'Enter') sendMessage()">
          <button onclick="sendMessage()" class="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded text-xs">Send</button>
        </div>
      </div>
    </div>
  </main>

  <script>
    async function sendMessage() {
      const input = document.getElementById("user-input");
      const msg = input.value.trim();
      if (!msg) return;
      input.value = "";
      appendMessage("Retailer", msg, "bg-slate-700 text-white ml-6");

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        appendMessage("AI Copilot", data.reply, "bg-slate-800 border border-slate-700 text-slate-200 mr-6");
      } catch (err) {
        appendMessage("System", "Service response delayed. Try again.", "bg-rose-950 text-rose-300");
      }
    }

    function askPrompt(text) {
      document.getElementById("user-input").value = text;
      sendMessage();
    }

    function appendMessage(sender, text, cls) {
      const box = document.getElementById("chat-box");
      const div = document.createElement("div");
      div.className = `p-3 rounded-lg ${cls}`;
      div.innerHTML = `<span class="font-bold ${sender === 'Retailer' ? 'text-blue-400' : 'text-emerald-400'} block mb-1">${sender}</span><pre class="whitespace-pre-wrap font-sans text-xs leading-relaxed">${text}</pre>`;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }
  </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request):
    return HTMLResponse(content=HTML_PAGE)

@app.get("/alerts")
@app.get("/api/alerts")
def get_alerts():
    low = analytics.get_low_stock()
    oos = analytics.get_out_of_stock()
    dead = analytics.get_dead_stock()
    return JSONResponse({
        "low_stock": low,
        "out_of_stock": oos,
        "dead_stock": dead,
        "total_alerts": len(low) + len(oos) + len(dead)
    })

@app.get("/api/dashboard")
def api_dashboard():
    return analytics.get_dashboard_data()

@app.post("/api/chat")
async def api_chat(request: Request):
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"reply": "Please enter a valid question."})
    return JSONResponse({"reply": agent.chat(message)})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, reload=False)
