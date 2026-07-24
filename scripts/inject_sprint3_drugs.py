path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

sprint3_generics = '''        "cemiplimab", "dostarlimab", "retifanlimab", "amivantamab", "mobocertinib", "tepotinib_hcl", "tufetimab",
        "futibatinib_tab", "infigratinib", "capmatinib_hbr", "selpercatinib_cap", "pralsetinib_cap", "sotorasib_tab",
        "adagrasib_tab", "erdafitinib_tab", "pemigatinib_tab", "tucatinib_tab", "neratinib_tab", "zanubrutinib_cap",
        "pirtobrutinib_tab", "venetoclax_tab", "elacestrant", "lasofoxifene", "relugolix_tab", "linzagolix", "opigolix",
        "dexmedetomidine_oromucosal", "lesinurad", "cenobamate_tab", "stiripentol_cap", "fenfluramine_sol",
        "ganaxolone", "zuranolone", "brexanolone", "esketamine_nasal", "ketamine_inj", "propofol_emulsion",
        "etomidate_inj", "dexmedetomidine_inj", "midazolam_syrup", "remimazolam", "methohexital", "thiopental",
        "vonoprazan_amoxicillin", "vonoprazan_clarithromycin", "tenofovir_alafenamide_hemifumarate", "maribavir_tab",
        "letermovir_inj", "ibrexafungerp_tab", "rezafungin_inj", "sulbactam_durlobactam_inj", "cefiderocol_inj",
        "lefamulin_tab", "plazomicin_inj", "fidaxomicin_tab", "bezlotoxumab_inj", "obeticholic_acid_tab",
        "tezepelumab", "dupilumab", "mepolizumab", "benralizumab", "reslizumab", "omalizumab", "trastuzumab_hyaluronidase",
        "rituximab_hyaluronidase", "daratumumab_hyaluronidase", "pertuzumab_trastuzumab", "casirivimab_imdevimab",
        "bamlanivimab_etesevimab", "sotrovimab", "tixagevimab_cilgavimab", "bebtelovimab", "regdanvimab",
        "acebutolol", "betaxolol", "carteolol", "penbutolol", "pindolol", "timolol", "labetalol_hcl", "carvedilol_phosphate",
        "felodipine_er", "isradipine", "nicardipine_sr", "nisoldipine_er", "nifedipine_cc", "clevidipine_inj", "nimodipine_cap",
        "diltiazem_cd", "verapamil_sr", "epoprostenol", "treprostinil", "iloprost", "selexipag", "macitentan", "ambrisentan",
        "bosentan", "riociguat", "vericiguat_tab", "nesiritide", "sacubitril_valsartan_50mg", "hydralazine_isosorbide",
        "chlorothiazide", "indapamide_sr", "metolazone_tab", "torsemide_inj", "bumetanide_inj", "ethacrynic_acid_tab",
        "triamterene", "amiloride", "spironolactone_100mg", "eplerenone_25mg", "finerenone_10mg", "finerenone_20mg",
        "aliskiren", "azilsartan_medoxomil", "candesartan_cilexetil", "eprosartan", "irbesartan", "losartan_potassium",
        "olmesartan_medoxomil", "telmisartan_micardis", "valsartan_diovan", "benazepril", "captopril", "enalaprilat",
        "fosinopril", "lisinopril_hydrochlorothiazide", "moexipril", "perindopril_erbumine", "quinapril", "ramipril_altace",
        "trandolapril", "guanfacine_er", "methyldopa", "moxonidine", "rilmenidine", "reserpine", "phenoxybenzamine",
        "phentolamine", "trimethaphan", "mecamylamine", "ivabradine_hcl", "ranolazine_er", "trimetazidine_mr",
        "perhexiline", "nicorandil_tab", "molsidomine", "nitroglycerin_patch", "isosorbide_dinitrate", "isosorbide_mononitrate_er",'''

sprint3_brands = '''        "tezspire": "tezepelumab", "kerendia": "finerenone", "jemperli": "dostarlimab", "rybrevant": "amivantamab",'''

marker_extras = 'sprint2_extras = [\n'
marker_brand_map = 'sprint2_brand_map = {\n'

if marker_extras in content:
    content = content.replace(marker_extras, marker_extras + sprint3_generics + '\n', 1)

if marker_brand_map in content:
    content = content.replace(marker_brand_map, marker_brand_map + sprint3_brands + '\n', 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Injected Sprint 3 generics and brand aliases into drug_resolver.py")
