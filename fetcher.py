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

# Same candidates, but WITHOUT a leading slash, for joining relative to the
# entered URL's own directory rather than the domain root -- see the big
# comment in fetch_site() below for why this exists.
RELATIVE_SUBPAGE_CANDIDATES = [
    "residents/", "residents",
    "resident-portal/", "resident-portal",
    "schedule-a-tour/", "schedule-a-tour",
    "self-guided-tours/", "self-guided-tours",
    "contact/", "contact-us/", "contact",
    "apply/", "apply-now/",
]


def _robots_allows(base_url: str, path: str) -> bool:
    """Check robots.txt before fetching.

    IMPORTANT: does NOT use urllib.robotparser's built-in fetcher. That
    fetcher sends a generic, unbranded request with no real headers --
    many property sites sit behind bot-protection services (Cloudflare,
    etc.) that will 403 a request like that even though the actual page
    content is fine for a normal-looking request. Python's robotparser
    has documented behavior of treating a 403 on robots.txt as "disallow
    everything," which produces false "blocked" results on sites that
    aren't really blocked at all -- caught this in testing 2026-09-21
    after two real, working-looking sites both got flagged.

    Fetches robots.txt ourselves with the same request setup as the rest
    of this tool, and only treats an explicit 200-response "Disallow"
    rule as a real block. Any fetch failure (403, timeout, DNS error,
    robots.txt not existing, etc.) fails OPEN -- we allow the fetch and
    let the real page request be the actual test of reachability.
    """
    try:
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        resp = requests.get(robots_url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
        if resp.status_code != 200:
            return True  # no usable robots.txt -- fail open, don't assume blocked
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(resp.text.splitlines())
        return rp.can_fetch(USER_AGENT, urljoin(base_url, path))
    except Exception:
        return True  # fail open -- a robots.txt fetch problem is not proof of a real block


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
    entered_url = url  # the exact URL as given, full path intact -- see below

    if not _robots_allows(base_url, parsed.path or "/"):
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

    # Build the full list of candidate URLs to check:
    #  1. The EXACT URL the user entered, always first -- this was
    #     previously missing entirely. base_url below strips the path down
    #     to just the domain, so every candidate used to be joined against
    #     the bare root -- meaning a specific property page under a larger
    #     portfolio site (e.g. cortland.com/apartments/cortland-riverview/)
    #     never actually got fetched at all. The tool silently analyzed
    #     just the parent corporate homepage instead, with no indication
    #     anything was wrong. Caught via cortland.com (2026-09-21) -- same
    #     underlying issue as the earlier Simpson Property Group case, but
    #     worse there it happened to still report an honest "not detected"
    #     for a genuinely custom site; here it would have silently
    #     attributed the corporate homepage's tech stack to the wrong page.
    #  2. Root-domain candidates (homepage + common top-level subpages) --
    #     still useful for single-property-domain sites, where the
    #     "corporate homepage" IS the property page.
    #  3. Candidates relative to the ENTERED URL's own directory, for
    #     portfolio sites where resident/contact/apply pages nest under
    #     the property's own subpath rather than the domain root.
    candidate_urls = [entered_url]
    for subpath in SUBPAGE_CANDIDATES:
        candidate_urls.append(urljoin(base_url, subpath))
    if parsed.path and parsed.path != "/":
        for subpath in RELATIVE_SUBPAGE_CANDIDATES:
            candidate_urls.append(urljoin(entered_url, subpath))

    for page_url in candidate_urls:
        try:
            resp = requests.get(
                page_url,
                timeout=TIMEOUT_SECONDS,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=True,
            )
            if resp.status_code == 200:
                # dedupe: multiple candidates often resolve to the same
                # final URL (e.g. the entered URL and a root-level
                # redirect) -- skip if we already have this exact page
                if resp.url in pages_fetched:
                    continue
                html_chunks.append(resp.text)
                pages_fetched.append(resp.url)
        except Exception:
            continue  # this candidate just doesn't exist / timed out -- fine, skip it

    if not html_chunks:
        # Direct fetch failed for every candidate page -- before giving up,
        # try the Wayback Machine. This covers real full-site blocks that
        # don't get caught by the (now much more conservative) robots.txt
        # check above, e.g. a WAF blocking the actual page requests too.
        archived = _try_wayback(url)
        if archived:
            return {
                "status": "ok",
                "combined_html": archived,
                "pages_fetched": [f"{url} (via Wayback Machine)"],
                "used_wayback": True,
                "note": "Could not fetch the live site directly (it may be "
                        "blocking automated requests). Used the most recent "
                        "Wayback Machine snapshot instead -- data may be "
                        "slightly out of date.",
            }
        return {
            "status": "no_data",
            "combined_html": "",
            "pages_fetched": [],
            "used_wayback": False,
            "note": "Could not fetch any pages from this site directly, and "
                    "no Wayback Machine snapshot is available either. The "
                    "site may be blocking automated requests, or may be "
                    "down. Try checking manually.",
        }

    return {
        "status": "ok",
        "combined_html": "\n".join(html_chunks),
        "pages_fetched": pages_fetched,
        "used_wayback": False,
        "note": f"Fetched {len(pages_fetched)} page(s).",
    }
