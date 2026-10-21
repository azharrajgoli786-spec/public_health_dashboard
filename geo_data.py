"""Reference geography data used to normalise the dashboard's raw counts.

Nothing in this module comes from the surveillance dataset. It is public
reference information, kept in one place so the normalisation stays easy to
audit and easy to swap out when better figures are available:

* ``POPULATION``     - estimated resident population, projected from the 2011
  Census of India to 2025 (annual growth compounded). Used for the
  "cases per lakh" ranking.
* ``DISTRICT_TOTAL`` - approximate number of districts in each state / UT,
  including later administrative changes. Used to show how much of a state's
  territory is actually reporting.

Keys use the same normalisation as ``app.normalize`` (lower case, dashes and
underscores turned into spaces).
"""

# Estimated resident population, 2025 projection from the 2011 Census.
POPULATION = {
    "andaman and nicobar islands": 410_000,
    "andhra pradesh": 54_800_000,
    "arunachal pradesh": 1_570_000,
    "assam": 35_000_000,
    "bihar": 127_000_000,
    "chandigarh": 1_250_000,
    "chhattisgarh": 30_000_000,
    "dadra and nagar haveli and daman and diu": 650_000,
    "delhi": 21_000_000,
    "goa": 1_570_000,
    "gujarat": 71_500_000,
    "haryana": 30_000_000,
    "himachal pradesh": 7_600_000,
    "jammu and kashmir": 14_000_000,
    "jharkhand": 39_000_000,
    "karnataka": 70_000_000,
    "kerala": 35_900_000,
    "ladakh": 300_000,
    "lakshadweep": 80_000,
    "madhya pradesh": 87_000_000,
    "maharashtra": 127_500_000,
    "manipur": 3_200_000,
    "meghalaya": 3_400_000,
    "mizoram": 1_200_000,
    "nagaland": 2_300_000,
    "odisha": 48_500_000,
    "puducherry": 1_600_000,
    "punjab": 31_000_000,
    "rajasthan": 81_500_000,
    "sikkim": 690_000,
    "tamil nadu": 77_000_000,
    "telangana": 39_000_000,
    "tripura": 4_100_000,
    "uttar pradesh": 236_000_000,
    "uttarakhand": 11_700_000,
    "west bengal": 100_000_000,
}

# Approximate number of districts in each state / UT (2011 Census, plus later
# administrative changes).
DISTRICT_TOTAL = {
    "andaman and nicobar islands": 3,
    "andhra pradesh": 26,
    "arunachal pradesh": 25,
    "assam": 35,
    "bihar": 38,
    "chandigarh": 1,
    "chhattisgarh": 33,
    "dadra and nagar haveli and daman and diu": 3,
    "delhi": 11,
    "goa": 2,
    "gujarat": 33,
    "haryana": 22,
    "himachal pradesh": 12,
    "jammu and kashmir": 20,
    "jharkhand": 24,
    "karnataka": 31,
    "kerala": 14,
    "ladakh": 1,
    "lakshadweep": 1,
    "madhya pradesh": 55,
    "maharashtra": 36,
    "manipur": 16,
    "meghalaya": 12,
    "mizoram": 11,
    "nagaland": 16,
    "odisha": 30,
    "puducherry": 4,
    "punjab": 23,
    "rajasthan": 33,
    "sikkim": 6,
    "tamil nadu": 38,
    "telangana": 33,
    "tripura": 8,
    "uttar pradesh": 75,
    "uttarakhand": 13,
    "west bengal": 23,
}

POPULATION_VINTAGE = "2025 projection from the 2011 Census of India"
DISTRICT_VINTAGE = "2011 Census, plus later administrative changes"

# Union territories, which the UI marks with a "UT" badge next to the name.
UNION_TERRITORIES = {
    "andaman and nicobar islands",
    "chandigarh",
    "dadra and nagar haveli and daman and diu",
    "delhi",
    "jammu and kashmir",
    "ladakh",
    "lakshadweep",
    "puducherry",
}


def is_union_territory(state_key):
    """True when a normalised state key is a union territory."""
    return state_key in UNION_TERRITORIES


def population(state_key):
    """Estimated population for a normalised state key, or None."""
    return POPULATION.get(state_key)


def district_total(state_key):
    """Approximate district count for a normalised state key, or None."""
    return DISTRICT_TOTAL.get(state_key)


def cases_per_lakh(cases, pop):
    """Cases per 100,000 residents, rounded to 1 decimal.

    Returns None when population is unknown so callers can show a dash
    instead of a misleading zero.
    """
    if not pop:
        return None
    return round(cases * 100_000 / pop, 1)


def coverage_pct(reported, total):
    """Percentage of a state's districts that appear in the dataset."""
    if not total:
        return None
    return round(100.0 * reported / total, 1)
