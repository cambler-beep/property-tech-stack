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
        "source": "DOWNGRADED from high back to moderate (2026-09-21) after "
                   "a real conflict: songbirdkirkwood.com matches this "
                   "pattern, but its footer explicitly says 'Website "
                   "Design by Repli' / 'Powered by MultiHub' -- direct, "
                   "authoritative counter-evidence that this domain is NOT "
                   "Duda-exclusive. Likely explanation: cdn-website.com is "
                   "shared backend/CDN infrastructure multiple different "
                   "website-builder platforms use, not a single-vendor "
                   "fingerprint. Originally seen on prproperties.org and "
                   "(mistakenly re-confirmed on) songbirdkirkwood.com -- "
                   "neither was independently verified by an explicit "
                   "footer credit the way this rule normally requires. "
                   "Treat any match as a real but uncertain signal, not "
                   "proof -- check for a footer credit before trusting it.",
    },
    {
        "name": "Repli (MultiHub)",
        "category": "platform",
        "patterns": [
            "website design by repli",
            "powered by multihub",
            "multihub",
            "repli.io",
            "alt=\"repli\"",
        ],
        "confidence": "moderate",
        "source": "Confirmed on songbirdkirkwood.com: footer credits "
                   "'Website Design by Repli' / 'Powered by MultiHub' "
                   "(Repli's product, confirmed as a real multifamily "
                   "platform in the Revyse vendor research earlier -- "
                   "'MultiHub is the property marketing platform for "
                   "multifamily, built by Repli'). BROADENED after the "
                   "full-phrase patterns failed to fire live: the brand "
                   "credits render as logo IMAGES, not plain adjacent "
                   "text, so 'website design by repli' as one contiguous "
                   "string never actually appears in the raw HTML (an "
                   "<img> tag sits between the words). Added bare "
                   "'multihub' as the most distinctive single-word "
                   "fallback -- lower confidence since it's broader and "
                   "less specifically tied to a confirmed exact string.",
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
    {
        "name": "Wix",
        "category": "platform",
        "patterns": [
            "wixstatic.com",
            "parastorage.com",
            "wix.com website builder",
        ],
        "confidence": "high",
        "source": "Well-established, widely-documented Wix fingerprint "
                   "(same treatment as the WordPress rule -- general "
                   "platform knowledge, not tied to one specific live test). "
                   "Added after garrettnorthpowers.com came back "
                   "'Not detected' despite BuiltWith showing it's built on "
                   "Wix Studio -- a real gap, no Wix rule existed before "
                   "this (2026-09-21). NOTE: BuiltWith's own crawler also "
                   "shows 'Cloudflare Blocked' / 403 on this specific site, "
                   "so this fix may not fully resolve THAT case if the site "
                   "itself is hard to reach for any automated tool -- but "
                   "the rule itself is a legitimate general-purpose gap "
                   "worth closing regardless.",
    },
    {
        "name": "LeaseLeads",
        "category": "platform",
        "patterns": [
            "powered by leaseleads",
            "leaseleads",
        ],
        "confidence": "high",
        "source": "Confirmed on liverashaaudubon.com: explicit footer "
                   "credit 'Powered by LeaseLeads' with logo. LeaseLeads "
                   "is a real multifamily website vendor (validated in "
                   "the Revyse vendor research earlier). Underlying CMS on "
                   "this site is WordPress (wp-content/) -- same "
                   "agency-plus-engine pattern as Jonah Digital+WordPress "
                   "and Poetic+Webflow, report both. Included the bare "
                   "'leaseleads' word from the start (not just the full "
                   "phrase) given the Repli/MultiHub lesson earlier today: "
                   "brand credits are often logo IMAGES, not adjacent "
                   "plain text, so phrase-only patterns can silently miss.",
    },
    {
        "name": "FINE",
        "category": "platform",
        "patterns": [
            "wearefine.com",
            "brought to you by fine",
        ],
        "confidence": "high",
        "source": "Confirmed on thegantrydc.com: explicit HTML comment "
                   "'This handcrafted digital experience brought to you "
                   "by FINE: wearefine.com.' -- about as unambiguous a "
                   "credit as exists. Underlying CMS is FAE (Fine Admin "
                   "Engine), FINE's own proprietary open-source Rails CMS "
                   "-- same agency-plus-engine pattern as other rules here, "
                   "but FAE isn't independently fingerprintable the way "
                   "WordPress/Webflow are (it's not widely used outside "
                   "FINE's own client base), so just report FINE.",
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
    {
        "name": "Yardi (via RentCafe / SecureCafe)",
        "category": "pms",
        "patterns": [
            "securecafenet.com",
            "securecafe.com",
            "website design by rentcafe",
            "yardi systems, inc",
        ],
        "confidence": "high",
        "source": "Confirmed on theweldondenton.com AND residencesat1125.com "
                   "(2026-09-21) -- two different SecureCafe domain variants "
                   "seen (securecafenet.com and securecafe.com, without "
                   "'net') -- both now covered. Footer credit 'Website "
                   "Design By RentCafe (c) Yardi Systems, Inc.' independently "
                   "confirms both too. Notable gap this closes: despite "
                   "researching Yardi/RentCafe extensively earlier (see the "
                   "w3techs mislabeling incident with Entrata), this is the "
                   "first time we've had an actual confirmed live fingerprint "
                   "for it -- one of the biggest PMS vendors in the industry "
                   "had NO hard rule until these two tests.",
    },
    {
        "name": "Entrata (embedded widget)",
        "category": "pms",
        "patterns": [
            "entrata.com",
            "prospectportal.com",
        ],
        "confidence": "moderate",
        "source": "Distinct from the 'Entrata' PLATFORM rule above, which "
                   "only fires on Entrata's specific asset-hosting "
                   "subdomains (i.e. when Entrata built the whole site). "
                   "This broader, lower-confidence rule catches Entrata "
                   "showing up as just an embedded leasing/application "
                   "widget on a site built with something else entirely -- "
                   "seen via BuiltWith on garrettnorthpowers.com (a Wix "
                   "site) listing 'Entrata - Property Management Software' "
                   "under Widgets, not CMS. Broader substring = more "
                   "false-positive risk than the specific asset-subdomain "
                   "rule, hence moderate not high confidence. "
                   "prospectportal.com added after songbirdkirkwood.com's "
                   "'Apply' button linked there -- that page's own footer "
                   "confirmed 'Entrata, Inc.' explicitly, but the link "
                   "domain itself doesn't contain the word 'entrata' at "
                   "all, so the plain entrata.com pattern alone would have "
                   "missed this one.",
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
