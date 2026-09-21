"""
partner_match.py

Loads Engrain's three partner CSVs and provides simple name-matching
against raw page HTML / extracted signal text, so we can flag known
partners (like EliseAI, Tour24, Knock, etc.) that show up on a property
site as embedded widgets, footer credits, or script domains.

This is intentionally simple substring/normalized matching, not a
fuzzy-matching library -- it's cheap, fast, and good enough for
"does this partner's name appear somewhere in the page." The known
brand-name-vs-CSV-name mismatches we found during testing (e.g. CSV
says "eliseai", the live product is branded "MeetElise") are handled
via the ALIASES dict below -- add to this as more mismatches turn up.
"""

import csv
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Known cases where a vendor's live product branding differs from the
# name Engrain tracks them under in the CSVs. Add to this list as you
# discover more (this is exactly the kind of thing that surfaces from
# real usage, not something we can fully predict up front).
ALIASES = {
    "eliseai": ["meetelise", "meet elise", "elise ai"],
    "tour24": ["tour 24", "tour24.com"],
    # add more as discovered, e.g.:
    # "some csv name": ["actual live product/brand name"],
}


def _normalize(name: str) -> str:
    """Lowercase, strip common corporate suffixes and punctuation, so
    'RealPage, Inc.' and 'realpage' both normalize to 'realpage'."""
    name = name.lower().strip()
    name = re.sub(r"[,.]", "", name)
    for suffix in [" inc", " llc", " l l c", " corp", " corporation", " co"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()


def _load_names(csv_path: str, name_col: str = "Account Name") -> list[str]:
    names = []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n = row.get(name_col, "").strip()
            if n and n.lower() not in ("(no value)", "no program", "other",
                                        "no answer/don't know", "own program"):
                names.append(n)
    return names


def load_all_partner_names() -> dict:
    """Returns {"pms": [...], "website_provider": [...], "all_partners": [...]}"""
    return {
        "pms": _load_names(os.path.join(DATA_DIR, "pms.csv")),
        "website_provider": _load_names(os.path.join(DATA_DIR, "website_provider.csv")),
        "all_partners": _load_names(os.path.join(DATA_DIR, "all_partners.csv")),
    }


def find_partner_mentions(html: str, partner_names: list[str]) -> list[dict]:
    """
    Scan raw HTML for mentions of any partner name (normalized substring
    match) or any of its known aliases. Returns a list of
    {"name": <CSV name as written>, "matched_as": <the actual string that hit>}.

    This deliberately does NOT try to be clever about distinguishing "this
    partner's script is embedded" from "this partner's name happens to be
    mentioned in passing" -- for a first pass, surfacing possible mentions
    for a human (the AE) to glance at is the goal, not full certainty.
    Categories like PMS/Website Platform use the hard rules for certainty;
    this partner list is explicitly the lower-confidence / "worth a look"
    tier, per how this tool was scoped.
    """
    html_lower = html.lower()
    matches = []
    seen = set()

    for name in partner_names:
        norm = _normalize(name)
        if len(norm) < 3:
            continue  # skip too-short names, too noisy (e.g. "AB")

        candidates = [norm] + ALIASES.get(norm, [])
        for candidate in candidates:
            if candidate in html_lower and name not in seen:
                matches.append({"name": name, "matched_as": candidate})
                seen.add(name)
                break

    return matches
