# Property Website Tech Detector

Paste a property website URL, get back its **Website Platform** (CMS/builder/agency),
**PMS** (property management system), and any **Engrain partners** detected on the site.

Built the same way as Property Transition Researcher: Streamlit + Python, deployed via
Streamlit Community Cloud, using the Gemini API.

## How detection works

1. **Fetch** — pulls raw HTML (not a "reader view" -- this matters, see below) from the
   homepage plus a handful of common subpages (`/residents/`, `/schedule-a-tour/`,
   `/self-guided-tours/`, `/contact/`, etc.), since PMS and partner widgets often only
   appear on specific subpages, not the homepage.
2. **Hard rules** (`fingerprints.py`) — checks the fetched HTML against a set of
   patterns verified against real, live sites (see the `source` field on each rule
   for exactly which test confirmed it). If a hard rule matches, that result is
   shown as high confidence and the AI step is skipped for that category.
3. **AI fallback** (`ai_fallback.py`) — only runs for whatever the hard rules didn't
   catch. Extracts script domains, meta tags, and footer text, and asks Gemini to
   identify the platform/PMS, preferring names from Engrain's own vendor lists.
   Results from this step are labeled "AI-inferred" in the UI — they're a best
   guess, not a certainty, and should be spot-checked.
4. **Partner matching** (`partner_match.py`) — scans the fetched HTML for mentions
   of any name in `data/all_partners.csv` (1,126 names), including a couple of known
   brand-name aliases (e.g. the CSV says "eliseai", the live product is branded
   "MeetElise" — add more aliases to `ALIASES` in that file as you find them).

## Setup (Streamlit Community Cloud)

1. Push this folder to a GitHub repo (same pattern as Transition Researcher).
2. In Streamlit Cloud, deploy pointing at `app.py`.
3. Under **Settings → Secrets**, add:
   ```
   GEMINI_API_KEY = "your-key-here"
   ```
   (Reuse the same key you already have approved for Transition Researcher.)
4. If you ever update the partner CSVs, just replace the files in `data/` and
   push — no code changes needed.

## Known limitations (read before trusting results blindly)

- **No JavaScript execution.** This fetches raw HTML only — it will miss anything
  that gets injected purely client-side *after* the page loads with no trace in
  the initial HTML (rare, but possible). We deliberately scoped this out for v1
  per our earlier discussion — can revisit if it turns out to matter often.
- **robots.txt-blocked sites** fall back to the Wayback Machine's most recent
  snapshot, if one exists. If neither works, the tool reports "blocked" rather
  than guessing.
- **AI-inferred results (🔵) are not certain.** Gemini is doing its best from
  limited signals — treat these as a starting point, not a final answer, until
  you've spot-checked enough of them to trust the accuracy.
- **The hard-rule set is a starting point, not exhaustive.** Confirmed today:
  G5, Jonah Digital, Apartments247, Entrata, RealPage LeaseStar, Duda (moderate
  confidence), WordPress, AppFolio, and RealPage-via-LOFT. That's roughly a
  dozen vendors out of the ~90 that matter (per the Revyse-validated shortlist
  from our research phase) — the rest currently fall to the AI layer. **The
  most valuable way to improve this tool over time is adding more hard rules**
  as you run it on more sites and see what the AI layer catches (or misses) --
  each new confirmed pattern makes the tool faster, cheaper, and more certain.
- **Partner matching is intentionally loose** — it flags *possible* mentions of
  partner names, not confirmed active integrations. Good for "worth a second
  look," not for "definitely integrated."

## Files

- `app.py` — Streamlit UI
- `fetcher.py` — page fetching, robots.txt check, Wayback fallback
- `fingerprints.py` — hard-coded detection rules (edit this to add more)
- `partner_match.py` — partner CSV loading + name matching
- `ai_fallback.py` — Gemini-based classifier for anything hard rules miss
- `data/` — Engrain's PMS / Website Provider / All Partners CSVs
