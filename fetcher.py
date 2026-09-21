"""
fetcher.py

Fetches RAW HTML (script tags included -- this matters, see below) from
a property website's homepage plus a handful of known subpages where
PMS/partner widgets tend to hide.

IMPORTANT LESSON FROM MANUAL TESTING:
A readable-text extraction (like a "reader mode" view) strips <script>
tags entirely, which makes it structurally blind to embedded widgets
like EliseAI/MeetElise or Tour24 -- those are delivered via
<script src="..."> and never appear as visible page text. This fetcher
deliberately grabs raw HTML for that reason. Hard rules and the AI
fallback should both be given this raw HTML, not a cleaned/readable
version.
"""

import requests
import urllib.robotparser
from urllib.parse import urljoin, urlparse

USER_AGENT = "Mozilla/5.0 (compatible; EngrainPropertyTechCheck/1.0; +internal-tool)"
TIMEOUT_SECONDS = 10

# Common subpage paths where PMS / partner widgets tend to live.
# Not every site will have all of these -- 404s are just skipped.
SUBPAGE_CANDIDATES = [
    "",  # homepage itself
    "/residents/", "/residents",
    "/resident-portal/", "/resident-portal",
    "/schedule-a-tour/", "/schedule-a-tour",
    "/self-guided-tours/", "/self-guided-tours",
    "/contact/", "/contact-us/", "/contact",
    "/apply/", "/apply-now/",
]


def _robots_allows(base_url: str, path: str) -> bool:
    """Check robots.txt before fetching. Fails open (allows) if robots.txt
    itself can't be fetched or parsed -- most sites don't have one, and we
    don't want a network hiccup to be mistaken for a real disallow."""
    try:
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, urljoin(base_url, path))
    except Exception:
        return True  # fail open


def _try_wayback(url: str) -> str | None:
    """Fallback: ask the Wayback Machine's public availability API for the
    most recent snapshot of this URL. Returns raw HTML of the snapshot,
    or None if nothing is available."""
    try:
        api_url = f"https://archive.org/wayback/available?url={url}"
        resp = requests.get(api_url, timeout=TIMEOUT_SECONDS)
        data = resp.json()
        snapshot = data.get("archived_snapshots", {}).get("closest")
        if not snapshot or not snapshot.get("available"):
            return None
        snapshot_url = snapshot["url"]
        page = requests.get(snapshot_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        page.raise_for_status()
        return page.text
    except Exception:
        return None


def fetch_site(url: str) -> dict:
    """
    Fetch homepage + known subpages for a property URL.

    Returns:
        {
            "status": "ok" | "blocked" | "no_data",
            "combined_html": str,       # all successfully fetched pages, concatenated
            "pages_fetched": [str],     # which URLs actually succeeded
            "used_wayback": bool,
            "note": str,                # human-readable explanation, esp. for failures
        }
    """
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    if not _robots_allows(base_url, "/"):
        # Blocked by robots.txt -- try Wayback Machine as fallback
        archived = _try_wayback(url)
        if archived:
            return {
                "status": "ok",
                "combined_html": archived,
                "pages_fetched": [f"{url} (via Wayback Machine)"],
                "used_wayback": True,
                "note": "Live site disallows automated access (robots.txt). "
                        "Used the most recent Wayback Machine snapshot instead "
                        "-- data may be slightly out of date.",
            }
        else:
            return {
                "status": "blocked",
                "combined_html": "",
                "pages_fetched": [],
                "used_wayback": False,
                "note": "Site disallows automated access (robots.txt) and no "
                        "Wayback Machine snapshot is available. Try checking "
                        "manually.",
            }

    html_chunks = []
    pages_fetched = []

    for subpath in SUBPAGE_CANDIDATES:
        page_url = urljoin(base_url, subpath)
        try:
            resp = requests.get(
                page_url,
                timeout=TIMEOUT_SECONDS,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=True,
            )
            if resp.status_code == 200:
                html_chunks.append(resp.text)
                pages_fetched.append(resp.url)
        except Exception:
            continue  # this subpage just doesn't exist / timed out -- fine, skip it

    if not html_chunks:
        return {
            "status": "no_data",
            "combined_html": "",
            "pages_fetched": [],
            "used_wayback": False,
            "note": "Could not fetch any pages from this site (site may be "
                    "down, or blocking requests in a way that isn't robots.txt).",
        }

    return {
        "status": "ok",
        "combined_html": "\n".join(html_chunks),
        "pages_fetched": pages_fetched,
        "used_wayback": False,
        "note": f"Fetched {len(pages_fetched)} page(s).",
    }
