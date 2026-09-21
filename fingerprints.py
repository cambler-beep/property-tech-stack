"""
fingerprints.py

Hard-coded, high-confidence detection rules for property website
technology stacks. Every rule in HARD_RULES below was verified against
a real, live property website during manual testing on 2026-09-21 --
see the "source" field on each rule for exactly which test site
confirmed it and what the actual signal looked like.

These rules run FIRST, before any AI-assisted fallback. A rule match
here is treated as high-confidence / certain. If nothing matches, the
caller should fall back to the Gemini-assisted classifier in
ai_fallback.py.

Each rule is a dict with:
    name        -- the vendor/product name to report
    category    -- "platform" (website builder/CMS/agency) or "pms"
    patterns    -- list of strings; if ANY appears (case-insensitive
                   substring match) in the raw page HTML, the rule fires
    confidence  -- "high" or "moderate" (moderate = pattern is a strong
                   signal but wasn't independently double-confirmed)
    source      -- human-readable note on where this was validated
"""

HARD_RULES = [
    # ---------------------------------------------------------------
    # WEBSITE PLATFORM / CMS rules
    # ---------------------------------------------------------------
    {
        "name": "G5",
        "category": "platform",
        "patterns": [
            "g5-assets-cld-res.cloudinary.com",
            "g5-c-", "g5-cl-",  # path segments seen in G5 asset URLs
        ],
        "confidence": "high",
        "source": "Confirmed on ethosapartments.com (2 independent signals: "
                   "every image asset routed through this Cloudinary path).",
    },
    {
        "name": "Jonah Digital (Jonah Systems)",
        "category": "platform",
        "patterns": [
            "jonah systems",
            "jonahdigital.com",
        ],
        "confidence": "high",
        "source": "Confirmed on treehausclemson.com via <meta name=\"generator\"> "
                   "tag AND explicit footer link to jonahdigital.com. Note: "
                   "BuiltWith showed the underlying engine is actually "
                   "WordPress + Elementor -- Jonah is the AGENCY/builder, "
                   "not necessarily the raw CMS. Report as platform/builder.",
    },
    {
        "name": "Apartments247",
        "category": "platform",
        "patterns": [
            "files.apts247.com",
            "/gridmedia/img/",
            "apartments247.com",
        ],
        "confidence": "high",
        "source": "Confirmed on ghpmgmt.com (known Apartments247 customer, "
                   "verified via idatalabs customer list): shared asset "
                   "domain files.apts247.com, /gridmedia/ path structure, "
                   "explicit footer credit.",
    },
    {
        "name": "Entrata",
        "category": "platform",
        "patterns": [
            "medialibrarycfo.entrata.com",
            "medialibrarycf.entrata.com",
            "commoncf.entrata.com",
            "entrata, inc.",
            "entrata's accessibility statement",
        ],
        "confidence": "high",
        "source": "Confirmed on mirageatsouthpoint.com: entrata.com asset "
                   "subdomains + explicit 'Entrata, Inc.' footer copyright "
                   "and accessibility statement. (Note: w3techs had this "
                   "site mis-tagged as 'Yardi' -- likely stale data from "
                   "before a platform migration. Trust the live HTML over "
                   "third-party trackers.)",
    },
    {
        "name": "RealPage LeaseStar",
        "category": "platform",
        "patterns": [
            "myleasestar.com",
            "capi.myleasestar.com",
            "realpage.com/apartment-marketing",
        ],
        "confidence": "high",
        "source": "Confirmed on parkplaceapartmentsclt.com: image CDN on "
                   "capi.myleasestar.com + explicit footer link to "
                   "realpage.com/apartment-marketing. LeaseStar is RealPage's "
                   "own website/marketing product (confirmed via RealPage's "
                   "own press releases, brand active since 2012). NOTE: this "
                   "can co-occur with RealPage as PMS (via LOFT) on the same "
                   "site -- report both, they are different product lines "
                   "of the same parent company.",
    },
    {
        "name": "Duda",
        "category": "platform",
        "patterns": [
            "irp.cdn-website.com",
            "cdn-website.com",
        ],
        "confidence": "moderate",
        "source": "Seen on prproperties.org (central-flats page): asset CDN "
                   "on irp.cdn-website.com, meta 'dm:lcp-preload' tag pattern "
                   "consistent with Duda's rendering pipeline. Not "
                   "independently re-confirmed on a second site -- flag as "
                   "moderate confidence until cross-checked again.",
    },
    {
        "name": "WordPress",
        "category": "platform",
        "patterns": [
            "wp-content/",
            "wp-json/",
            "wp-includes/",
        ],
        "confidence": "high",
        "source": "Standard WordPress fingerprint (well-established, not "
                   "specific to today's tests). NOTE: WordPress is the "
                   "underlying engine -- if an agency-specific rule ALSO "
                   "fires (e.g. Jonah Digital), report the agency as the "
                   "builder and WordPress as the underlying CMS, not as "
                   "competing answers.",
    },
    {
        "name": "Poetic",
        "category": "platform",
        "patterns": [
            "poetic.io",
            "website by poetic",
        ],
        "confidence": "high",
        "source": "Confirmed on thejamesonhomewood.com: explicit footer "
                   "credit 'Website by Poetic' linking to poetic.io.",
    },
    {
        "name": "Webflow",
        "category": "platform",
        "patterns": [
            "website-files.com",
        ],
        "confidence": "high",
        "source": "Confirmed on thejamesonhomewood.com: all assets served "
                   "from cdn.prod.website-files.com, Webflow's own asset "
                   "CDN domain. Same pattern as WordPress -- this is the "
                   "underlying engine; report alongside an agency rule "
                   "(e.g. Poetic) if one also fires, not as a conflicting "
                   "answer.",
    },
    # ---------------------------------------------------------------
    # PMS rules
    # ---------------------------------------------------------------
    {
        "name": "AppFolio",
        "category": "pms",
        "patterns": [
            "cdn.appfoliowebsites.com",
            "powered-by-appfolio",
            "appfolio.com",
        ],
        "confidence": "high",
        "source": "Confirmed on prproperties.org/central-flats: explicit "
                   "'powered by AppFolio' badge image next to the resident "
                   "'Online Portal / Log In' link.",
    },
    {
        "name": "RealPage (via LOFT resident portal)",
        "category": "pms",
        "patterns": [
            "loftliving.com",
        ],
        "confidence": "high",
        "source": "Confirmed TWICE independently: ethosapartments.com "
                   "(-> ethosapartments.loftliving.com) and "
                   "parkplaceapartmentsclt.com "
                   "(-> parkplaceapartmentsmecklenburg.loftliving.com). "
                   "LOFT is RealPage's resident-experience platform "
                   "(replaced ActiveBuilding). Pattern: "
                   "<property-slug>.loftliving.com",
    },
    {
        "name": "RealPage (legacy / ActiveBuilding)",
        "category": "pms",
        "patterns": [
            "activebuilding.com",
        ],
        "confidence": "high",
        "source": "Confirmed on thejamesonhomewood.com: Resident Portal "
                   "links to thejamesonal.activebuilding.com. LOFT "
                   "explicitly 'replaces ActiveBuilding' per RealPage's "
                   "own product pages -- older/not-yet-migrated sites "
                   "still show this domain. Report as RealPage PMS either "
                   "way.",
    },
    {
        "name": "RealPage (online leasing)",
        "category": "pms",
        "patterns": [
            "onlineleasing.realpage.com",
        ],
        "confidence": "high",
        "source": "Confirmed on thejamesonhomewood.com: 'Lease Now' button "
                   "links to a numbered onlineleasing.realpage.com "
                   "subdomain. A third distinct RealPage domain pattern "
                   "(alongside loftliving.com and activebuilding.com) -- "
                   "RealPage clearly has several differently-branded "
                   "products that all indicate the same PMS vendor.",
    },
]


def check_hard_rules(html: str):
    """
    Run all hard rules against raw page HTML (or a combined string of
    HTML from multiple fetched pages -- homepage + residents page etc).

    Returns a dict: {"platform": [...matches...], "pms": [...matches...]}
    Each match is {"name", "confidence", "matched_pattern"}.
    Multiple platform or PMS matches CAN occur (e.g. RealPage as PMS via
    LOFT + RealPage LeaseStar as platform are two separate, valid matches
    in different categories) -- the caller decides how to reconcile /
    display multiple hits in the same category if that happens.
    """
    html_lower = html.lower()
    results = {"platform": [], "pms": []}

    for rule in HARD_RULES:
        for pattern in rule["patterns"]:
            if pattern.lower() in html_lower:
                results[rule["category"]].append({
                    "name": rule["name"],
                    "confidence": rule["confidence"],
                    "matched_pattern": pattern,
                })
                break  # one match per rule is enough, don't double-count

    return results
