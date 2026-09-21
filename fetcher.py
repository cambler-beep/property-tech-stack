"""
fetcher_js.py

A JavaScript-RENDERING fetcher using Playwright, as an alternative to
fetcher.py's plain HTTP requests. This exists to catch content that only
appears after a real browser runs JavaScript -- e.g. a chat widget SDK
that builds its own asset URLs at runtime with no trace in the raw
server-delivered HTML at all (a deeper case than the inline-script-body
pattern fetcher.py's sibling module ai_fallback.py already catches).

SCOPE AND AN INTENTIONAL LIMIT, READ BEFORE MODIFYING:
This module is for RENDERING pages the way a real browser would -- running
JS, letting the DOM settle -- not for evading a site's anti-bot security.
It deliberately does NOT include: stealth/fingerprint-spoofing plugins,
proxy rotation, CAPTCHA-solving, or any other technique whose specific
purpose is to defeat Cloudflare Bot Manager or similar deliberate
bot-detection systems. Sites that actively block automated access (see
the README's "Entrata-integrated sites" note) are expected to still
block this fetcher too -- that's an intentional line, not a bug to fix
by adding evasion techniques on top of this. If a page renders, great;
if a site detects and blocks a headless browser the same way it blocks a
plain request, that's the site's security working as intended, and this
tool should fall back to the plain fetcher / Wayback / "blocked" states
in fetcher.py, not try harder to get through.

DEPLOYMENT NOTE: Playwright needs real Chromium browser binaries, which
Streamlit Community Cloud does not install by default. See README for
the setup workaround (installing the browser on first run) and its
real trade-offs (slow first load, fragility).
"""

from playwright.sync_api import sync_playwright

TIMEOUT_MS = 15000  # JS rendering is slower than a plain request -- budget for it
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_rendered_html(url: str) -> dict:
    """
    Load a page in a real (headless) browser, let JS run, and return the
    fully rendered HTML. No stealth/evasion techniques -- see module
    docstring. A site that blocks this the way it blocks a plain request
    is expected behavior, not something to route around further.

    Returns:
        {"status": "ok" | "error", "html": str, "note": str}
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.set_default_timeout(TIMEOUT_MS)
            try:
                page.goto(url, wait_until="networkidle")
            except Exception:
                # networkidle can time out on pages with long-polling/analytics
                # that never go fully idle -- fall back to whatever loaded
                page.goto(url, wait_until="domcontentloaded")
            html = page.content()
            browser.close()
            return {"status": "ok", "html": html, "note": f"Rendered {len(html)} chars of JS-executed HTML."}
    except Exception as e:
        return {"status": "error", "html": "", "note": f"JS rendering failed: {e}"}
