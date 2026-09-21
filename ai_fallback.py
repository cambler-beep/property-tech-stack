"""
ai_fallback.py

For anything the hard rules (fingerprints.py) don't catch, this module
extracts the key signals from the raw page HTML (script domains, meta
tags, footer-area text -- NOT the whole page, to keep this cheap and
fast) and asks Gemini to identify the CMS/website platform and PMS,
matching against Engrain's known vendor lists where possible.

This is explicitly the LOWER-confidence layer. Anything it returns
should be labeled as "AI-inferred" in the UI, distinct from the
"confirmed" hard-rule matches, so an AE can tell the difference at a
glance.
"""

import json
import re
from google import genai

MODEL_NAME = "gemini-2.5-flash"  # fast/cheap -- adjust to whatever model
                                   # your Transition Researcher app already
                                   # uses, for consistency


def extract_signals(html: str) -> dict:
    """Pull out the lightweight signals worth sending to the model,
    instead of the full raw HTML (which can be huge and mostly noise)."""

    # All external script/link src domains
    script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.I)
    link_hrefs = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html, re.I)
    img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)

    def domains_from(urls):
        domains = set()
        for u in urls:
            m = re.search(r'https?://([^/"\']+)', u)
            if m:
                domains.add(m.group(1))
        return sorted(domains)

    # Meta generator tag, if present
    generator_match = re.search(
        r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.I)
    generator = generator_match.group(1) if generator_match else None

    # Rough footer text -- last ~3000 chars of the page tends to hold
    # copyright lines, "powered by" credits, legal links
    footer_snippet = html[-3000:]
    footer_text = re.sub(r'<[^>]+>', ' ', footer_snippet)
    footer_text = re.sub(r'\s+', ' ', footer_text).strip()

    return {
        "script_domains": domains_from(script_srcs),
        "link_domains": domains_from(link_hrefs),
        "image_domains": domains_from(img_srcs),
        "meta_generator": generator,
        "footer_text_snippet": footer_text[:1500],
    }


def classify_with_ai(signals: dict, known_pms: list[str], known_platforms: list[str],
                      needs_platform: bool, needs_pms: bool, api_key: str) -> dict:
    """
    Ask Gemini to identify the website platform and/or PMS from the
    extracted signals. Only asks about whichever category the hard
    rules didn't already resolve (needs_platform / needs_pms flags).

    Returns: {"platform": str|None, "pms": str|None, "reasoning": str}
    A None value means the model also couldn't determine it -- that's a
    valid, honest answer, not a failure.
    """
    if not needs_platform and not needs_pms:
        return {"platform": None, "pms": None, "reasoning": "Not needed -- hard rules resolved both."}

    client = genai.Client(api_key=api_key)

    ask_for = []
    if needs_platform:
        ask_for.append("website platform/CMS/builder (who built or hosts this site)")
    if needs_pms:
        ask_for.append("property management system (PMS) software")

    prompt = f"""You are helping identify the technology behind a multifamily
apartment property website, based on signals extracted from its HTML.

Signals found on the page:
- Script domains: {signals['script_domains']}
- Stylesheet/link domains: {signals['link_domains']}
- Image/asset domains: {signals['image_domains']}
- <meta name="generator"> tag: {signals['meta_generator']}
- Footer text snippet: {signals['footer_text_snippet']}

Known PMS vendors to consider (a match should be one of these if possible,
but if you're confident it's something else, say so): {known_pms[:60]}

Known website platform/agency vendors to consider (same rule -- prefer
this list if it fits, otherwise say what you actually see):
{known_platforms[:60]}

Based on these signals, identify the {' and '.join(ask_for)}.

Respond in this exact JSON format, nothing else:
{{"platform": "<name or null>", "pms": "<name or null>", "reasoning": "<one sentence>"}}

If you cannot determine one of these with reasonable confidence, use null
for that field rather than guessing. Only fill in the field(s) that were asked for above; leave the other as null.
"""

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = response.text.strip()
        # Strip markdown code fences if the model added them
        text = re.sub(r'^```json\s*|\s*```$', '', text.strip())
        result = json.loads(text)
        return {
            "platform": result.get("platform") if needs_platform else None,
            "pms": result.get("pms") if needs_pms else None,
            "reasoning": result.get("reasoning", ""),
        }
    except Exception as e:
        return {"platform": None, "pms": None, "reasoning": f"AI classification failed: {e}"}
