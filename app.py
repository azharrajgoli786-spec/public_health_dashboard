from flask import Flask, render_template, request, abort, make_response
import csv
import datetime
import io
import os
import re
import diseases_data

app = Flask(__name__)

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "india_disease_data_sample.csv")


def normalize(name: str) -> str:
    """Case/space/dash-insensitive normalization for search."""
    name = (name or "").strip().lower()
    name = name.replace("-", " ").replace("_", " ")
    name = re.sub(r"\s+", " ", name)
    return name


IDSP_REAL_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "idsp_outbreak_data.csv"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "idsp_real_data.csv"),
]

DATA_SOURCE = {"label": "Sample", "detail": "demo CSV + estimated legacy diseases"}


def _pick(row, *names):
    for n in names:
        v = row.get(n)
        if v not in (None, ""):
            return str(v)
    return ""


def _to_int(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 0


def load_idsp_real_data(path):
    """Load real IDSP outbreak CSV.

    Accepts Dataful/data.gov.in schema variants:
    state | district_as_per_source/district | disease_illness_name/disease |
    cases | deaths | year/week.
    Aggregates the most recent year only (env IDSP_YEAR overrides).
    Returns (finalized_dict, info_dict) or (None, None) on failure.
    """
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except (OSError, csv.Error):
        return None, None
    if not rows:
        return None, None
    cols = {c.strip().lower() for c in (rows[0].keys() or [])}
    if "state" not in cols:
        return None, None

    want_year = os.environ.get("IDSP_YEAR", "").strip()
    years = set()
    for r in rows:
        y = _pick(r, "year").strip()
        if y.isdigit():
            years.add(int(y))
    year = int(want_year) if want_year.isdigit() else (max(years) if years else 0)

    data, skipped = {}, 0
    for r in rows:
        if year and _pick(r, "year").strip().isdigit() and int(_pick(r, "year").strip()) != year:
            continue
        state = _pick(r, "state").strip()
        district = _pick(r, "district_as_per_source", "district_as_per_lgd", "district").strip()
        disease = _pick(r, "disease_illness_name", "disease", "disease_illness").strip()
        if not state or not disease:
            continue
        cases = _to_int(_pick(r, "cases"))
        if cases <= 0:
            skipped += 1
            continue
        key = normalize(state)
        entry = data.setdefault(key, {
            "display": state.strip(), "cases": 0, "deaths": 0,
            "diseases_set": set(), "disease_cases": {},
            "districts": {}, "district_display": {},
        })
        entry["cases"] += cases
        entry["deaths"] += _to_int(_pick(r, "deaths"))
        entry["diseases_set"].add(disease)
        entry["disease_cases"][disease] = entry["disease_cases"].get(disease, 0) + cases
        if district:
            dkey = normalize(district)
            if dkey not in entry["district_display"]:
                entry["district_display"][dkey] = district
            entry["districts"][dkey] = entry["districts"].get(dkey, 0) + cases

    if not data:
        return None, None
    finalized = {}
    for key in sorted(data.keys()):
        e = data[key]
        districts = {
            e["district_display"][dk]: e["districts"][dk]
            for dk in sorted(e["districts"], key=lambda k: e["districts"][k], reverse=True)
        }
        finalized[key] = {
            "display": e["display"],
            "cases": e["cases"],
            "deaths": e["deaths"],
            "diseases": ", ".join(sorted(e["diseases_set"])),
            "disease_breakdown": dict(sorted(e["disease_cases"].items(), key=lambda kv: kv[1], reverse=True)),
            "districts": districts,
        }
    return finalized, {"label": "IDSP real", "detail": f"{os.path.basename(path)} · year {year} · {len(rows)} outbreak rows"}


def load_health_data():
    """Load, deduplicate and aggregate CSV into {key: {display, cases, diseases, districts}}.

    Dedupes exact duplicate rows, sums cases per district,
    derives total cases and disease list per state.
    Restores legacy surveillance diseases (COVID-19, Influenza,
    Tuberculosis) for every state, proportional to its CSV total.
    Falls back to {} if CSV is missing.
    """
    # Legacy diseases from the original hardcoded dataset, absent from the CSV.
    # Values are shares of the state's CSV total (keeps big states big).
    LEGACY_SHARE = {"COVID-19": 0.12, "Influenza": 0.09, "Tuberculosis": 0.07}
    data = {}
    if not os.path.exists(CSV_PATH):
        return data
    seen = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            state = (row.get("state") or "").strip()
            district = (row.get("district") or "").strip()
            disease = (row.get("disease") or "").strip()
            if not state or not district:
                continue
            try:
                cases = int(str(row.get("cases") or "0").strip())
            except ValueError:
                cases = 0
            # Deduplicate exact rows (CSV contains ~8 exact dups)
            sig = (state.lower(), district.lower(), disease.lower(), cases)
            if sig in seen:
                continue
            seen.add(sig)

            key = normalize(state)
            entry = data.setdefault(key, {
                "display": state,
                "cases": 0,
                "diseases_set": set(),
                "disease_cases": {},
                "districts": {},
                "district_display": {},
            })
            # Aggregate if same district appears twice (different disease/rows)
            dkey = normalize(district)
            if dkey not in entry["district_display"]:
                entry["district_display"][dkey] = district
            entry["districts"][dkey] = entry["districts"].get(dkey, 0) + cases
            entry["cases"] += cases
            if disease:
                entry["diseases_set"].add(disease)
                entry["disease_cases"][disease] = entry["disease_cases"].get(disease, 0) + cases

    # Finalize: sort states A-Z, districts + diseases by cases desc.
    # Add legacy diseases on top; district table stays CSV-only (see footnote in templates).
    finalized = {}
    for key in sorted(data.keys()):
        e = data[key]
        districts = {
            e["district_display"][dk]: e["districts"][dk]
            for dk in sorted(e["districts"], key=lambda k: e["districts"][k], reverse=True)
        }
        base_total = e["cases"]
        for disease, share in LEGACY_SHARE.items():
            extra = max(20, round(base_total * share))
            e["diseases_set"].add(disease)
            e["disease_cases"][disease] = e["disease_cases"].get(disease, 0) + extra
            e["cases"] += extra
        finalized[key] = {
            "display": e["display"],
            "cases": e["cases"],
            "diseases": ", ".join(sorted(e["diseases_set"])),
            "disease_breakdown": dict(sorted(e["disease_cases"].items(), key=lambda kv: kv[1], reverse=True)),
            "districts": districts,
        }
    # Prefer real IDSP file when present; else sample + legacy estimates.
    for _p in IDSP_REAL_PATHS:
        if os.path.exists(_p):
            _real, _info = load_idsp_real_data(_p)
            if _real:
                DATA_SOURCE.update(_info)
                return _real
    return finalized


health_data = load_health_data()


def _file_date_label(path):
    """Honest last-updated label from a file's modification time.

    Returns a YYYY-MM-DD string, or None when the file is missing,
    so templates can show 'Date not available' instead of a guess.
    """
    try:
        ts = os.path.getmtime(path)
    except OSError:
        return None
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def _file_date_display(path):
    """Same date, in a human '14 Nov 2025' format for date fields."""
    try:
        ts = os.path.getmtime(path)
    except OSError:
        return None
    return datetime.datetime.fromtimestamp(ts).strftime("%d %b %Y").lstrip("0")


def site_info():
    return {
        "source_label": DATA_SOURCE["label"],
        "source_detail": DATA_SOURCE["detail"],
        "surveillance_updated": _file_date_label(CSV_PATH),
        "surveillance_updated_display": _file_date_display(CSV_PATH),
        "library_updated": _file_date_label(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "diseases_data.py")
        ),
    }


@app.context_processor
def inject_site():
    return {"site": site_info()}


def get_stats():
    total_states = len(health_data)
    total_districts = sum(len(v["districts"]) for v in health_data.values())
    total_cases = sum(v["cases"] for v in health_data.values())
    all_diseases = set()
    for v in health_data.values():
        for d in v["diseases"].split(","):
            d = d.strip()
            if d:
                all_diseases.add(d)
    return {
        "total_states": total_states,
        "total_districts": total_districts,
        "total_cases": total_cases,
        "total_diseases": len(all_diseases),
        "source_label": DATA_SOURCE["label"],
        "source_detail": DATA_SOURCE["detail"],
    }


def _disease_totals():
    """Cases per disease, summed across all states."""
    totals = {}
    for v in health_data.values():
        for d, c in (v.get("disease_breakdown") or {}).items():
            totals[d] = totals.get(d, 0) + c
    return totals


# Zones used by the States page "Region" filter. Keyed by normalised name.
REGION_BY_STATE = {
    # Northern
    "chandigarh": "Northern", "delhi": "Northern", "haryana": "Northern",
    "himachal pradesh": "Northern", "jammu and kashmir": "Northern",
    "ladakh": "Northern", "punjab": "Northern", "rajasthan": "Northern",
    "uttar pradesh": "Northern", "uttarakhand": "Northern",
    # Western
    "goa": "Western", "gujarat": "Western", "maharashtra": "Western",
    "dadra and nagar haveli and daman and diu": "Western",
    # Central
    "chhattisgarh": "Central", "madhya pradesh": "Central",
    # Eastern
    "bihar": "Eastern", "jharkhand": "Eastern", "odisha": "Eastern",
    "west bengal": "Eastern",
    # Southern
    "andhra pradesh": "Southern", "karnataka": "Southern", "kerala": "Southern",
    "puducherry": "Southern", "tamil nadu": "Southern", "telangana": "Southern",
    "lakshadweep": "Southern", "andaman and nicobar islands": "Southern",
    # North-Eastern
    "arunachal pradesh": "North-Eastern", "assam": "North-Eastern",
    "manipur": "North-Eastern", "meghalaya": "North-Eastern",
    "mizoram": "North-Eastern", "nagaland": "North-Eastern",
    "sikkim": "North-Eastern", "tripura": "North-Eastern",
}

REGIONS = ["Northern", "Western", "Central", "Eastern", "Southern", "North-Eastern"]

# Schematic tile-map positions for the States page map view.
# (column, row) on a grid that loosely mirrors India's geography.
# This is a tile map, not a geographic projection - the page says so.
TILE_POS = {
    "jammu and kashmir": (2, 0), "ladakh": (3, 0),
    "himachal pradesh": (2, 1), "chandigarh": (4, 1),
    "punjab": (3, 2), "uttarakhand": (4, 2),
    "sikkim": (7, 2), "meghalaya": (8, 2), "arunachal pradesh": (9, 2),
    "delhi": (3, 3), "haryana": (4, 3), "rajasthan": (2, 3),
    "uttar pradesh": (5, 3), "bihar": (6, 3), "tripura": (7, 3),
    "assam": (8, 3), "nagaland": (9, 3),
    "gujarat": (1, 4), "madhya pradesh": (4, 4), "jharkhand": (6, 4),
    "west bengal": (7, 4), "manipur": (8, 4),
    "dadra and nagar haveli and daman and diu": (2, 5), "maharashtra": (3, 5),
    "chhattisgarh": (5, 5), "odisha": (7, 5), "mizoram": (9, 5),
    "lakshadweep": (0, 6), "goa": (2, 6), "karnataka": (3, 6),
    "telangana": (4, 6), "andhra pradesh": (5, 6),
    "kerala": (3, 7), "tamil nadu": (4, 7), "puducherry": (5, 7),
    "andaman and nicobar islands": (9, 7),
}


def get_state_rows():
    """Rows for the States page table, map and CSV export."""
    rows = []
    for v in health_data.values():
        key = normalize(v["display"])
        bd = v.get("disease_breakdown") or {}
        top = list(bd.items())[:3]
        rows.append({
            "display": v["display"],
            "key": key,
            "cases": v["cases"],
            "districts": len(v["districts"]),
            "top_diseases": top,
            "diseases": v["diseases"],
            "disease_breakdown": bd,
            "district_rows": list(v["districts"].items()),
            "region": REGION_BY_STATE.get(key, "Other"),
            "tile": TILE_POS.get(key, (5, 4)),
        })
    return rows


def _sort_state_rows(rows, sort):
    if sort == "cases-asc":
        return sorted(rows, key=lambda r: r["cases"])
    if sort == "name-asc":
        return sorted(rows, key=lambda r: r["display"])
    if sort == "districts-desc":
        return sorted(rows, key=lambda r: (-r["districts"], -r["cases"]))
    return sorted(rows, key=lambda r: -r["cases"])


def _filter_state_rows(rows, q, region):
    q = (q or "").strip().lower()
    region = (region or "").strip()
    out = []
    for r in rows:
        if region and r["region"] != region:
            continue
        if q and q not in r["display"].lower() and not any(
            q in d.lower() for d, _ in r["district_rows"]
        ):
            continue
        out.append(r)
    return out


@app.route("/states.csv")
def states_csv():
    """Download the current states view as CSV."""
    rows = _filter_state_rows(
        get_state_rows(),
        request.args.get("q", ""),
        request.args.get("region", ""),
    )
    rows = _sort_state_rows(rows, request.args.get("sort", "cases-desc"))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["State / UT", "Region", "Reported cases", "Districts", "Top diseases"])
    for r in rows:
        w.writerow([
            r["display"],
            r["region"],
            r["cases"],
            r["districts"],
            ", ".join("%s (%d)" % (d, c) for d, c in r["top_diseases"]),
        ])
    resp = make_response(buf.getvalue())
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = (
        'attachment; filename="public-health-states.csv"'
    )
    return resp


@app.route("/states")
def states():
    rows = get_state_rows()
    max_cases = max((r["cases"] for r in rows), default=0)
    for r in rows:
        # 1 (lightest) .. 5 (darkest) bucket for the map view shading.
        r["level"] = 1 + int(4 * (r["cases"] / max_cases)) if max_cases else 1
    return render_template("states.html", active="states", health_data=health_data,
                           source=DATA_SOURCE, rows=_sort_state_rows(rows, "cases-desc"),
                           regions=REGIONS, site=site_info(), stats=get_stats(),
                           total_districts=sum(len(v["districts"]) for v in health_data.values()))



def get_home_data():
    """Aggregates used by the home page hero, chart and pick lists."""
    top_states = sorted(
        (
            {
                "display": v["display"],
                "cases": v["cases"],
                "districts": len(v["districts"]),
            }
            for v in health_data.values()
        ),
        key=lambda r: r["cases"],
        reverse=True,
    )
    totals = _disease_totals()
    top_diseases = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "top_states": top_states,
        "top_diseases": top_diseases,
        "state_names": [v["display"] for v in health_data.values()],
        "surveillance_diseases": sorted(totals.keys()),
        "library_names": [d["name"] for d in diseases_data.DISEASES],
        "chart_states": top_states[:8],
        "chart_diseases": top_diseases[:6],
    }


@app.route("/")
def home():
    return render_template("index.html", active="home", stats=get_stats(),
                           library_count=len(diseases_data.DISEASES),
                           home_data=get_home_data())


@app.route("/find")
def find():
    """Hero finder: disease + place -> surveillance rows and health guide."""
    disease = (request.args.get("disease") or "").strip()
    place = (request.args.get("place") or "").strip()
    view = (request.args.get("view") or "cases").strip()
    q = (request.args.get("q") or "").strip()

    # Global search (top bar): one free-text box that may name a disease or a place.
    if q and not disease and not place:
        surveillance_names = {n.lower() for n in _disease_totals()}
        library_names = {d["name"].lower() for d in diseases_data.DISEASES}
        nq = normalize(q)
        if q.lower() in surveillance_names or q.lower() in library_names:
            disease = q
        elif any(nq in normalize(v["display"]) or any(
            nq in normalize(d) for d in v["districts"]
        ) for v in health_data.values()):
            place = q
        # else: no disease and no place - the template reports no matches.

    nd = normalize(disease)
    np_ = normalize(place)

    # Health guide match (library diseases) for the requested disease.
    guide = None
    if nd:
        for d in diseases_data.DISEASES:
            if normalize(d["name"]) == nd:
                guide = dict(d)
                guide["_transmission"] = diseases_data.transmission_badge(guide)
                guide["_vaccine"] = diseases_data.has_vaccine_note(guide)
                break

    # Surveillance rows for the requested disease (all diseases when blank).
    rows = []
    for v in health_data.values():
        if np_ and np_ not in normalize(v["display"]) and not any(
            np_ in normalize(d) for d in v["districts"]
        ):
            continue
        bd = v.get("disease_breakdown") or {}
        if nd:
            cases = bd.get(disease, 0)
            if cases <= 0:
                continue
        else:
            cases = v["cases"]
        rows.append({
            "display": v["display"],
            "cases": cases,
            "districts": v["districts"],
            "diseases": v["diseases"],
        })
    rows.sort(key=lambda r: r["cases"], reverse=True)

    return render_template(
        "find.html",
        active="home",
        disease=disease,
        place=place,
        query=q,
        view=view,
        guide=guide,
        rows=rows[:15],
        total_matches=len(rows),
        library_count=len(diseases_data.DISEASES),
        state_names=[v["display"] for v in health_data.values()],
        disease_names=sorted(set(_disease_totals().keys()) | {d["name"] for d in diseases_data.DISEASES}),
    )


@app.route("/live_search", methods=["GET", "POST"])
def live_search():
    query = ""
    if request.method == "POST":
        query = request.form.get("search", "")
    else:
        query = request.args.get("search", request.args.get("q", ""))
    query = (query or "").strip()
    results = []
    if query:
        nq = normalize(query)
        # 1. exact match
        if nq in health_data:
            info = health_data[nq]
            results = [(nq, info["display"], info)]
        else:
            # 2. partial/substring match (either direction)
            for key, info in health_data.items():
                if nq in key or key in nq:
                    results.append((key, info["display"], info))
    return render_template("live_search.html", active="search", query=query, results=results, health_data=health_data)


@app.route("/chart")
def chart():
    return render_template("chart.html", active="analytics", health_data=health_data,
                           surveillance_diseases=_surveillance_disease_list())


@app.route("/analytics")
def analytics():
    """Analytics alias: same view as /chart, kept under the nav label."""
    return render_template("chart.html", active="analytics", health_data=health_data,
                           surveillance_diseases=_surveillance_disease_list())


def _surveillance_disease_list():
    names = set()
    for v in health_data.values():
        for d in (v.get("disease_breakdown") or {}):
            names.add(d)
    return sorted(names)


@app.route("/about")
def about():
    return render_template("about.html", active="about")


@app.route("/diseases")
def diseases():
    query = request.args.get("q", request.args.get("search", "")).strip()
    category = request.args.get("category", "").strip()
    letter = request.args.get("letter", "").strip().upper()
    results = diseases_data.search_diseases(query=query, category=category)
    if letter and len(letter) == 1:
        results = [d for d in results if d["name"].upper().startswith(letter)]
    for d in results:
        d["_transmission"] = diseases_data.transmission_badge(d)
        d["_vaccine"] = diseases_data.has_vaccine_note(d)
    return render_template(
        "diseases.html",
        active="diseases",
        diseases=results,
        categories=diseases_data.CATEGORIES,
        category_counts=diseases_data.category_counts(),
        query=query,
        active_category=category,
        active_letter=letter,
        letters=diseases_data.alpha_index(),
        total_count=len(diseases_data.DISEASES),
    )


@app.route("/diseases/<slug>")
def disease_detail(slug):
    disease = diseases_data.get_disease(slug)
    if not disease:
        abort(404)
    # Related: same category, excluding self, up to 3
    related = [d for d in diseases_data.DISEASES if d["category"] == disease["category"] and d["slug"] != slug][:3]
    # Previous / Next in library order
    order = diseases_data.DISEASES
    idx = next((i for i, d in enumerate(order) if d["slug"] == slug), None)
    prev_d = order[idx - 1] if idx is not None and idx > 0 else None
    next_d = order[idx + 1] if idx is not None and idx < len(order) - 1 else None
    disease["_transmission"] = diseases_data.transmission_badge(disease)
    disease["_vaccine"] = diseases_data.has_vaccine_note(disease)
    return render_template("disease_detail.html", active="diseases", disease=disease,
                           related=related, prev_d=prev_d, next_d=next_d)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", active=""), 404


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug)
