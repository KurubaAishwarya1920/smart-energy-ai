# Smart Energy AI

A household energy-management web application. It monitors electricity
consumption, explains where the energy goes, estimates the bill, flags unusual
consumption, forecasts what is coming, and ranks the changes worth making.

It runs entirely on your own machine. There is **no paid API, no cloud account
and no internet connection required** — not to install it, and not to use it.

---

## Run it

You need Python 3.9 or newer. Nothing else.

**macOS / Linux**

```bash
./run.sh
```

**Windows**

```bat
run.bat
```

**Any platform, manually**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Then open <http://127.0.0.1:5000>. A browser tab opens on its own unless you set
`OPEN_BROWSER=0`.

The app is populated from the first second — it generates a sample household of
around 4,300 hourly readings across 180 days on startup, so every screen has
real-looking data to show.

**The terminal must stay open.** The server runs in the foreground; closing the
window or pressing Ctrl+C stops it and the page stops loading.

Run the tests with:

```bash
python -m unittest discover tests
```

---

## What is on each page

| Page | What it does |
| --- | --- |
| **Dashboard** | Today's load curve against a typical day, consumption and bill figures, efficiency score with its own breakdown, CO₂, the top finding and recent alerts. Day / week / month / year filters. |
| **Consumption** | Daily, weekly and monthly views plus a custom date range. Bar, area and hour-profile charts, comparison against the previous period, and a full reading log with per-day cost, peak hour and usage status. |
| **AI insights** | Rule-based findings with severity, an explanation of what was measured, an estimated saving and a specific action. Optionally narrated by an LLM, and you can ask questions about your own data. |
| **Prediction** | Next-day, next-week and month-end forecasts with an expected bill, a confidence figure earned from backtesting, and a history-plus-forecast chart with a likely-range band. |
| **Anomalies** | Z-score detection at day and hour level, each event with severity, a probable cause, the appliance responsible and the extra cost. Three sensitivity settings. |
| **Appliances** | Nine devices ranked by consumption, with monthly kWh, cost, run hours, share of total and a rating against a typical home. Donut chart and a you-versus-typical comparison. |
| **Bill estimator** | Fully editable slab tariff, fixed charge and duty. Shows the slab-by-slab working, not just a total. Save it and every cost figure in the app follows. |
| **Saving ideas** | Recommendations ranked by what they actually save on your appliance mix, with difficulty, effort and CO₂ avoided. |
| **Reports** | A period report covering totals, bill breakdown, appliances, findings, anomalies and actions. Print to PDF, or export daily and hourly CSV. |
| **Settings** | Household details, targets, CO₂ factor, tariff, demo-data controls and AI provider status. |

---

## How it works

```
run.py                  start the server
backend/
  app.py                Flask routes, JSON API, static serving, CSV export
  config.py             defaults and user settings (data/settings.json)
  data_store.py         seeded demo-data generator with injected faults
  analytics.py          aggregation, slab tariff maths, appliances, efficiency
  ml.py                 forecasting and anomaly detection
  insights.py           rule engine and recommendation catalogue
  ai_provider.py        OPTIONAL llm narration, server-side only
frontend/
  index.html            app shell
  css/styles.css        design system
  js/charts.js          hand-written SVG charts (no chart library)
  js/api.js             API client
  js/ui.js              formatting and shared components
  js/pages.js           the ten pages
  js/app.js             hash router
tests/test_backend.py   19 tests, standard library only
tools/build_demo.py     optional: bakes a read-only single-file preview
```

**Analytics and machine learning are pure Python.** No numpy, no pandas, no
scikit-learn, no model files. The only runtime dependency is Flask.

* **Forecasting** — least-squares linear trend over the last 60 days, multiplied
  by day-of-week seasonal factors from the last 8 weeks. The confidence figure is
  not decorative: the model is walk-forward backtested against 14 days it never
  saw, and the resulting mean error sets the confidence and the range band.
* **Anomaly detection** — z-score against a 14-day rolling average for daily
  totals, and against the same hour-of-day across 45 days for hourly spikes.
  Consecutive flagged hours are grouped into one event and attributed to the
  appliance that deviated most. A day already explained by an hourly event is
  suppressed so nothing is counted twice.
* **Insights** — a rule engine measuring evening-versus-daytime load, the peak
  window, the overnight floor, weekday-versus-weekend behaviour, month-on-month
  trend, target tracking and the dominant appliance.
* **Charts** — plain SVG generated in the browser, roughly 400 lines, with
  tooltips and resize handling. Nothing is fetched from a CDN, so the interface
  works with the network cable unplugged.

---

## The optional AI

Every insight, forecast, anomaly and recommendation is produced locally. The
optional LLM adds exactly two things: a short written summary on the AI Insights
page, and the ability to ask questions about your own figures.

Copy `.env.example` to `.env` and uncomment one provider. **Ollama is free and
runs on your own machine**, so you can have the narration without paying anyone:

```bash
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

Key handling, by design:

* Keys are read by the Python server from `.env` and are **never sent to the
  browser**. There is a test that asserts this.
* No key is hard-coded anywhere, and no placeholder key is shipped.
* If the provider is missing, misconfigured, unreachable or times out, the app
  silently falls back to the local rule engine. A demo cannot break because the
  Wi-Fi did.
* `.env` is in `.gitignore`.

---

## Demo data, and what these numbers are not

The bundled household is **generated, not measured**. It is labelled "Demo data"
in the interface, and the label is not decoration — treat every figure as an
illustration of the format, not a reading from a meter.

Specifically:

* **Appliance figures are modelled**, from typical load profiles for a home of
  this size. They are not per-device measurements. Only smart plugs or a
  sub-metered board give you that.
* **The bill is an estimate.** It uses the tariff *you* configure. Real bills
  carry provider-specific charges, subsidies, meter rent and rounding rules that
  differ by state and connection type. The defaults loosely follow a typical
  Indian domestic slab structure and are meant to be replaced with the numbers
  off your own bill.
* **Forecasts are statistical estimates**, not guarantees. Weather, house guests
  and appliance faults are not modelled. The range band is the honest part of the
  forecast.
* **Savings are estimates**, and findings overlap — the headline saving total is
  an upper bound, not a figure you can bank.

To use your own data, replace the generator in `backend/data_store.py` with a
reader for your meter export. Everything downstream — aggregation, forecasting,
anomalies, insights, billing — consumes the same simple hourly structure:

```python
{"date": "2026-09-18", "hour": 20, "weekday": 4,
 "appliances": {"Air Conditioner": 0.31, ...}, "total": 1.07}
```

Appliance-level values are optional; only `date`, `hour` and `total` are needed
for consumption, prediction, anomalies and billing to work.

---

## API

| Method | Endpoint | Returns |
| --- | --- | --- |
| GET | `/api/health` | version, reading count, AI status |
| GET | `/api/overview?range=day\|week\|month\|year` | dashboard payload |
| GET | `/api/consumption?view=daily\|weekly\|monthly&start=&end=` | series, log, summary |
| GET | `/api/appliances?days=30` | ranked appliance breakdown |
| GET | `/api/insights?ai=1` | findings, optional narrative |
| GET | `/api/predictions` | forecasts and confidence |
| GET | `/api/anomalies?day_z=&hour_z=&window=` | events and summary |
| GET | `/api/recommendations` | ranked saving ideas |
| POST | `/api/bill/estimate` | slab-by-slab bill for `{kwh, days, tariff}` |
| GET | `/api/reports/summary?days=30` | full report payload |
| GET | `/api/export/consumption.csv`, `/api/export/hourly.csv` | CSV download |
| GET / POST | `/api/settings` | read or update settings |
| POST | `/api/settings/reset`, `/api/demo/regenerate` | reset, or generate a new household |
| POST | `/api/ai/ask` | ask a question (offline-safe) |

---

## Troubleshooting

**"Can't reach this page" at 127.0.0.1:5000** — `127.0.0.1` means *this computer*.
The address only exists once `python run.py` is running on the same machine as
the browser. Start the server first; it prints the exact URL to open. If the
terminal shows no server, nothing is listening yet.

**Port 5000 is busy** — the launcher now moves to 5001, 5002 and so on by itself
and prints the port it landed on, so read the terminal rather than assuming 5000.
You can also force one with `PORT=8080 python run.py`. On macOS, AirPlay Receiver
holds port 5000 by default; System Settings > General > AirDrop & Handoff turns
it off if you want 5000 back.

**`ModuleNotFoundError: No module named 'flask'`** — dependencies are not
installed in the Python you are running. `pip install -r requirements.txt`, or
just use `./run.sh` / `run.bat`, which build the virtual environment for you.

**"Cannot reach the server"** — the page is open but `python run.py` is not
running, or it is running on a different port.

**Charts look empty** — check the browser console. The app needs JavaScript, and
it does not support Internet Explorer.

**Figures changed after I clicked "Generate a different household"** — that is
what the button does. Reset it in Settings to go back to defaults.
