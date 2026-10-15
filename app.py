from flask import Flask, render_template, request, abort
import csv
import datetime
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


def site_info():
    return {
        "source_label": DATA_SOURCE["label"],
        "source_detail": DATA_SOURCE["detail"],
        "surveillance_updated": _file_date_label(CSV_PATH),
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


@app.route("/")
def home():
    return render_template("index.html", active="home", stats=get_stats(),
                           library_count=len(diseases_data.DISEASES))


@app.route("/states")
def states():
    return render_template("states.html", active="states", health_data=health_data, source=DATA_SOURCE)


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
