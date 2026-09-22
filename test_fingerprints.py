"""
Quick validation: replay the exact signal strings we captured from each
live site tested today, and confirm the hard rules fire correctly.
This is NOT a live network test (sandboxed environment can't reach
arbitrary external sites) -- it's a regression check that the pattern
matching logic itself is correct, using real captured signal text.
"""

from fingerprints import check_hard_rules

# Each entry: (site tested today, real signal snippet captured, expected results)
test_cases = [
    (
        "ethosapartments.com",
        '<img src="https://g5-assets-cld-res.cloudinary.com/image/upload/.../g5-c-60my76eob-starwood-capital/...">'
        '<a href="https://ethosapartments.loftliving.com/">Resident Portal</a>',
        {"platform": ["G5"], "pms": ["RealPage (via LOFT resident portal)"]},
    ),
    (
        "prproperties.org/central-flats",
        '<img src="https://cdn.appfoliowebsites.com/sites/resources/images/powered-by-appfolio.png">'
        '<link href="https://irp.cdn-website.com/39cfdf92/dms3rep/multi/opt/logo.png">'
        '<meta name="dm:lcp-preload" content="dm:lcp-frozen">',
        {"platform": ["Duda"], "pms": ["AppFolio"]},
    ),
    (
        "treehausclemson.com",
        '<meta name="generator" content="Jonah Systems, LLC - www.jonahdigital.com">'
        '<a href="https://jonahdigital.com/">Jonah Digital Agency</a>',
        {"platform": ["Jonah Digital (Jonah Systems)"], "pms": []},
    ),
    (
        "ghpmgmt.com (Apartments247 customer)",
        '<img src="https://www.ghpmgmt.com/gridmedia/img/logo.png">'
        'Copyright &copy; 2000-2026 <a href="https://www.apartments247.com">Apartments247.com</a>'
        '<a href="https://files.apts247.com/files/common/disclaimer/index.html">Disclaimers</a>',
        {"platform": ["Apartments247"], "pms": []},
    ),
    (
        "mirageatsouthpoint.com (Entrata example)",
        '<img src="https://medialibrarycfo.entrata.com/17795/MLv3/9/36/.../logo.png">'
        '<img src="https://commoncf.entrata.com/images/loader_grey.gif">'
        "Entrata, Inc. is dedicated to ensuring digital accessibility",
        {"platform": ["Entrata"], "pms": ["Entrata (embedded widget)"]},
    ),
    (
        "parkplaceapartmentsclt.com",
        '<img src="https://capi.myleasestar.com/v2/dimg/178694114/400x400/178694114.png">'
        '<a href="https://www.realpage.com/apartment-marketing/">'
        '<a href="https://parkplaceapartmentsmecklenburg.loftliving.com/">Resident Portal</a>',
        {"platform": ["RealPage LeaseStar"], "pms": ["RealPage (via LOFT resident portal)"]},
    ),
    (
        "thejamesonhomewood.com",
        '<img src="https://cdn.prod.website-files.com/66f57e163e2379a61db650f2/logo.webp">'
        '<a href="https://9147849.onlineleasing.realpage.com/">Lease Now</a>'
        '<a href="https://thejamesonal.activebuilding.com/">Resident Portal</a>'
        '<a href="https://poetic.io/">Website by Poetic</a>',
        {"platform": ["Webflow", "Poetic"], "pms": ["RealPage (legacy / ActiveBuilding)", "RealPage (online leasing)"]},
    ),
    (
        "theweldondenton.com",
        '<meta name="generator" content="Jonah Systems, LLC - www.jonahdigital.com">'
        '<a href="https://theweldonapts.securecafenet.com/residentservices/the-weldon0/userlogin">Resident Portal</a>'
        'Website Design by RentCafe (&copy; 2026 Yardi Systems, Inc. All Rights Reserved.)',
        {"platform": ["Jonah Digital (Jonah Systems)"], "pms": ["Yardi (via RentCafe / SecureCafe)"]},
    ),
    (
        "garrettnorthpowers.com (Wix + Entrata widget)",
        '<script src="https://static.wixstatic.com/sites/somebundle.js"></script>'
        '<script src="https://static.entrata.com/leasing-widget.js"></script>',
        {"platform": ["Wix"], "pms": ["Entrata (embedded widget)"]},
    ),
    (
        "songbirdkirkwood.com (Repli/MultiHub + Entrata via prospectportal)",
        '<a href="https://songbird.prospectportal.com/Apartments/module/application_authentication/">Apply</a>'
        'Professionally Managed by Gallery Residential'
        'Powered by <img src="/multihub-logo.svg" alt="MultiHub">'
        'Website Design by <img src="/repli-logo.svg" alt="Repli">',
        {"platform": ["Repli (MultiHub)"], "pms": ["Entrata (embedded widget)"]},
    ),
    (
        "liverashaaudubon.com (LeaseLeads + WordPress, RPM Living managed)",
        '<link rel="stylesheet" href="/wp-content/themes/rasha/style.css">'
        '<div class="footer-credit">Powered by <img src="/leaseleads-logo.svg" alt="LeaseLeads"></div>',
        {"platform": ["WordPress", "LeaseLeads"], "pms": []},
    ),
    (
        "thegantrydc.com (FINE + Yardi/SecureCafe, Funnel chat widget)",
        '<!--This handcrafted digital experience brought to you by FINE: wearefine.com.-->'
        '<a href="https://gantry.securecafe.com/residentservices/login">Resident Portal</a>'
        '<script src="https://funnelleasing.com/widget.js"></script>',
        {"platform": ["FINE"], "pms": ["Yardi (via RentCafe / SecureCafe)"]},
    ),
    (
        "livebakerblock.com (Yardi as BOTH platform via REACH and PMS via SecureCafe)",
        '<script src="https://cdngeneralmvc.rentcafe.com/assets/askka.134342014730000000.js"></script>'
        '<a href="https://bakerblock.securecafenet.com/residentservices/login">Resident Portal</a>',
        {"platform": ["Yardi (REACH by RentCafe Websites)"], "pms": ["Yardi (via RentCafe / SecureCafe)"]},
    ),
    (
        "hollandresidential.com/co/denver/commons-park-west/ (Razz)",
        '<img src="https://images.myrazz.com/uc-image/rtCeEx2CwQBHGzZsq/-/format/png/commons_park_west.png">'
        '[Happily Made by Razz](https://www.razzinteractive.com/)',
        {"platform": ["Razz Interactive"], "pms": []},
    ),
    (
        "livebellehaven.com (RentVision)",
        'meta-author: RentVision '
        '[Website created by RentVision](https://www.rentvision.com/)',
        {"platform": ["RentVision"], "pms": []},
    ),
    (
        "themarkatlanta.com (JUMPEM + Entrata white-label subdomain)",
        'Powered By [Jumpem Web Design & Internet Marketing](https://www.jumpem.com/) '
        '<a href="https://entrata.themarkatlanta.com/Apartments/module/application_authentication/">Apply</a>',
        {"platform": ["JUMPEM"], "pms": ["Entrata (embedded widget)"]},
    ),
    (
        "livebh.com/apartments/sylvan-thirty-apartments/ (iExposure)",
        'Site Created by: [iExposure](https://iexposure.com) | Site hosted on [Satorix](https://satorix.com)',
        {"platform": ["Internet Exposure (iExposure)"], "pms": []},
    ),
    (
        "apartmentsspringtx.com (365 Connect)",
        '2026 - 365 Connect - All Rights Reserved '
        '[Powered by 365 Connect](https://www.365connect.com) '
        '<img src="//cdn.365residentservices.com/global/images/mstile-144x144.png">',
        {"platform": ["365 Connect"], "pms": []},
    ),
    (
        "thealdentownes.com (Resident360)",
        '[Website by Resident360](https://www.resident360.com/)',
        {"platform": ["Resident360"], "pms": []},
    ),
    (
        "lolaapartments.com (Spherexx)",
        '[Copyright 2024-2026 All Rights Reserved](https://www.spherexx.com/copyright/) '
        '<img src="https://sxxweb8cdn.cachefly.net/common/uploads/zrs2019/779/media/logo.png">'
        '[Spherexx](https://spherexx.com/)',
        {"platform": ["Spherexx"], "pms": []},
    ),
    (
        "westloveapts.com (Mixed Media Creations)",
        '[.mmc-logo](https://www.mixedmediacreations.com "Crafted By Mixed Media Creations - Lewisville, TX")',
        {"platform": ["Mixed Media Creations"], "pms": []},
    ),
    (
        "marketsquaretower.com (P11 Creative)",
        '[Site By P11](http://www.p11.com "Site by p11")',
        {"platform": ["P11 Creative"], "pms": []},
    ),
    (
        "parkvanness.com (Streetsense)",
        'Design by [STREETSENSE](http://www.streetsense.com/ "Design by Streetsense")',
        {"platform": ["Streetsense"], "pms": []},
    ),
    (
        "townarlington.com (Swifty)",
        '[Powered By Swifty](https://beswifty.com) '
        '<img src="https://swifty-media.s3.us-east-1.amazonaws.com/sites/20418/logo.png">',
        {"platform": ["Swifty"], "pms": []},
    ),
    (
        "adveniratlighthousepoint.com (Resident360 built it, but embeds an Entrata widget)",
        '<link rel="stylesheet" href="https://adveniratlighthousepoint.com/wp-content/themes/garden-east/style.css">'
        '<img src="https://medialibrarycf.entrata.com/some/floorplan.jpg">'
        '<a href="https://adveniratlighthousepoint.prospectportal.com/Apartments/module/application_authentication/">Apply</a>'
        '[Website by Resident360](https://www.resident360.com/)',
        {"platform": ["WordPress", "Entrata", "Resident360"], "pms": ["Entrata (embedded widget)"]},
    ),
]

all_passed = True
for site, html_snippet, expected in test_cases:
    result = check_hard_rules(html_snippet)
    got_platform = sorted([m["name"] for m in result["platform"]])
    got_pms = sorted([m["name"] for m in result["pms"]])
    exp_platform = sorted(expected["platform"])
    exp_pms = sorted(expected["pms"])

    passed = (got_platform == exp_platform) and (got_pms == exp_pms)
    all_passed = all_passed and passed

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {site}")
    print(f"        expected platform={exp_platform} pms={exp_pms}")
    print(f"        got      platform={got_platform} pms={got_pms}")
    print()

print("=" * 60)
print("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED")
