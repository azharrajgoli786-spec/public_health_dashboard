"""Deterministically expand the sample CSV into a monthly series.

SAMPLE DATA FOR UI DEMONSTRATION ONLY - these are synthetic figures, not
official surveillance data. The dashboard labels them as such everywhere.

What it does:
  * Reads the current sample CSV (state, district, disease, cases rows),
    dropping exact duplicate rows exactly like app.load_health_data does.
  * Splits every row's total across 24 complete months (2024-11 .. 2026-10)
    using a deterministic per-row seed plus a mild seasonal curve, with a
    largest-remainder allocation so the monthly values sum EXACTLY to the
    original total. Every state / district / disease aggregate therefore
    stays identical to before - only the time dimension is new.
  * Output schema: date,state,district,disease,cases
      date    - YYYY-MM (complete months only)
      cases   - integer >= 0 (zero months are omitted)
    The unused `vaccinated` column is dropped. Population is NOT duplicated
    here: it stays in geo_data.py as the single source of truth.

Run:  python gen_sample_series.py
"""
import csv
import hashlib
import random

CSV_IN = "india_disease_data_sample.csv"
CSV_OUT = "india_disease_data_sample.csv"
MONTHS = 24
END_YEAR, END_MONTH = 2026, 10  # last complete month

# Relative monthly weight (Jan..Dec). Water/vector-borne diseases peak in the
# monsoon; chickenpox is flatter with a spring bump. Purely illustrative shape.
SEASON = {
    "dengue":      [0.30, 0.25, 0.30, 0.40, 0.60, 0.90, 1.40, 1.60, 1.50, 1.10, 0.60, 0.40],
    "malaria":     [0.30, 0.25, 0.30, 0.40, 0.60, 0.90, 1.40, 1.60, 1.50, 1.10, 0.60, 0.40],
    "cholera":     [0.40, 0.35, 0.40, 0.50, 0.70, 1.00, 1.30, 1.40, 1.20, 0.90, 0.60, 0.50],
    "typhoid":     [0.50, 0.45, 0.50, 0.60, 0.80, 1.10, 1.30, 1.30, 1.10, 0.90, 0.70, 0.60],
    "chickenpox":  [0.90, 1.00, 1.20, 1.30, 1.10, 0.90, 0.80, 0.80, 0.90, 1.00, 1.00, 0.90],
}
FLAT = [1.0] * 12


def month_list(n=MONTHS, end_y=END_YEAR, end_m=END_MONTH):
    out = []
    y, m = end_y, end_m
    for _ in range(n):
        out.append("%04d-%02d" % (y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return sorted(out)


def seed_of(*parts):
    return int.from_bytes(hashlib.sha1("|".join(parts).encode("utf-8")).digest()[:4], "big")


def allocate(total, weights):
    """Split `total` into integers summing exactly to it (largest remainder)."""
    if total <= 0:
        return [0] * len(weights)
    s = sum(weights)
    if s <= 0:
        return [0] * len(weights)
    raw = [total * w / s for w in weights]
    base = [int(x) for x in raw]
    short = total - sum(base)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - base[i], reverse=True)
    for i in order[:short]:
        base[i] += 1
    return base


def main():
    with open(CSV_IN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Mirror app.load_health_data's exact-duplicate removal so totals match.
    seen, groups = set(), {}
    for r in rows:
        state = (r.get("state") or "").strip()
        district = (r.get("district") or "").strip()
        disease = (r.get("disease") or "").strip()
        try:
            cases = int(str(r.get("cases") or "0").strip())
        except ValueError:
            cases = 0
        if not state or not district:
            continue
        sig = (state.lower(), district.lower(), disease.lower(), cases)
        if sig in seen:
            continue
        seen.add(sig)
        groups[(state, district, disease)] = groups.get((state, district, disease), 0) + cases

    periods = month_list()
    out_rows = []
    for (state, district, disease), total in groups.items():
        rng = random.Random(seed_of(state, district, disease))
        curve = SEASON.get(disease.lower(), FLAT)
        weights = []
        for p in periods:
            month = int(p[5:7])
            jitter = 0.7 + 0.6 * rng.random()  # deterministic per row
            weights.append(curve[month - 1] * jitter)
        for p, c in zip(periods, allocate(total, weights)):
            if c > 0:
                out_rows.append({"date": p, "state": state, "district": district,
                                 "disease": disease, "cases": str(c)})

    out_rows.sort(key=lambda r: (r["state"], r["district"], r["disease"], r["date"]))
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "state", "district", "disease", "cases"])
        w.writeheader()
        w.writerows(out_rows)

    # Sanity: per-key totals must equal the input totals.
    check = {}
    for r in out_rows:
        k = (r["state"], r["district"], r["disease"])
        check[k] = check.get(k, 0) + int(r["cases"])
    assert check == groups, "total mismatch!"
    print("rows in: %d (deduped groups: %d) -> rows out: %d, months: %d"
          % (len(rows), len(groups), len(out_rows), len(periods)))
    print("period range: %s .. %s" % (periods[0], periods[-1]))
    print("all group totals preserved: True")


if __name__ == "__main__":
    main()
