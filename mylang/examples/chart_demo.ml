// chart_demo.ml  —  mylang v0.6.0
// Demonstrates the chart.* namespace.
// Press F5 in Pacer — charts open in the browser panel and your browser.

// ── 1. Line chart — monthly sales ─────────────────────────────────────────
let months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"];
let sales  = [12, 19, 8, 25, 22, 30, 28, 35, 40, 38, 45, 52];

chart.page("Sales Dashboard 2026");
chart.line(months, sales, "Monthly Revenue (thousands)");

// ── 2. Bar chart — product comparison ─────────────────────────────────────
let products = ["Widget A","Widget B","Widget C","Widget D","Widget E"];
let units    = [340, 210, 480, 160, 390];
chart.bar(products, units, "Units Sold by Product");

// ── 3. Pie chart — market share ────────────────────────────────────────────
let segments = ["Enterprise","SMB","Consumer","Education"];
let share    = [45, 28, 18, 9];
chart.pie(segments, share, "Market Share (%)");

// ── 4. Area chart — website traffic ───────────────────────────────────────
let weeks = ["W1","W2","W3","W4","W5","W6","W7","W8"];
let visits = [1200, 1900, 1500, 2800, 2400, 3100, 2700, 3800];
chart.area(weeks, visits, "Weekly Website Visits");

// ── 5. Histogram — response time distribution ──────────────────────────────
let times = [45,52,48,61,55,70,43,58,49,65,72,53,47,60,68,
             51,44,57,63,50,66,54,46,59,71,42,64,56,67,48];
chart.histogram(times, 8, "API Response Time Distribution (ms)");

// ── Render all charts ──────────────────────────────────────────────────────
chart.show(["browser", "panel"]);
print("Charts rendered! Check your browser and the Pacer panel.");
