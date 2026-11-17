# Public Health Dashboard

A dashboard for analyzing and visualizing public health data.

## Technologies Used
- Python
- Pandas
- Flask
- HTML
- CSS
- JavaScript

## Features
- Engaging home page: hero with live data snapshot, disease + location finder, stat cards, top-states chart with a **reported cases / cases per lakh** ranking toggle, quick-access cards, and a data freshness strip
- Disease and location finder (`/find`) returning dataset rows plus the matching health guide
- Disease library: landing page with a search bar, category dropdown, a **Popular diseases** strip, a **Browse by category** grid, and the full A&ndash;Z indexed library — each condition shown with a pastel category icon
- States page: region filter, sort (including population-adjusted), in-table search, **server-side pagination**, CSV export, and a schematic tile map shaded by reported cases
- Heat map page (`/map`): schematic India tile map with a **Reported cases / Cases per lakh** toggle, five-bucket shading and a click-through detail panel (population, district coverage, top diseases, links into States/Analytics/Find); metric and selected state live in the URL
- Data & downloads page (`/data`): server-rendered **filtered CSV export** (state, disease, month range) with a matching row count — the download is disabled with a clear warning when no rows match — written in Excel-friendly form (UTF-8 BOM, CRLF line endings), plus a **data dictionary** for every CSV column and derived field, **sources** and the full **methodology** — no page JavaScript
- Global search box in the top bar for diseases, states and districts
- Health data visualization
- Data analysis
- Interactive dashboard
- Analytics page: KPI tiles plus four tabs — **Trends** (line chart over time per disease/state, a **cases by state & UT** bar ranking with `UT` badges, a **disease distribution** donut and a **districts** panel), **Compare** (two states or two diseases side by side, with an overlaid monthly line), **Seasonal** (share of cases by calendar month, peak month highlighted, plus a peak-month table per disease) and **Alerts** (flags when cases jump ≥25% vs the previous period — `Surge` ≥50%, `Rise` ≥25%, `Eased` for declines). Filters, tab and compare picks are reflected in the URL, so a view can be bookmarked or shared

### Library metadata

`diseases_data.py` carries the presentation metadata for the library alongside the
content itself:

- `POPULAR_SLUGS` — which conditions lead the "Popular diseases" strip
- `CATEGORY_ICONS` / `DISEASE_ICONS` — icon key per category and per condition
  (icons are drawn in `templates/_icons.html`; a condition without an entry
  falls back to its category's icon)
- `CATEGORY_TONES` / `DISEASE_TONES` — pastel colour for the icon badge
- `CATEGORY_SHORT` — short category label for card subtitles
- `TRANSMISSION_OVERRIDES` / `NON_TRANSMISSIBLE` — transmission route where the
  category default would misdescribe the condition

## Data notes

The project ships with a **sample dataset** (`india_disease_data_sample.csv`).
The figures are demonstration data for interface testing and are **not** official
surveillance data. The interface says so on every page:

- A persistent "Sample dataset" banner appears above the content.
- The home hero, states page and About page all label the source as demo data.
- The sample file carries no reporting period, so **no date is presented as a data
  vintage**. A file's modification timestamp moves whenever anyone touches the file,
  so it is shown only in the footer, clearly labelled as a file timestamp.
- Rows marked with an `est` badge are **modelled, not reported**. COVID-19, Influenza
  and Tuberculosis are reconstructed for every state as a share of that state's
  dataset total, with a fixed per-state variation so the numbers are not identical
  across states.

Dropping a real IDSP outbreak file named `idsp_outbreak_data.csv` or
`idsp_real_data.csv` next to `app.py` switches the dashboard to real data
automatically; the reporting year is then read from the file and shown as the
reporting period.

### Population normalisation

`geo_data.py` holds public reference data used only to normalise counts:

- `POPULATION` — estimated resident population (2025 projection from the 2011 Census of India)
- `DISTRICT_TOTAL` — approximate district count per state/UT (2011 Census, plus later administrative changes)

These power the **cases per lakh** ranking (home page toggle, states table column
and sort) and the district-coverage figures that explain why one state reports
many more districts than another.

## How to Run
1. Install Python
2. Install required packages
3. Run the Flask application
4. Open the local URL in a browser
