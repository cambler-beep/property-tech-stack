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
import re  # noqa: F401 (used below for word-boundary matching)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Known cases where a vendor's live product branding differs from the
# name Engrain tracks them under in the CSVs. Add to this list as you
# discover more (this is exactly the kind of thing that surfaces from
# real usage, not something we can fully predict up front).
ALIASES = {
    "eliseai": ["meetelise", "meet elise", "elise ai"],
    "tour24": ["tour 24", "tour24.com"],
    "funnel": ["funnelleasing"],  # CSV says "Funnel", live product/domain is
                                    # "funnelleasing.com" -- the word-boundary
                                    # match (added to stop "door" matching
                                    # inside "outdoor") has the side effect of
                                    # also missing "funnel" as a prefix of a
                                    # longer compound word with no separator.
                                    # Confirmed via thegantrydc.com (2026-09-21).
    "apartment list": ["lea.ai", "lea ai"],  # CSV says "Apartment List", live
                                    # product is an AI chat widget branded
                                    # "Lea" (domain ai-chat-frontend.lea.ai).
                                    # BuiltWith independently confirms "Lea
                                    # AparmentList" [their typo] as a real
                                    # leasing/lead-gen tool -- same company,
                                    # different sub-brand for the AI chat
                                    # product. Confirmed via livebakerblock.com
                                    # (2026-09-21).
    # add more as discovered, e.g.:
    # "some csv name": ["actual live product/brand name"],
}

# Legitimate brand names under the 5-character length floor (see
# find_partner_mentions below) that are NOT ordinary English words, so
# the false-positive risk that floor exists for doesn't apply to them.
# The floor exists to stop things like "Door"/"Here"/"Fetch" matching in
# ordinary marketing copy -- these names don't have that problem, they're
# just short. Add to this list rather than lowering the floor globally,
# which would reopen that exact risk for every other short common word.
SHORT_NAME_EXCEPTIONS = {
    "hyly",  # real estate marketing/attribution platform -- confirmed via
             # simpsonpropertygroup.com (2026-09-21), silently filtered by
             # the length floor despite being a real, distinctive brand name
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


def filter_out_already_reported(partner_hits: list[dict], already_reported_names: list[str]) -> list[dict]:
    """
    Remove any partner match whose normalized name overlaps with something
    already shown under Website Platform or PMS. Otherwise a vendor with
    BOTH a specific hard rule AND a generic CRM listing (e.g. Repli --
    has its own "Repli (MultiHub)" platform rule, but is also just
    "REPLI" in all_partners.csv) shows up twice: once with real detail,
    once again as bare noise in the generic list. Caught via
    songbirdkirkwood.com (2026-09-21) -- Repli appeared in both places.

    Uses SUBSTRING containment, not exact equality -- rule names carry
    descriptive suffixes the bare CSV name won't have (e.g. "repli" vs
    "repli (multihub)", "entrata" vs "entrata (embedded widget)"), so an
    exact-match check misses these; a first version of this function had
    exactly that bug and didn't actually filter anything (caught in
    testing immediately after writing it, 2026-09-21).
    """
    already_normalized = [_normalize(n) for n in already_reported_names]
    result = []
    for hit in partner_hits:
        hit_norm = _normalize(hit["name"])
        overlaps = any(
            hit_norm in already or already in hit_norm
            for already in already_normalized
            if already  # skip empty strings
        )
        if not overlaps:
            result.append(hit)
    return result


def find_partner_mentions(signal_text: str, partner_names: list[str]) -> list[dict]:
    """
    Scan a NARROW slice of signal text (script/image/link domains + footer
    area text -- see ai_fallback.extract_signals(), NOT the full raw page
    HTML/body copy) for mentions of any partner name or its known aliases.

    IMPORTANT: this must NOT be called with the full page HTML. Partner
    logos and integration credits live in domains (script src, img src)
    and footer/badge areas -- not scattered through marketing prose. Early
    testing (2026-09-21, parkplaceapartmentsclt.com) found that scanning
    full-page body copy produces heavy false positives: short company
    names like "Door", "Here", "Fetch", "Avo", "Further", "Landing" match
    as ordinary English words used in the page's marketing copy (e.g.
    "...easy access to your front door...", "...further questions...").
    Narrowing to domains + footer text, plus a word-boundary regex match
    (not raw substring) and a length floor, is the fix.

    Returns [{"name": <CSV name as written>, "matched_as": <string that hit>}]
    """
    text_lower = signal_text.lower()
    matches = []
    seen = set()

    for name in partner_names:
        norm = _normalize(name)
        if len(norm) < 5 and norm not in SHORT_NAME_EXCEPTIONS:
            continue  # short names are too collision-prone with ordinary words,
                       # unless explicitly allowlisted above as safe

        candidates = [norm] + ALIASES.get(norm, [])
        for candidate in candidates:
            # word-boundary match, not raw substring -- "door" won't match
            # inside "outdoor", and short/common words are already filtered
            # by the length floor above
            pattern = r'\b' + re.escape(candidate) + r'\b'
            if re.search(pattern, text_lower) and name not in seen:
                matches.append({"name": name, "matched_as": candidate})
                seen.add(name)
                break

    return matches


def build_signal_text_for_matching(signals: dict) -> str:
    """
    Combine the narrow signal set (from ai_fallback.extract_signals) into
    one string suitable for find_partner_mentions -- domains plus footer
    text, deliberately excluding the full page body copy.
    """
    parts = (
        signals.get("script_domains", [])
        + signals.get("link_domains", [])
        + signals.get("image_domains", [])
        + signals.get("anchor_domains", [])
        + signals.get("inline_script_domains", [])
        + [signals.get("footer_text_snippet", "") or ""]
    )
    return " ".join(parts)
