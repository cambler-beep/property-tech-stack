"""
Property Website Tech Detector
-------------------------------
Paste a property website URL, get back:
  - Website Platform (CMS / builder / agency)
  - PMS (property management system)
  - Detected Partners (from Engrain's partner lists)

Detection order: hard-coded fingerprint rules first (fast, certain, see
fingerprints.py for exactly what's been verified and how), then Gemini
AI fallback for anything not caught by a hard rule (ai_fallback.py).
"""

import subprocess
import streamlit as st

from fetcher import fetch_site
from fetcher_js import fetch_rendered_html
from fingerprints import check_hard_rules, filter_to_highest_confidence
from partner_match import load_all_partner_names, find_partner_mentions, build_signal_text_for_matching, filter_out_already_reported
from ai_fallback import extract_signals, classify_with_ai

st.set_page_config(page_title="Property Tech Detector", page_icon="\U0001F50D", layout="centered")


@st.cache_resource
def _ensure_chromium_installed():
    """Streamlit Community Cloud doesn't install Playwright's Chromium
    binary by default -- this installs it on the app's first run only
    (cached so it doesn't re-run per request). This makes the FIRST
    JS-rendering request after a fresh deploy noticeably slow (a real
    browser download); every request after that is normal speed. See
    README for why this workaround exists and its trade-offs."""
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True, capture_output=True, timeout=180)
        return True
    except Exception:
        return False

st.title("Property Website Tech Detector")
st.caption(
    "Paste a property website URL to identify its website platform, PMS, "
    "and any known Engrain partners detected on the site."
)

# --- Load reference data once ---------------------------------------
@st.cache_data
def get_partner_names():
    return load_all_partner_names()

partner_names = get_partner_names()

# --- API key ----------------------------------------------------------
# Reuse the same Gemini API key setup as Property Transition Researcher.
# In Streamlit Cloud: Settings -> Secrets -> GEMINI_API_KEY = "..."
gemini_api_key = st.secrets.get("GEMINI_API_KEY", None)

# --- Input --------------------------------------------------------------
url = st.text_input("Property website URL", placeholder="https://example-apartments.com")
use_js_rendering = st.checkbox(
    "Also render with JavaScript (slower, ~15s -- catches widgets that build "
    "their own URLs at runtime with no trace in plain HTML at all)",
    value=False,
)
go = st.button("Analyze", type="primary")

if go and url:
    with st.spinner("Fetching site..."):
        fetch_result = fetch_site(url)

    if fetch_result["status"] == "blocked":
        st.error(f"⛔ {fetch_result['note']}")
        st.stop()
    elif fetch_result["status"] == "no_data":
        st.error(f"⚠️ {fetch_result['note']}")
        st.stop()

    if fetch_result["used_wayback"]:
        st.warning(f"ℹ️ {fetch_result['note']}")

    html = fetch_result["combined_html"]

    # Optional: also render the homepage with real JS execution and fold
    # that into what gets analyzed. This is NOT a bot-detection-evasion
    # step -- a site that blocks the plain fetch above will very likely
    # block this too (that's the site's security working as intended, see
    # README). This is purely for catching content that only exists after
    # JS runs on sites that AREN'T actively blocking automated access.
    if use_js_rendering:
        with st.spinner("Setting up JavaScript rendering (first use may take a minute)..."):
            chromium_ok = _ensure_chromium_installed()
        if not chromium_ok:
            st.caption("⚠️ Could not set up JavaScript rendering on this deployment -- skipping.")
        else:
            with st.spinner("Rendering with JavaScript (this takes longer)..."):
                js_result = fetch_rendered_html(url)
            if js_result["status"] == "ok":
                html += "\n" + js_result["html"]
                st.caption(f"✓ {js_result['note']}")
            else:
                st.caption(f"JS rendering didn't add anything: {js_result['note']}")

    # --- Hard rules pass ------------------------------------------------
    with st.spinner("Checking known fingerprints..."):
        hard_matches = check_hard_rules(html)

    platform_matches = hard_matches["platform"]
    pms_matches = hard_matches["pms"]

    needs_platform = len(platform_matches) == 0
    needs_pms = len(pms_matches) == 0

    # Extract the narrow signal set (script/image/link domains + footer text)
    # once -- used by BOTH the AI fallback and partner matching. Partner
    # matching deliberately does NOT scan the full page body copy: short
    # company names collide with ordinary English words in marketing prose
    # (e.g. "Door", "Here", "Fetch" matching "...front door...", "...here...").
    signals = extract_signals(html)

    # --- AI fallback for anything hard rules didn't catch ----------------
    ai_result = {"platform": None, "pms": None, "reasoning": ""}
    if (needs_platform or needs_pms):
        if gemini_api_key:
            with st.spinner("Checking with AI for anything not in the known list..."):
                ai_result = classify_with_ai(
                    signals,
                    known_pms=partner_names["pms"],
                    known_platforms=partner_names["website_provider"],
                    needs_platform=needs_platform,
                    needs_pms=needs_pms,
                    api_key=gemini_api_key,
                )
        else:
            st.info(
                "No GEMINI_API_KEY configured in Streamlit secrets -- skipping "
                "AI fallback. Only hard-rule-confirmed results are shown below."
            )

    # --- Partner mentions -------------------------------------------------
    with st.spinner("Checking for known partners..."):
        signal_text = build_signal_text_for_matching(signals)
        partner_hits = find_partner_mentions(signal_text, partner_names["all_partners"])
        # Don't repeat something already shown as the Website Platform or
        # PMS answer (with real detail) as bare noise in this generic list
        # too -- see partner_match.filter_out_already_reported.
        already_shown = (
            [m["name"] for m in platform_matches] + [m["name"] for m in pms_matches]
        )
        if ai_result["platform"]:
            already_shown.append(ai_result["platform"])
        if ai_result["pms"]:
            already_shown.append(ai_result["pms"])
        partner_hits = filter_out_already_reported(partner_hits, already_shown)

    # ======================================================================
    # RESULTS
    # ======================================================================
    st.divider()
    st.subheader("Results")

    col1, col2 = st.columns(2)

    # Apply the high-confidence-wins filter for DISPLAY only -- the raw,
    # unfiltered platform_matches/pms_matches are still what's used above
    # for needs_platform/needs_pms and the partner-dedup list, since those
    # decisions should reflect everything we actually know, not just what
    # we choose to show.
    platform_display = filter_to_highest_confidence(platform_matches)
    pms_display = filter_to_highest_confidence(pms_matches)

    with col1:
        st.markdown("**Website Platform**")
        if platform_display:
            for m in platform_display:
                badge = "🟢" if m["confidence"] == "high" else "🟡"
                st.write(f"{badge} **{m['name']}**")
                st.caption(f"Confirmed pattern: `{m['matched_pattern']}`")
        elif ai_result["platform"]:
            st.write(f"🔵 **{ai_result['platform']}** *(AI-inferred)*")
            st.caption(ai_result["reasoning"])
        else:
            st.write("— Not detected")

    with col2:
        st.markdown("**PMS**")
        if pms_display:
            for m in pms_display:
                badge = "🟢" if m["confidence"] == "high" else "🟡"
                st.write(f"{badge} **{m['name']}**")
                st.caption(f"Confirmed pattern: `{m['matched_pattern']}`")
        elif ai_result["pms"]:
            st.write(f"🔵 **{ai_result['pms']}** *(AI-inferred)*")
            st.caption(ai_result["reasoning"])
        else:
            st.write("— Not detected")

    st.markdown("**Detected Partners**")
    if partner_hits:
        for hit in partner_hits:
            st.write(f"• {hit['name']}")
    else:
        st.write("— None detected from Engrain's partner list")

    with st.expander("Pages checked"):
        for p in fetch_result["pages_fetched"]:
            st.write(f"- {p}")

    st.divider()
    st.caption(
        "🟢 high confidence · 🟡 moderate confidence (hard rule, less-tested) · "
        "🔵 AI-inferred (Gemini fallback, not a hard-coded rule) — always spot-check "
        "AI-inferred results."
    )

elif go and not url:
    st.warning("Enter a URL first.")
