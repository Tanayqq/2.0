path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

sprint2_generics = '''        "ceftazidime", "ceftazidime_avibactam", "ceftolozane_tazobactam", "meropenem_vaborbactam", "imipenem_cilastatin_relebactam",
        "cefiderocol", "lefamulin", "plazomicin", "fidaxomicin", "bezlotoxumab", "maribavir", "letermovir", "ibrexafungerp",
        "rezafungin", "sulbactam_durlobactam", "aztreonam", "fosfomycin_trometamol", "secnidazole", "tinidazole", "nitazoxanide",
        "alpelisib", "abemaciclib", "palbociclib", "ribociclib", "olaparib", "rucaparib", "niraparib", "talazoparib",
        "encorafenib", "dabrafenib", "vemurafenib", "binimetinib", "trametinib", "cobimetinib", "selumetinib", "capmatinib",
        "tepotinib", "selpercatinib", "pralsetinib", "sotorasib", "adagrasib", "futibatinib", "erdafitinib", "pemigatinib",
        "tucatinib", "neratinib", "lapatinib", "zanubrutinib", "acalabrutinib", "ibrutinib", "pirtobrutinib", "venetoclax",
        "brexpiprazole", "cariprazine", "lumateperone", "pimavanserin", "iloperidone", "asenapine", "paliperidone",
        "risperidone_laic", "aripiprazole_lauroxil", "deutetrabenazine", "valbenazine", "tetrabenazine", "pitolisant",
        "solriamfetol", "armodafinil", "modafinil", "sodium_oxybate", "calcium_magnesium_potassium_sodium_oxybates",
        "rimegepant", "atogepant", "ubrogepant", "zavegepant", "eptinezumab", "galcanezumab", "fremanezumab", "erenumab",
        "voxilaprevir", "glecaprevir", "pibrentasvir", "sofosbuvir_velpatasvir", "ledipasvir", "daclatasvir", "elbasvir",
        "grazoprevir", "tenofovir_alafenamide", "entecavir_monohydrate", "tenofovir_disoproxil", "peginterferon_alfa_2a",
        "budesonide_mmx", "ozanimod_hcl", "etrasimod", "mirikizumab", "risankizumab_rzaa", "gustidukumab",
        "brentuximab", "polatuzumab", "loncastuximab", "tisotumab", "enfortumab", "sacituzumab", "trastuzumab_deruxtecan",
        "trastuzumab_emtansine", "fam_trastuzumab", "datopotamab", "patritumab", "tarlatamab", "teclistamab", "elranatamab",
        "talquetamab", "epcoritamab", "glofitamab", "axicabtagene", "tisagenlecleucel", "brexucabtagene", "idecabtagene",
        "ciltacabtagene", "lisocabtagene", "alglucosidase", "avaerglucosidase", "galsulfase", "idursulfase", "laronidase",
        "elosulfase", "sebelipase", "cerliponase", "pegunigalsidase", "olipudase", "velmanase", "asfotase", "pegvaliase",'''

sprint2_brands = '''        "avycaz": "ceftazidime_avibactam", "zerbaxa": "ceftolozane_tazobactam", "vabomere": "meropenem_vaborbactam",
        "recarbrio": "imipenem_cilastatin_relebactam", "fetroja": "cefiderocol", "xenleta": "lefamulin", "zemdri": "plazomicin",
        "dificid": "fidaxomicin", "zinplava": "bezlotoxumab", "livtencity": "maribavir", "prevymis": "letermovir",
        "brexafemme": "ibrexafungerp", "rezzayo": "rezafungin", "xacduro": "sulbactam_durlobactam", "piqray": "alpelisib",
        "verzenio": "abemaciclib", "ibrance": "palbociclib", "kisqali": "ribociclib", "lynparza": "olaparib", "rubraca": "rucaparib",
        "zejula": "niraparib", "talzenna": "talazoparib", "braftovi": "encorafenib", "tafinlar": "dabrafenib", "zelboraf": "vemurafenib",
        "mektovi": "binimetinib", "mekinist": "trametinib", "cotellic": "cobimetinib", "koselugo": "selumetinib", "tabrecta": "capmatinib",
        "tepmetko": "tepotinib", "retevmo": "selpercatinib", "gavreto": "pralsetinib", "lumakras": "sotorasib", "krazati": "adagrasib",
        "lytgobi": "futibatinib", "balversa": "erdafitinib", "pemazyre": "pemigatinib", "tukysa": "tucatinib", "nerlynx": "neratinib",
        "tykerb": "lapatinib", "brukinsa": "zanubrutinib", "calquence": "acalabrutinib", "imbruvica": "ibrutinib", "jaypirca": "pirtobrutinib",
        "venclexta": "venetoclax", "rexulti": "brexpiprazole", "vraylar": "cariprazine", "caplyta": "lumateperone", "nuplazid": "pimavanserin",
        "fanapt": "iloperidone", "saphris": "asenapine", "invega": "paliperidone", "austedo": "deutetrabenazine", "ingrezza": "valbenazine",
        "xenazine": "tetrabenazine", "wakix": "pitolisant", "sunosi": "solriamfetol", "provigil": "modafinil", "nuvigil": "armodafinil",
        "xyrem": "sodium_oxybate", "xywav": "calcium_magnesium_potassium_sodium_oxybates", "nurtec": "rimegepant", "qulipta": "atogepant",
        "ubrelvy": "ubrogepant", "zavzpret": "zavegepant", "vyepti": "eptinezumab", "emgality": "galcanezumab", "ajovy": "fremanezumab",
        "aimovig": "erenumab",'''

marker_gen = 'GENERIC_NAMES = {\n'
marker_brand = 'BRAND_TO_GENERIC: Dict[str, str] = {\n'

if marker_gen in content:
    content = content.replace(marker_gen, marker_gen + sprint2_generics + '\n', 1)

if marker_brand in content:
    content = content.replace(marker_brand, marker_brand + sprint2_brands + '\n', 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Injected Sprint 2 generics and brand aliases into drug_resolver.py")
