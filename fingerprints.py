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
        "confidence": "moderate",
        "source": "Confirmed on mirageatsouthpoint.com: entrata.com asset "
                   "subdomains + explicit 'Entrata, Inc.' footer copyright "
                   "and accessibility statement. (Note: w3techs had this "
                   "site mis-tagged as 'Yardi' -- likely stale data from "
                   "before a platform migration. Trust the live HTML over "
                   "third-party trackers.) DOWNGRADED from high to moderate "
                   "(2026-09-22) after adveniratlighthousepoint.com: this "
                   "site's actual builder is confirmed Resident360 "
                   "('Website by Resident360' explicit credit), but "
                   "medialibrarycf.entrata.com STILL appeared -- because "
                   "the site embeds an Entrata-powered floor-plan/media "
                   "widget, not because Entrata built the whole site. Same "
                   "lesson as Duda/Repli: an asset-domain match can mean "
                   "'this resource is embedded here' rather than 'this "
                   "vendor built the site' -- treat as real but uncertain "
                   "unless an explicit builder credit (like 'Entrata, "
                   "Inc.' copyright) is also present.",
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
        "source": "STATUS UPDATE (2026-09-22): this domain has now been "
                   "traced to Repli/MultiHub with certainty (see the Repli "
                   "rule above -- repli360.com's own corporate site uses "
                   "it, plus two independent customer confirmations). "
                   "Across all of today's testing, EVERY real sighting of "
                   "this domain has turned out to be Repli, and Duda was "
                   "never independently confirmed even once -- the "
                   "original attribution came from general training "
                   "knowledge, not a live-verified source. This rule is "
                   "kept only as a residual fallback for the rare case "
                   "where this domain appears with NO other Repli signal "
                   "present (the high-confidence Repli rule already covers "
                   "and will display instead whenever it also fires) -- "
                   "treat any surfaced 'Duda' result as genuinely "
                   "uncertain and worth a manual check, since it may well "
                   "just be an unconfirmed Repli account with no other "
                   "visible brand marker on that particular page.",
    },
    {
        "name": "Repli (MultiHub)",
        "category": "platform",
        "patterns": [
            "repli360.com",
            "irp.cdn-website.com",
            "website design by repli",
            "powered by multihub",
            "multihub",
            "repli.io",
            "alt=\"repli\"",
        ],
        "confidence": "high",
        "source": "UPGRADED from moderate to high (2026-09-22) after decisive "
                   "evidence: repli360.com is Repli's OWN corporate site, "
                   "and it uses irp.cdn-website.com for its own assets -- "
                   "confirming that domain is Repli/MultiHub's platform "
                   "infrastructure, not (as originally guessed, never "
                   "independently confirmed) Duda's. Also confirmed on "
                   "regencymp.com: explicit 'Powered by [repli logo]' "
                   "linking directly to repli360.com. That's THREE real "
                   "sites tying this domain to Repli (also "
                   "songbirdkirkwood.com originally) and ZERO confirmed "
                   "genuine Duda sightings across all of today's testing. "
                   "Added 'repli360.com' itself as the strongest pattern.",
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
        "name": "Squarespace",
        "category": "platform",
        "patterns": [
            "static1.squarespace.com",
            "squarespace-cdn.com",
            "squarespace.com/universal",
        ],
        "confidence": "high",
        "source": "Well-established, widely-documented Squarespace "
                   "fingerprint (same treatment as WordPress/Wix -- general "
                   "platform knowledge). Added from the ranked CRM list "
                   "(386 properties, 2026-09-21) -- not tied to one "
                   "specific live multifamily example, but the pattern "
                   "itself is extremely well-documented across the web at "
                   "large, so confidence stays high despite that.",
    },
    {
        "name": "Prismic",
        "category": "platform",
        "patterns": [
            "images.prismic.io",
            "prismic.io",
        ],
        "confidence": "high",
        "source": "Confirmed on amli.com/apartments/southeast-florida/"
                   "miami-apartments/amli-midtown-29: literally every "
                   "image on the page is served from images.prismic.io. "
                   "Same treatment as WordPress/Wix/Squarespace -- Prismic "
                   "is a real, specific headless-CMS product (not a bare "
                   "language/framework like Ruby on Rails, which doesn't "
                   "get a rule for exactly that reason), so it's an "
                   "identifiable platform fact worth reporting even though "
                   "it's not multifamily-specific. Typically the "
                   "underlying engine behind a custom-built (often "
                   "in-house, as with AMLI here) front-end, similar to how "
                   "WordPress pairs with an agency credit.",
    },
    {
        "name": "Optimizely",
        "category": "platform",
        "patterns": [
            "/globalassets/",
        ],
        "confidence": "high",
        "source": "Confirmed on villagegreenlancaster.com: the /globalassets/ "
                   "path is used throughout for every image asset -- a "
                   "well-documented, distinct Episerver/Optimizely CMS "
                   "signature (Optimizely was formerly known as Episerver). "
                   "Same treatment as Prismic -- a real, specific CMS "
                   "product, not multifamily-specific but an identifiable "
                   "platform fact.",
    },
    {
        "name": "Virtual Leasing Systems",
        "category": "platform",
        "patterns": [
            "virtualleasingsystems.com",
            "website provided by virtual leasing systems",
        ],
        "confidence": "high",
        "source": "Confirmed on carolinewestgray.com: explicit 'Website "
                   "provided by Virtual Leasing Systems' footer credit "
                   "linking to virtualleasingsystems.com.",
    },
    {
        "name": "Threshold Agency",
        "category": "platform",
        "patterns": [
            "thresholdagency.com",
            "powered by threshold",
        ],
        "confidence": "high",
        "source": "Confirmed on postchicago.com: explicit 'WEBSITE POWERED "
                   "BY THRESHOLD' footer credit linking to "
                   "thresholdagency.com.",
    },
    {
        "name": "Superpath",
        "category": "platform",
        "patterns": [
            "superpathliving.com",
            "marketing services powered by superpath",
        ],
        "confidence": "high",
        "source": "Confirmed on thereserveatclarkstownny.com: explicit "
                   "'Marketing services powered by Superpath' footer "
                   "credit linking to superpathliving.com.",
    },
    {
        "name": "Junex",
        "category": "platform",
        "patterns": [
            "powered by junex",
        ],
        "confidence": "high",
        "source": "Confirmed on renaissancevirginiabeach.com: explicit "
                   "'Powered by Junex.' footer text (plain text, no "
                   "hyperlinked domain found).",
    },
    {
        "name": "Highform",
        "category": "platform",
        "patterns": [
            "highform.com",
            "built by highform",
        ],
        "confidence": "high",
        "source": "Confirmed on village43.com: 'Site Credit -- Built by "
                   "Highform' footer credit linking to highform.com.",
    },
    {
        "name": "DB Marketing",
        "category": "platform",
        "patterns": [
            "dbmarketingltd.com",
        ],
        "confidence": "high",
        "source": "Confirmed on 17walnut.com: footer logo image labeled "
                   "'DB Marketing' linking directly to dbmarketingltd.com.",
    },
    {
        "name": "Uncomn Projects",
        "category": "platform",
        "patterns": [
            "uncomn-projects.com",
        ],
        "confidence": "high",
        "source": "Confirmed on westcottliving.com: footer logo image "
                   "labeled 'Uncomn Projects' linking to "
                   "uncomn-projects.com.",
    },
    {
        "name": "People People",
        "category": "platform",
        "patterns": [
            "people-people.com",
            "web by people people",
        ],
        "confidence": "high",
        "source": "Confirmed on thecolina.com: explicit 'Web by People "
                   "People.' footer credit linking to people-people.com.",
    },
    {
        "name": "DEI Creative",
        "category": "platform",
        "patterns": [
            "deicreative.com",
            "website by dei creative",
        ],
        "confidence": "high",
        "source": "Confirmed on cobbapartments.com: explicit 'Website by "
                   "DEI Creative' footer credit linking to deicreative.com, "
                   "also independently confirmed via the page's own "
                   "meta-author tag ('DEI Creative in Seattle, WA'). NOTE: "
                   "this was given to us as 'Del Creative' -- the real "
                   "name is DEI Creative; likely a misread of the name.",
    },
    {
        "name": "Social Fire Media",
        "category": "platform",
        "patterns": [
            "socialfiremedia.com",
            "designed by social fire media",
        ],
        "confidence": "high",
        "source": "Confirmed on crystalwoodsapts.com: explicit 'Designed by "
                   "Social Fire Media' footer credit linking to "
                   "socialfiremedia.com.",
    },
    {
        "name": "UpShift Creative",
        "category": "platform",
        "patterns": [
            "upshiftcreative.com",
        ],
        "confidence": "high",
        "source": "Confirmed on nevele22.com: 'Site Design' footer link "
                   "goes directly to upshiftcreative.com.",
    },
    {
        "name": "Dulce Design",
        "category": "platform",
        "patterns": [
            "dulcedesign.com",
            "web design by dulce design",
        ],
        "confidence": "high",
        "source": "Confirmed on hearthonbroad.com: explicit 'Web design by "
                   "Dulce Design Co.' footer credit linking to "
                   "dulcedesign.com.",
    },
    {
        "name": "BT Creative",
        "category": "platform",
        "patterns": [
            "designed by bt creative",
        ],
        "confidence": "high",
        "source": "Confirmed on bellevue10.com: explicit 'DESIGNED BY BT "
                   "CREATIVE' footer text (plain text, no hyperlinked "
                   "domain found).",
    },
    {
        "name": "Paradigm Marketing & Creative",
        "category": "platform",
        "patterns": [
            "2dimes.com",
            "site by paradigm marketing",
        ],
        "confidence": "high",
        "source": "Confirmed on the-provost.com: explicit 'Site by "
                   "Paradigm Marketing & Creative' footer credit -- but "
                   "the real linked domain is 2dimes.com, not a "
                   "paradigm-branded domain (another name/domain "
                   "mismatch, same pattern as Resite/thinkresite).",
    },
    {
        "name": "Tenderling",
        "category": "platform",
        "patterns": [
            "tenderling.com",
            "site by tenderling",
        ],
        "confidence": "high",
        "source": "Confirmed on theavenuehollywood.com: explicit 'Site By "
                   "Tenderling' footer credit linking to tenderling.com. "
                   "(Greystar-managed property, using an outside agency -- "
                   "consistent with Greystar Creative Services being the "
                   "in-house team for some properties and outside "
                   "agencies like this being used for others.)",
    },
    {
        "name": "Studio Fabric",
        "category": "platform",
        "patterns": [
            "studiofabric.com",
            "site by fabric",
        ],
        "confidence": "high",
        "source": "Confirmed on circala.com: explicit 'Site By Fabric' "
                   "footer credit linking to studiofabric.com.",
    },
    {
        "name": "Prismatic",
        "category": "platform",
        "patterns": [
            "helloprismatic.com",
            "branding + website by prismatic",
        ],
        "confidence": "high",
        "source": "Confirmed on theyardivanhoe.com: explicit 'Branding + "
                   "Website by PRISMATIC.' footer credit linking to "
                   "helloprismatic.com. NOTE: distinct company from "
                   "'Prismic' (the headless CMS, prismic.io) despite the "
                   "near-identical name -- do not conflate the two.",
    },
    {
        "name": "Green Stick Marketing",
        "category": "platform",
        "patterns": [
            "greenstick.io",
            "site created by greenstick",
        ],
        "confidence": "high",
        "source": "Confirmed on fifteen51.com: explicit 'Site Created by "
                   "GREENstick' footer credit linking to greenstick.io, "
                   "independently confirmed by the page's own "
                   "accessibility-statement contact email "
                   "(kmill@greenstick.io). Live brand is shown as "
                   "'GREENstick' (one word); CSV name is 'Green Stick "
                   "Marketing'.",
    },
    {
        "name": "Razz Interactive",
        "category": "platform",
        "patterns": [
            "images.myrazz.com",
            "happily made by razz",
            "razzinteractive.com",
        ],
        "confidence": "high",
        "source": "Confirmed on hollandresidential.com/co/denver/commons-park-west/: "
                   "footer credit 'Happily Made by Razz' linking to "
                   "razzinteractive.com, plus every property image served "
                   "from images.myrazz.com. Razz is the brand within "
                   "Inhabit that powers ResMan Websites (confirmed via "
                   "ResMan's own materials) -- #1 on the ranked CRM list "
                   "by property count (1,269) that wasn't yet covered.",
    },
    {
        "name": "RentVision",
        "category": "platform",
        "patterns": [
            "rentvision.com",
            "website created by rentvision",
        ],
        "confidence": "high",
        "source": "Confirmed on livebellehaven.com: meta-author is "
                   "'RentVision', explicit 'Website created by RentVision' "
                   "footer link, 'Admin Login' points to my.rentvision.com, "
                   "and even the logo image filename is literally "
                   "'websitePoweredByRentVision.png'. Four independent "
                   "confirmations on one page.",
    },
    {
        "name": "JUMPEM",
        "category": "platform",
        "patterns": [
            "jumpem.com",
            "powered by jumpem",
        ],
        "confidence": "high",
        "source": "Confirmed on themarkatlanta.com: 'Powered By Jumpem Web "
                   "Design & Internet Marketing' footer credit linking to "
                   "jumpem.com. Underlying CMS is WordPress -- same "
                   "agency-plus-engine pattern as other agency rules.",
    },
    {
        "name": "Internet Exposure (iExposure)",
        "category": "platform",
        "patterns": [
            "iexposure.com",
            "site created by: iexposure",
        ],
        "confidence": "high",
        "source": "Confirmed on livebh.com/apartments/sylvan-thirty-apartments/: "
                   "explicit footer credit 'Site Created by: iExposure | "
                   "Site hosted on Satorix'. Another CSV-name-vs-live-brand "
                   "mismatch -- CRM tracks this vendor as 'Internet "
                   "Exposure', live branding is 'iExposure'. Underlying CMS "
                   "is WordPress.",
    },
    {
        "name": "365 Connect",
        "category": "platform",
        "patterns": [
            "365connect.com",
            "365residentservices.com",
            "powered by 365 connect",
        ],
        "confidence": "high",
        "source": "Confirmed on apartmentsspringtx.com: explicit '365 "
                   "Connect - All Rights Reserved' footer text, 'Powered "
                   "by 365 Connect' badge linking to 365connect.com, and "
                   "assets served from the distinctive "
                   "365residentservices.com domain.",
    },
    {
        "name": "Resident360",
        "category": "platform",
        "patterns": [
            "resident360.com",
            "website by resident360",
        ],
        "confidence": "high",
        "source": "Confirmed on thealdentownes.com: explicit 'Website by "
                   "Resident360' footer link to resident360.com, on top of "
                   "WordPress. NOTE: a second example given for this "
                   "vendor (adveniratlighthousepoint.com) was not yet "
                   "independently checked -- worth confirming this pattern "
                   "holds there too if it comes up.",
    },
    {
        "name": "Spherexx",
        "category": "platform",
        "patterns": [
            "spherexx.com",
            "sxxweb8cdn",
        ],
        "confidence": "high",
        "source": "Confirmed independently on TWO sites: lolaapartments.com "
                   "and live33west.com -- both have a footer copyright "
                   "link to spherexx.com/copyright/, an explicit "
                   "'Spherexx' logo link, and assets served from "
                   "sxxweb8cdn.cachefly.net (sxx = Spherexx abbreviated).",
    },
    {
        "name": "Mixed Media Creations",
        "category": "platform",
        "patterns": [
            "mixedmediacreations.com",
            "crafted by mixed media creations",
        ],
        "confidence": "high",
        "source": "Confirmed on westloveapts.com: footer link title text "
                   "'Crafted By Mixed Media Creations - Lewisville, TX' "
                   "linking to mixedmediacreations.com, on top of "
                   "WordPress.",
    },
    {
        "name": "P11 Creative",
        "category": "platform",
        "patterns": [
            "p11.com",
            "site by p11",
        ],
        "confidence": "high",
        "source": "Confirmed on marketsquaretower.com: explicit 'Site By "
                   "P11' footer credit linking to p11.com, on top of "
                   "WordPress. NOTE: a second example given for this "
                   "vendor (royceirvine.com) was not yet independently "
                   "checked.",
    },
    {
        "name": "Streetsense",
        "category": "platform",
        "patterns": [
            "streetsense.com",
            "design by streetsense",
        ],
        "confidence": "high",
        "source": "Confirmed on parkvanness.com: explicit 'Design by "
                   "STREETSENSE' footer credit linking to streetsense.com.",
    },
    {
        "name": "Market Apartments",
        "category": "platform",
        "patterns": [
            "marketapts.com",
            "apartment marketing by marketapts",
        ],
        "confidence": "high",
        "source": "Confirmed on park67glendale.com: explicit '[Apartment "
                   "Marketing by MarketApts.com]' footer credit, plus every "
                   "image asset served from assets.marketapts.com. Also "
                   "independently confirmed as a genuine agency (not a "
                   "management company) via marketapts.com's own site: "
                   "'get your website live in under 24 hours' template "
                   "service.",
    },
    {
        "name": "Agency FIFTY3",
        "category": "platform",
        "patterns": [
            "agencyfifty3.com",
            "designed by agency fifty3",
            "design by agencyfifty3",
        ],
        "confidence": "high",
        "source": "Confirmed independently on TWO sites: "
                   "editiononoberlin.com ('WEBSITE DESIGNED BY AGENCY "
                   "FIFTY3') and banyanflatsapts.com ('DESIGN BY "
                   "AGENCYFIFTY3'), both linking to agencyfifty3.com.",
    },
    {
        "name": "Resite",
        "category": "platform",
        "patterns": [
            "thinkresite.com",
            "powered by resite",
            "resiteimages",
        ],
        "confidence": "high",
        "source": "Confirmed on uptonoxmoor.com: explicit 'Powered by "
                   "Resite' footer credit -- but note the real domain is "
                   "thinkresite.com, NOT resite.com (another CSV-name-vs-"
                   "live-brand mismatch). Also assets served from a "
                   "distinctive resiteimages...digitaloceanspaces.com CDN.",
    },
    {
        "name": "Brindle Digital Marketing",
        "category": "platform",
        "patterns": [
            "brindledigital.com",
        ],
        "confidence": "high",
        "source": "Confirmed on 202park.com: footer logo (brindle-icons.svg) "
                   "links directly to brindledigital.com. Real domain is "
                   "brindledigital.com, not brindledigitalmarketing.com as "
                   "the CSV name might suggest.",
    },
    {
        "name": "Rentsync",
        "category": "platform",
        "patterns": [
            "rentsync.com",
            "designed and developed by rentsync",
        ],
        "confidence": "high",
        "source": "Confirmed on kelsongroup.com/residential/panorama-crossing: "
                   "explicit 'Designed and Developed by Rentsync' footer "
                   "credit linking to rentsync.com, plus logo hosted on "
                   "rentsync.s3.amazonaws.com. Canadian multifamily "
                   "property management sites (Kelson Group, Fitzrovia).",
    },
    {
        "name": "BetterNOI",
        "category": "platform",
        "patterns": [
            "betternoi.com",
            "bettercmspro.com",
            "betternoi, llc",
        ],
        "confidence": "high",
        "source": "Confirmed on theoaksapts.com/en/: explicit 'Copyright "
                   "(c) 2020-2026 BetterNOI, LLC' footer text, internal "
                   "links to the bettercmspro.com subdomain (their CMS "
                   "product, 'BetterCMS Pro'), and scripts hosted on "
                   "betternoi.com (analytics.betternoi.com, "
                   "ares.betternoi.com).",
    },
    {
        "name": "Swifty",
        "category": "platform",
        "patterns": [
            "beswifty.com",
            "powered by swifty",
            "swifty-media.s3",
        ],
        "confidence": "high",
        "source": "Confirmed on townarlington.com: explicit 'Powered By "
                   "Swifty' footer credit linking to beswifty.com, plus "
                   "assets served from swifty-media.s3.us-east-1.amazonaws.com "
                   "and a WordPress plugin path 'swifty-frontend'. CSV name "
                   "('Swifty') matches the live brand exactly, unlike most "
                   "other vendors today -- no alias needed.",
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
        "name": "Yardi (REACH by RentCafe Websites)",
        "category": "platform",
        "patterns": [
            "cdngeneralmvc.rentcafe.com",
        ],
        "confidence": "high",
        "source": "Confirmed on livebakerblock.com: CSS/JS assets served "
                   "from cdngeneralmvc.rentcafe.com. Same 'one vendor, two "
                   "product roles' pattern as RealPage (LOFT for PMS + "
                   "LeaseStar for the website itself, confirmed earlier on "
                   "parkplaceapartmentsclt.com) -- Yardi's RentCafe brand "
                   "covers both the resident/PMS side (SecureCafe login, "
                   "already a separate PMS rule) AND their own website "
                   "product, 'REACH by RentCafe Websites' (a real, "
                   "Revyse-validated vendor from the earlier research). "
                   "Report both when both fire, same as RealPage -- not "
                   "competing answers, two real facts about the same "
                   "parent company.",
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
            "entrata.",
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
                   "missed this one. Bare 'entrata.' (trailing dot) added "
                   "after themarkatlanta.com's Apply link used a "
                   "white-labeled subdomain -- entrata.themarkatlanta.com "
                   "-- which contains neither entrata.com nor "
                   "prospectportal.com as a substring.",
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


def filter_to_highest_confidence(matches: list) -> list:
    """
    For DISPLAY purposes only: if any match in this category is "high"
    confidence, drop any "moderate" confidence matches alongside it.

    Why: "moderate" confidence exists specifically to flag patterns that
    are sometimes misleading (e.g. the Entrata platform rule can fire from
    just an embedded floor-plan widget, not because Entrata built the
    site -- see adveniratlighthousepoint.com, 2026-09-22). When a
    high-confidence result already answers the question, showing a
    known-sometimes-wrong moderate result alongside it is noise, not
    information -- it makes a clean, correct answer (e.g. "Resident360")
    look like an ambiguous 3-way tie with WordPress and Entrata.

    This does NOT affect whether AI fallback runs (see needs_platform /
    needs_pms in app.py) -- those should still be based on whether ANY
    match exists, high or moderate. This filter is purely about what
    gets shown once we already have real information.
    """
    if any(m["confidence"] == "high" for m in matches):
        return [m for m in matches if m["confidence"] == "high"]
    return matches
