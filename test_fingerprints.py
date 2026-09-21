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
        {"platform": ["Entrata"], "pms": []},
    ),
    (
        "parkplaceapartmentsclt.com",
        '<img src="https://capi.myleasestar.com/v2/dimg/178694114/400x400/178694114.png">'
        '<a href="https://www.realpage.com/apartment-marketing/">'
        '<a href="https://parkplaceapartmentsmecklenburg.loftliving.com/">Resident Portal</a>',
        {"platform": ["RealPage LeaseStar"], "pms": ["RealPage (via LOFT resident portal)"]},
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
