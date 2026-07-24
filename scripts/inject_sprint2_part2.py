path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

part2_generics = '''        "abiraterone", "enzalutamide", "apalutamide", "darolutamide", "bicalutamide", "flutamide", "nilutamide",
        "goserelin", "leuprolide", "triptorelin", "degarelix", "relugolix", "anastrozole", "letrozole", "exemestane",
        "tamoxifen", "fulvestrant", "toremifene", "megestrol", "medroxyprogesterone", "bexarotene", "tretinoin_retinoic",
        "arsenic_trioxide", "asparaginase", "pegaspargase", "calaspargase", "bleomycin", "dactinomycin", "mitomycin",
        "daunorubicin", "doxorubicin", "epirubicin", "idarubicin", "valrubicin", "mitoxantrone", "amrubicin",
        "cyclophosphamide", "ifosfamide", "melphalan", "chlorambucil", "busulfan", "thiotepa", "carmustine", "lomustine",
        "streptozocin", "dacarbazine", "temozolomide", "procarbazine", "altretamine", "carboplatin", "cisplatin",
        "oxaliplatin", "nedaplatin", "lobaplatin", "heptaplatin", "methotrexate_sodium", "pemetrexed", "pralatrexate",
        "fluorouracil", "capecitabine", "cytarabine", "gemcitabine", "azacitidine", "decitabine", "trifluridine_tipiracil",
        "mercaptopurine", "thioguanine", "fludarabine", "cladribine_inj", "clofarabine", "nelarabine", "pentostatin",
        "vinblastine", "vincristine", "vinorelbine", "vinflunine", "paclitaxel", "docetaxel", "cabazitaxel",
        "nab_paclitaxel", "ixabepilone", "eribulin", "trabectedin", "lurbinectedin", "irinotecan", "topotecan",
        "etoposide", "teniposide", "mitotane", "bortezomib", "carfilzomib", "ixazomib", "thalidomide", "lenalidomide",
        "pomalidomide", "belantamab", "elotuzumab", "daratumumab", "isatuximab", "brentuximab_vedotin", "sacituzumab_govitecan",
        "fam_trastuzumab_deruxtecan", "enfortumab_vedotin", "tisotumab_vedotin", "loncastuximab_tesirine", "mirvetuximab",
        "padcev", "trodelvy", "enhertu", "blrep", "elrexfio", "talvey", "columvi", "epkinly", "tecvayli", "breyanzi",
        "kymriah", "yescarta", "tecartus", "abecma", "carvykti", "furosemide_inj", "torsemide_tab", "bumetanide_tab",
        "ethacrynic_acid", "metolazone", "indapamide_tab", "chlorthalidone_tab", "spironolactone_25mg", "eplerenone_50mg",
        "sacubitril_valsartan_97_103mg", "dapagliflozin_10mg", "empagliflozin_10mg", "canagliflozin_100mg", "ertugliflozin_5mg",
        "sitagliptin_100mg", "linagliptin_5mg", "saxagliptin_5mg", "alogliptin_25mg", "teneligliptin_20mg", "vildagliptin_50mg",
        "gliclazide_80mg", "glimepiride_2mg", "glipizide_5mg", "glyburide_5mg", "pioglitazone_15mg", "metformin_500mg",
        "acarbose_50mg", "voglibose_0_2mg", "miglitol_50mg", "repaglinide_1mg", "nateglinide_60mg", "insulin_regular",
        "insulin_nph", "insulin_glargine", "insulin_detemir", "insulin_degludec", "insulin_lispro", "insulin_aspart",
        "insulin_glulisine", "pramlintide_pen", "exenatide_pen", "liraglutide_pen", "dulaglutide_pen", "semaglutide_pen",
        "tirzepatide_pen", "lixisenatide_pen",'''

marker_gen = 'GENERIC_NAMES = {\n'

if marker_gen in content:
    content = content.replace(marker_gen, marker_gen + part2_generics + '\n', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Injected Sprint 2 Part 2 generics into drug_resolver.py")
