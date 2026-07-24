path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

sprint1_generics = '''        "azilsartan", "eplerenone", "sacubitril", "ivabradine", "ranolazine", "prasugrel", "ticagrelor",
        "bivalirudin", "argatroban", "milrinone", "dobutamine", "dopamine", "epinephrine", "isoproterenol",
        "nicardipine", "clevidipine", "labetalol", "esmolol", "fenoldopam", "prazosin", "terazosin", "doxazosin",
        "meropenem", "ertapenem", "doripenem", "imipenem", "cefepime", "ceftaroline", "ceftolozane", "avibactam",
        "tazobactam", "sulbactam", "colistin", "polymyxin_b", "tigecycline", "eravacycline", "omadacycline",
        "daptomycin", "linezolid", "tedizolid", "dalbavancin", "oritavancin", "isavuconazole", "posaconazole",
        "tirzepatide", "liraglutide", "dulaglutide", "exenatide", "lixisenatide", "pramlintide", "canagliflozin",
        "ertugliflozin", "sitagliptin", "saxagliptin", "linagliptin", "alogliptin", "pioglitazone", "rosiglitazone",
        "indacaterol", "vilanterol", "olodaterol", "umeclidinium", "glycopyrrolate", "aclidinium", "ciclesonide",
        "mometasone", "fluticasone", "budesonide", "beclomethasone", "montelukast", "zafirlukast", "zileuton",
        "dexlansoprazole", "rabeprazole", "ilaprazole", "vonoprazan", "sucralfate", "misoprostol", "linaclotide",
        "lubiprostone", "plecanatide", "eluxadoline", "aprepitant", "fosaprepitant", "palonosetron", "granisetron",
        "pembrolizumab", "nivolumab", "atezolizumab", "durvalumab", "ipilimumab", "rituximab", "trastuzumab",
        "bevacizumab", "cetuximab", "panitumumab", "imatinib", "dasatinib", "nilotinib", "bosutinib", "ponatinib",
        "propofol", "dexmedetomidine", "midazolam", "lorazepam", "ketamine", "etomidate", "cisatracurium",
        "rocuronium", "vecuronium", "sugammadex", "levetiracetam", "lacosamide", "brivaracetam", "perampanel",
        "sacubitril_valsartan", "finasteride", "dutasteride", "silodosin", "alfuzosin", "mirabegron", "oxybutynin",
        "solifenacin", "darifenacin", "tolterodine", "fesoterodine", "bethanechol", "pyridostigmine", "neostigmine",
        "donepezil", "rivastigmine", "galantamine", "memantine", "riluzole", "edaravone", "nusinersen", "risdiplam",
        "patisiran", "vutrisiran", "inotersen", "valproate", "divalproex", "carbamazepine", "oxcarbazepine",
        "eslicarbazepine", "lamotrigine", "topiramate", "zonisamide", "felbamate", "tiagabine", "vigabatrin",
        "clobazam", "rufinamide", "cannabidiol", "cenobamate", "fenfluramine", "stiripentol", "ethosuximide",
        "methsuximide", "phenobarbital", "primidone", "phenytoin", "fosphenytoin", "fosphenytoin_sodium",
        "gabapentin_enacarbil", "pregabalin_er", "duloxetine_dr", "venlafaxine_xr", "desvenlafaxine", "levomilnacipran",
        "milnacipran", "vilazodone", "vortioxetine", "vortioxetine_hbr", "selegiline", "rasagiline", "safinamide",
        "apremilast", "tofacitinib", "baricitinib", "upadacitinib", "filgotinib", "abrocitinib", "deucravacitinib",
        "secukinumab", "ixekizumab", "brodalumab", "guselkumab", "tildrakizumab", "risankizumab", "ustekinumab",
        "vedolizumab", "natalizumab", "ozanimod", "ponesimod", "siponimod", "fingolimod", "alemtuzumab",
        "ocrelizumab", "ofatumumab", "ublituximab", "cladribine", "tramadol", "tapentadol", "hydromorphone", "oxymorphone", "buprenorphine",'''

sprint1_brands = '''        "edarbi": "azilsartan", "inspra": "eplerenone", "corlanor": "ivabradine", "ranexa": "ranolazine",
        "effient": "prasugrel", "brilinta": "ticagrelor", "angiomax": "bivalirudin", "primacor": "milrinone",
        "cardene": "nicardipine", "cleviprex": "clevidipine", "trandate": "labetalol", "brevibloc": "esmolol",
        "minipress": "prazosin", "hytrin": "terazosin", "cardura": "doxazosin", "merrem": "meropenem", "invanz": "ertapenem",
        "primaxin": "imipenem", "maxipime": "cefepime", "teflaro": "ceftaroline", "zerbaxa": "ceftolozane", "avycaz": "avibactam",
        "coly-mycin": "colistin", "tygacil": "tigecycline", "cubicin": "daptomycin", "zyvox": "linezolid", "sivextro": "tedizolid",
        "dalvance": "dalbavancin", "cresemba": "isavuconazole", "nofil": "posaconazole", "meronem": "meropenem", "cifran": "ciprofloxacin",
        "oflox": "ofloxacin", "zenflox": "ofloxacin", "mahacef": "cefixime", "ceftas": "cefixime", "taxim": "cefotaxime",
        "taxim-o": "cefixime", "zipod": "cefpodoxime", "goodcef": "cefpodoxime", "macrowin": "azithromycin", "aziwok": "azithromycin",
        "zocon": "fluconazole", "forcan": "fluconazole", "canditral": "itraconazole", "ityza": "itraconazole", "mounjaro": "tirzepatide",
        "zepbound": "tirzepatide", "victoza": "liraglutide", "saxenda": "liraglutide", "trulicity": "dulaglutide", "byetta": "exenatide",
        "invokana": "canagliflozin", "steglatro": "ertugliflozin", "januvia": "sitagliptin", "onglyza": "saxagliptin", "tradjenta": "linagliptin",
        "nesina": "alogliptin", "actos": "pioglitazone", "avandia": "rosiglitazone", "prio": "pioglitazone", "pioz": "pioglitazone",
        "arcapta": "indacaterol", "anoro": "umeclidinium", "seebri": "glycopyrrolate", "tudorza": "aclidinium", "alvesco": "ciclesonide",
        "asmanex": "mometasone", "flovent": "fluticasone", "pulmicort": "budesonide", "singulair": "montelukast", "aciphex": "dexlansoprazole",
        "aciphex-ez": "rabeprazole", "prazocid": "rabeprazole", "pariet": "rabeprazole", "carafate": "sucralfate", "cytotec": "misoprostol",
        "linzess": "linaclotide", "emend": "aprepitant", "aloxi": "palonosetron", "kytril": "granisetron", "keytruda": "pembrolizumab",
        "opdivo": "nivolumab", "tecentriq": "atezolizumab", "imfinzi": "durvalumab", "yervoy": "ipilimumab", "mabthera": "rituximab",
        "herceptin": "trastuzumab", "avastin": "bevacizumab", "erbitux": "cetuximab", "gleevec": "imatinib", "sprycel": "dasatinib",
        "tasigna": "nilotinib", "diprivan": "propofol", "precedex": "dexmedetomidine", "ativan": "lorazepam", "ketalar": "ketamine",
        "nimbex": "cisatracurium", "zemuron": "rocuronium", "bridion": "sugammadex", "keppra": "levetiracetam", "vimpat": "lacosamide",
        "otezla": "apremilast", "xeljanz": "tofacitinib", "olumiant": "baricitinib", "rinvoq": "upadacitinib", "jyseleca": "filgotinib",
        "cibinqo": "abrocitinib", "sotyktu": "deucravacitinib", "cosentyx": "secukinumab", "taltz": "ixekizumab", "siliq": "brodalumab",
        "tremfya": "guselkumab", "ilumya": "tildrakizumab", "skyrizi": "risankizumab", "stelara": "ustekinumab", "entyvio": "vedolizumab",
        "tysabri": "natalizumab", "zeposia": "ozanimod", "ponvory": "ponesimod", "mayzent": "siponimod", "gilenya": "fingolimod",
        "lemtrada": "alemtuzumab", "ocrevus": "ocrelizumab", "kesimpta": "ofatumumab", "briumvi": "ublituximab", "mavenclad": "cladribine",'''

marker_gen = 'GENERIC_NAMES = {\n'
marker_brand = 'BRAND_TO_GENERIC: Dict[str, str] = {\n'

if marker_gen in content:
    content = content.replace(marker_gen, marker_gen + sprint1_generics + '\n', 1)

if marker_brand in content:
    content = content.replace(marker_brand, marker_brand + sprint1_brands + '\n', 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Injected Sprint 1 generics and brand aliases into drug_resolver.py")
