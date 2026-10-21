from flask import Flask, render_template, request, abort, make_response
import csv
import datetime
import hashlib
import io
import math
import os
import re
import urllib.parse
import diseases_data
import geo_data

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

DATA_SOURCE = {
    "label": "Sample",
    "detail": "demo CSV + estimated legacy diseases",
    # "sample" means the figures are a demonstration set, not reported
    # surveillance data. The UI leans on this to say so out loud.
    "kind": "sample",
    "is_demo": True,
    # The reporting period, read from the data itself. The sample dataset
    # has no period, so it stays None rather than borrowing the file's
    # modification time - a file timestamp is not a data vintage.
    "period": None,
}


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
    return finalized, {
        "label": "IDSP real",
        "detail": f"{os.path.basename(path)} · year {year} · {len(rows)} outbreak rows",
        "kind": "real",
        "is_demo": False,
        # The reporting year comes from the data, so it is a real vintage.
        "period": str(year) if year else None,
    }


# Legacy diseases from the original hardcoded dataset, absent from the sample
# CSV. Each is modelled as a share of the state's CSV total (so big states stay
# big) with a deterministic per-state variation. An earlier version floored
# every estimate at 20, which made every small state report an identical
# "20 COVID-19, 20 Influenza, 20 TB" - an obvious giveaway that the numbers
# were modelled rather than reported.
LEGACY_SHARE = {"COVID-19": 0.14, "Influenza": 0.09, "Tuberculosis": 0.06}
LEGACY_FLOOR = 1

# District names that look like filler ("Belgaum City 1", "District 3", ...).
# Flagged rather than silently shown as if they were real reporting units.
PLACEHOLDER_DISTRICT = re.compile(
    r"\b(?:city|town|village|district|test|sample|dummy)\s*[-_]?\d+\b", re.IGNORECASE
)


def _legacy_estimate(state_key, disease, base_total, share):
    """Deterministic, state-specific estimate for a legacy surveillance disease.

    The value is stable across runs (it is derived from a hash of the state
    and disease name) but differs from state to state, so the numbers look
    modelled rather than copy-pasted.
    """
    digest = hashlib.sha1(f"{state_key}|{disease}".encode("utf-8")).digest()
    # 0.75 .. 1.25 in 1% steps.
    factor = 0.75 + (int.from_bytes(digest[:2], "big") % 51) / 100.0
    return max(LEGACY_FLOOR, round(base_total * share * factor))


def load_health_data():
    """Load, deduplicate and aggregate CSV into {key: {display, cases, diseases, districts}}.

    Dedupes exact duplicate rows, sums cases per district,
    derives total cases and disease list per state.
    Restores legacy surveillance diseases (COVID-19, Influenza,
    Tuberculosis) for every state, proportional to its CSV total.
    Falls back to {} if CSV is missing.
    """
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
                "synthetic_districts": set(),
            })
            # Aggregate if same district appears twice (different disease/rows)
            dkey = normalize(district)
            if dkey not in entry["district_display"]:
                entry["district_display"][dkey] = district
            entry["districts"][dkey] = entry["districts"].get(dkey, 0) + cases
            entry["cases"] += cases
            if PLACEHOLDER_DISTRICT.search(district):
                entry["synthetic_districts"].add(district)
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
        estimated = {}
        for disease, share in LEGACY_SHARE.items():
            extra = _legacy_estimate(key, disease, base_total, share)
            e["diseases_set"].add(disease)
            e["disease_cases"][disease] = e["disease_cases"].get(disease, 0) + extra
            e["cases"] += extra
            estimated[disease] = extra
        finalized[key] = {
            "display": e["display"],
            "cases": e["cases"],
            "diseases": ", ".join(sorted(e["diseases_set"])),
            "disease_breakdown": dict(sorted(e["disease_cases"].items(), key=lambda kv: kv[1], reverse=True)),
            "districts": districts,
            # Rows that were modelled rather than read from the dataset.
            "estimated": estimated,
            "estimated_diseases": sorted(estimated),
            "synthetic_districts": sorted(e["synthetic_districts"]),
        }
    # Prefer real IDSP file when present; else sample + legacy estimates.
    for _p in IDSP_REAL_PATHS:
        if os.path.exists(_p):
            _real, _info = load_idsp_real_data(_p)
            if _real:
                DATA_SOURCE.update(_info)
                return _add_reference_data(_real)
    return _add_reference_data(finalized)


def _add_reference_data(finalized):
    """Attach population, per-lakh rate and district-coverage reference data.

    Kept separate from the loading path so the same figures are attached
    whether the rows came from the sample CSV or a real IDSP file.
    """
    for key, entry in finalized.items():
        pop = geo_data.population(key)
        total_districts = geo_data.district_total(key)
        reported = len(entry.get("districts") or {})
        entry.setdefault("estimated", {})
        entry.setdefault("estimated_diseases", [])
        entry.setdefault("synthetic_districts", [])
        entry["population"] = pop
        entry["district_total"] = total_districts
        entry["cases_per_lakh"] = geo_data.cases_per_lakh(entry["cases"], pop)
        entry["coverage_pct"] = geo_data.coverage_pct(reported, total_districts)
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
    """Metadata shared with every template.

    ``data_period`` is the reporting period taken from the data itself.
    It is deliberately None for the sample dataset: the sample CSV carries
    no reporting period, and borrowing the file's modification time would
    present a meaningless date as if it were a data vintage (it moves
    whenever anyone touches the file).
    """
    period = DATA_SOURCE.get("period")
    return {
        "source_label": DATA_SOURCE["label"],
        "source_detail": DATA_SOURCE["detail"],
        "source_kind": DATA_SOURCE.get("kind", "sample"),
        "is_demo": bool(DATA_SOURCE.get("is_demo", True)),
        "data_period": period,
        "data_period_display": period or "No reporting period",
        # Kept, but only ever labelled as a file timestamp.
        "file_modified": _file_date_label(CSV_PATH),
        "file_modified_display": _file_date_display(CSV_PATH),
        "surveillance_updated": _file_date_label(CSV_PATH),
        "surveillance_updated_display": _file_date_display(CSV_PATH),
        "library_updated": _file_date_label(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "diseases_data.py")
        ),
        "population_vintage": geo_data.POPULATION_VINTAGE,
        "district_vintage": geo_data.DISTRICT_VINTAGE,
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
    possible_districts = sum(
        (v.get("district_total") or 0) for v in health_data.values()
    )
    estimated_diseases = set()
    for v in health_data.values():
        for d in v.get("estimated_diseases") or []:
            estimated_diseases.add(d)
    return {
        "total_states": total_states,
        "total_districts": total_districts,
        "total_cases": total_cases,
        "total_diseases": len(all_diseases),
        "source_label": DATA_SOURCE["label"],
        "source_detail": DATA_SOURCE["detail"],
        "source_kind": DATA_SOURCE.get("kind", "sample"),
        "is_demo": bool(DATA_SOURCE.get("is_demo", True)),
        "possible_districts": possible_districts or None,
        "coverage_pct": geo_data.coverage_pct(total_districts, possible_districts),
        "estimated_diseases": sorted(estimated_diseases),
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
        estimated = v.get("estimated") or {}
        rows.append({
            "display": v["display"],
            "key": key,
            "cases": v["cases"],
            "districts": len(v["districts"]),
            "district_total": v.get("district_total"),
            "coverage_pct": v.get("coverage_pct"),
            "population": v.get("population"),
            "cases_per_lakh": v.get("cases_per_lakh"),
            "top_diseases": top,
            "diseases": v["diseases"],
            "disease_breakdown": bd,
            "estimated": estimated,
            "estimated_diseases": v.get("estimated_diseases") or [],
            "synthetic_districts": v.get("synthetic_districts") or [],
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
    if sort == "per-lakh-desc":
        # States without a population figure sort last, not first.
        return sorted(rows, key=lambda r: (-(r["cases_per_lakh"] or -1), -r["cases"]))
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


STATES_PER_PAGE = 10


def _states_url(**kwargs):
    """Build a /states URL that keeps the current filters."""
    q = request.args.get("q", "")
    region = request.args.get("region", "")
    sort = request.args.get("sort", "cases-desc")
    view = request.args.get("view", "table")
    params = {"q": q, "region": region, "sort": sort, "view": view}
    params.update(kwargs)
    parts = []
    for k, v in params.items():
        if v in (None, ""):
            continue
        parts.append("%s=%s" % (k, urllib.parse.quote(str(v))))
    return "/states" + ("?" + "&".join(parts) if parts else "")


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
    w.writerow([
        "State / UT", "Region", "Reported cases", "Cases per lakh",
        "Districts reporting", "Districts in state", "Top diseases",
    ])
    for r in rows:
        w.writerow([
            r["display"],
            r["region"],
            r["cases"],
            r["cases_per_lakh"] if r["cases_per_lakh"] is not None else "",
            r["districts"],
            r["district_total"] if r["district_total"] is not None else "",
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
    """States table.

    Filtering, sorting and pagination all happen on the server so the page
    stays light: only the current page of states (and their detail panels)
    is sent to the browser, instead of every state and every district
    breakdown.
    """
    all_rows = get_state_rows()
    max_cases = max((r["cases"] for r in all_rows), default=0)
    for r in all_rows:
        # 1 (lightest) .. 5 (darkest) bucket for the map view shading.
        r["level"] = 1 + int(4 * (r["cases"] / max_cases)) if max_cases else 1

    q = request.args.get("q", "")
    region = request.args.get("region", "")
    sort = request.args.get("sort", "cases-desc")
    view = "map" if request.args.get("view") == "map" else "table"
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    page = max(1, page)

    filtered = _filter_state_rows(all_rows, q, region)
    filtered = _sort_state_rows(filtered, sort)
    total = len(filtered)
    pages = max(1, math.ceil(total / STATES_PER_PAGE))
    page = min(page, pages)
    start = (page - 1) * STATES_PER_PAGE
    rows = filtered[start:start + STATES_PER_PAGE]

    # States outside the current filter stay on the tile map, but dimmed.
    visible_keys = {r["key"] for r in filtered}
    for r in all_rows:
        r["dimmed"] = r["key"] not in visible_keys

    # Pagination links keep the current filters.
    page_urls = {n: _states_url(page=n) for n in range(1, pages + 1)}
    prev_url = _states_url(page=page - 1) if page > 1 else None
    next_url = _states_url(page=page + 1) if page < pages else None
    # Each tile links to the table filtered down to that one state. The URL
    # stays short because only non-default filters are included.
    tile_urls = {}
    for r in all_rows:
        params = ["q=" + urllib.parse.quote(r["display"])]
        if sort != "cases-desc":
            params.append("sort=" + urllib.parse.quote(sort))
        if view == "map":
            params.append("view=table")
        tile_urls[r["key"]] = "/states?" + "&".join(params)

    return render_template(
        "states.html", active="states", health_data=health_data,
        source=DATA_SOURCE, rows=rows, all_rows=all_rows,
        regions=REGIONS, site=site_info(), stats=get_stats(),
        total_districts=sum(len(v["districts"]) for v in health_data.values()),
        q=q, region=region, sort=sort, view=view, page=page, pages=pages,
        total_results=total, start=start,
        page_urls=page_urls, prev_url=prev_url, next_url=next_url,
        tile_urls=tile_urls,
        view_table_url=_states_url(view="table", page=1),
        view_map_url=_states_url(view="map", page=1),
    )


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

    # Both rankings for the home chart: raw counts and population-adjusted.
    state_metrics = sorted(
        (
            {
                "display": v["display"],
                "cases": v["cases"],
                "per_lakh": v.get("cases_per_lakh"),
                "districts": len(v["districts"]),
            }
            for v in health_data.values()
        ),
        key=lambda r: -r["cases"],
    )
    by_lakh = sorted(
        (r for r in state_metrics if r["per_lakh"] is not None),
        key=lambda r: -r["per_lakh"],
    )
    return {
        "top_states": top_states,
        "top_diseases": top_diseases,
        "state_names": [v["display"] for v in health_data.values()],
        "surveillance_diseases": sorted(totals.keys()),
        "library_names": [d["name"] for d in diseases_data.DISEASES],
        "chart_states": top_states[:8],
        "chart_diseases": top_diseases[:6],
        "state_metrics": state_metrics,
        "chart_states_per_lakh": by_lakh[:8],
        "highest_per_lakh": by_lakh[0] if by_lakh else None,
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


def analytics_payload():
    """Compact data for the analytics page.

    Everything the page needs to redraw itself lives here, so changing a
    filter never needs a round trip to the server.
    """
    states = []
    for v in health_data.values():
        key = normalize(v["display"])
        states.append({
            "display": v["display"],
            "cases": v["cases"],
            "isUT": geo_data.is_union_territory(key),
            "perLakh": v.get("cases_per_lakh"),
            "districts": [
                {"name": d, "cases": c} for d, c in v["districts"].items()
            ],
            "diseases": v.get("disease_breakdown") or {},
        })
    states.sort(key=lambda s: -s["cases"])
    diseases = sorted(
        {d for v in health_data.values() for d in (v.get("disease_breakdown") or {})}
    )
    return {"states": states, "diseases": diseases}


@app.route("/chart")
@app.route("/analytics")
def chart():
    """Analytics: KPIs, a sample trend, a state ranking and a disease mix."""
    return render_template(
        "chart.html", active="analytics", stats=get_stats(),
        payload=analytics_payload(),
    )


@app.route("/about")
def about():
    return render_template("about.html", active="about", stats=get_stats(),
                           library_count=len(diseases_data.DISEASES))


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
        d["_icon"] = diseases_data.icon_for(d)
        d["_tone"] = diseases_data.tone_for(d)
        d["_short"] = diseases_data.short_category(d)
    return render_template(
        "diseases.html",
        active="diseases",
        diseases=results,
        categories=diseases_data.CATEGORIES,
        category_counts=diseases_data.category_counts(),
        category_cards=diseases_data.category_cards(),
        popular=diseases_data.popular_diseases(),
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
    disease["_icon"] = diseases_data.icon_for(disease)
    disease["_tone"] = diseases_data.tone_for(disease)
    disease["_short"] = diseases_data.short_category(disease)
    for r in related:
        r["_icon"] = diseases_data.icon_for(r)
        r["_tone"] = diseases_data.tone_for(r)
        r["_short"] = diseases_data.short_category(r)
    return render_template("disease_detail.html", active="diseases", disease=disease,
                           related=related, prev_d=prev_d, next_d=next_d)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", active=""), 404


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug)
