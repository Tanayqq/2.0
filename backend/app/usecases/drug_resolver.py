from typing import Optional, Dict

class DrugNameResolver:
    """
    Resolves brand names and alternative phrasings to canonical generic names
    for the 105 drugs supported by MedRef.
    """
    
    BRAND_TO_GENERIC: Dict[str, str] = {
        # Core Brand to Generic Mappings
        "prinivil": "lisinopril",
        "zestril": "lisinopril",
        "lipitor": "atorvastatin",
        "glucophage": "metformin",
        "fortamet": "metformin",
        "glumetza": "metformin",
        "amoxil": "amoxicillin",
        "novamox": "amoxicillin",
        "advil": "ibuprofen",
        "motrin": "ibuprofen",
        "cozaar": "losartan",
        "coumadin": "warfarin",
        "jantoven": "warfarin",
        "ventolin": "albuterol",
        "proair": "albuterol",
        "proventil": "albuterol",
        "norvasc": "amlodipine",
        "synthroid": "levothyroxine",
        "levoxyl": "levothyroxine",
        "unithroid": "levothyroxine",
        "neurontin": "gabapentin",
        "prilosec": "omeprazole",
        "lopressor": "metoprolol",
        "toprol": "metoprolol",
        "microzide": "hydrochlorothiazide",
        "zocor": "simvastatin",
        "zoloft": "sertraline",
        "singulair": "montelukast",
        "lexapro": "escitalopram",
        "tylenol": "acetaminophen",
        "lasix": "furosemide",
        "flonase": "fluticasone",
        "flovent": "fluticasone",
        "wellbutrin": "bupropion",
        "zyban": "bupropion",
        "cymbalta": "duloxetine",
        "protonix": "pantoprazole",
        "deltasone": "prednisone",
        "crestor": "rosuvastatin",
        "flomax": "tamsulosin",
        "celexa": "citalopram",
        "mobic": "meloxicam",
        "zyloprim": "allopurinol",
        "aloprim": "allopurinol",
        "xanax": "alprazolam",
        "klonopin": "clonazepam",
        "valium": "diazepam",
        "ativan": "lorazepam",
        "ambien": "zolpidem",
        "coreg": "carvedilol",
        "aldactone": "spironolactone",
        "vasotec": "enalapril",
        "altace": "ramipril",
        "diovan": "valsartan",
        "tenormin": "atenolol",
        "inderal": "propranolol",
        "apresoline": "hydralazine",
        "catapres": "clonidine",
        "pravachol": "pravastatin",
        "mevacor": "lovastatin",
        "tricor": "fenofibrate",
        "antara": "fenofibrate",
        "lopid": "gemfibrozil",
        "zetia": "ezetimibe",
        "colcrys": "colchicine",
        "mitigare": "colchicine",
        "rheumatrex": "methotrexate",
        "trexall": "methotrexate",
        "plaquenil": "hydroxychloroquine",
        "imuran": "azathioprine",
        "neoral": "cyclosporine",
        "sandimmune": "cyclosporine",
        "gengraf": "cyclosporine",
        "prograf": "tacrolimus",
        "millipred": "prednisolone",
        "orapred": "prednisolone",
        "decadron": "dexamethasone",
        "medrol": "methylprednisolone",
        "pulmicort": "budesonide",
        "rhinocort": "budesonide",
        "foradil": "formoterol",
        "serevent": "salmeterol",
        "spiriva": "tiotropium",
        "atrovent": "ipratropium",
        "zyrtec": "cetirizine",
        "claritin": "loratadine",
        "allegra": "fexofenadine",
        "benadryl": "diphenhydramine",
        "vistaril": "hydroxyzine",
        "atarax": "hydroxyzine",
        "phenergan": "promethazine",
        "zofran": "ondansetron",
        "reglan": "metoclopramide",
        "imodium": "loperamide",
        "pepcid": "famotidine",
        "tagamet": "cimetidine",
        "nexium": "esomeprazole",
        "prevacid": "lansoprazole",
        "aciphex": "rabeprazole",
        "cytotec": "misoprostol",
        "azulfidine": "sulfasalazine",
        "lialda": "mesalamine",
        "asacol": "mesalamine",
        "pentasa": "mesalamine",
        "zithromax": "azithromycin",
        "biaxin": "clarithromycin",
        "erythrocin": "erythromycin",
        "vibramycin": "doxycycline",
        "doryx": "doxycycline",
        "minocin": "minocycline",
        "solodyn": "minocycline",
        "sumycin": "tetracycline",
        "keflex": "cephalexin",
        "omnicef": "cefdinir",
        "ceftin": "cefuroxime",
        "cipro": "ciprofloxacin",
        "levaquin": "levofloxacin",
        "avelox": "moxifloxacin",
        "flagyl": "metronidazole",
        "cleocin": "clindamycin",
        "zyvox": "linezolid",
        "vancocin": "vancomycin",
        "macrobid": "nitrofurantoin",
        "macrodantin": "nitrofurantoin",
        "primsol": "trimethoprim",
        "diflucan": "fluconazole",
        "nizoral": "ketoconazole",
        "sporanox": "itraconazole",
        "lamisil": "terbinafine",
        "zovirax": "acyclovir",
        "valtrex": "valacyclovir",
        "tamiflu": "oseltamivir",
        "ozempic": "semaglutide",
        "wegovy": "semaglutide",
        "mounjaro": "tirzepatide",
        "zepbound": "tirzepatide",
        "jardiance": "empagliflozin",
        "farxiga": "dapagliflozin",
        "invokana": "canagliflozin",
        "victoza": "liraglutide",
        "saxenda": "liraglutide",
        "trulicity": "dulaglutide",
        "januvia": "sitagliptin",
        "tradjenta": "linagliptin",
        "onglyza": "saxagliptin",
        "nesina": "alogliptin",
        "actos": "pioglitazone",
        "avandia": "rosiglitazone",
        "precose": "acarbose",
        "glyset": "miglitol",
        "amaryl": "glimepiride",
        "glucotrol": "glipizide",
        "micronase": "glyburide",
        "diabeta": "glyburide",
        "prandin": "repaglinide",
        "starlix": "nateglinide",
        "humalog": "insulin lispro",
        "novolog": "insulin aspart",
        "apidra": "insulin glulisine",
        "lantus": "insulin glargine",
        "toujeo": "insulin glargine",
        "basaglar": "insulin glargine",
        "levemir": "insulin detemir",
        "tresiba": "insulin degludec",
        # Specialty & Oncology Mappings
        "eliquis": "apixaban",
        "xarelto": "rivaroxaban",
        "pradaxa": "dabigatran",
        "savaysa": "edoxaban",
        "plavix": "clopidogrel",
        "brilinta": "ticagrelor",
        "effient": "prasugrel",
        "entresto": "sacubitril_valsartan",
        "keytruda": "pembrolizumab",
        "opdivo": "nivolumab",
        "tecentriq": "atezolizumab",
        "imfinzi": "durvalumab",
        "yervoy": "ipilimumab",
        "herceptin": "trastuzumab",
        "perjeta": "pertuzumab",
        "avastin": "bevacizumab",
        "rituxan": "rituximab",
        "erbitux": "cetuximab",
        "gleevec": "imatinib",
        "sprycel": "dasatinib",
        "tasigna": "nilotinib",
        "tagrisso": "osimertinib",
        "tarceva": "erlotinib",
        "alecensa": "alectinib",
        "imbruvica": "ibrutinib",
        "calquence": "acalabrutinib",
        "brukinsa": "zanubrutinib",
        "venclexta": "venetoclax",
        "ibrance": "palbociclib",
        "kisqali": "ribociclib",
        "verzenio": "abemaciclib",
        "lynparza": "olaparib",
        "zejula": "niraparib",
        "rubraca": "rucaparib",
        "humira": "adalimumab",
        "enbrel": "etanercept",
        "remicade": "infliximab",
        "cimzia": "certolizumab",
        "simponi": "golimumab",
        "actemra": "tocilizumab",
        "cosentyx": "secukinumab",
        "taltz": "ixekizumab",
        "stelara": "ustekinumab",
        "tremfya": "guselkumab",
        "skyrizi": "risankizumab",
        "benlysta": "belimumab",
        "orencia": "abatacept",
        "cellcept": "mycophenolate_mofetil",
        "uloric": "febuxostat"
    }

    GENERIC_NAMES = {
        "lisinopril", "atorvastatin", "metformin", "amoxicillin", "ibuprofen",
        "losartan", "warfarin", "albuterol", "amlodipine", "levothyroxine",
        "gabapentin", "omeprazole", "metoprolol", "hydrochlorothiazide",
        "simvastatin", "sertraline", "montelukast", "escitalopram",
        "acetaminophen", "furosemide", "fluticasone", "bupropion",
        "duloxetine", "pantoprazole", "prednisone", "rosuvastatin",
        "tamsulosin", "citalopram", "meloxicam", "allopurinol",
        "alprazolam", "clonazepam", "diazepam", "lorazepam", "zolpidem",
        "carvedilol", "spironolactone", "enalapril", "ramipril",
        "valsartan", "atenolol", "propranolol", "hydralazine", "clonidine",
        "pravastatin", "lovastatin", "fenofibrate", "gemfibrozil",
        "ezetimibe", "colchicine", "methotrexate", "hydroxychloroquine",
        "azathioprine", "cyclosporine", "tacrolimus", "prednisolone",
        "dexamethasone", "methylprednisolone", "budesonide", "formoterol",
        "salmeterol", "tiotropium", "ipratropium", "cetirizine",
        "loratadine", "fexofenadine", "diphenhydramine", "hydroxyzine",
        "promethazine", "ondansetron", "metoclopramide", "loperamide",
        "famotidine", "cimetidine", "esomeprazole", "lansoprazole",
        "rabeprazole", "misoprostol", "sulfasalazine", "mesalamine",
        "azithromycin", "clarithromycin", "erythromycin", "doxycycline",
        "minocycline", "tetracycline", "cephalexin", "cefdinir",
        "cefuroxime", "ciprofloxacin", "levofloxacin", "moxifloxacin",
        "metronidazole", "clindamycin", "linezolid", "vancomycin",
        "nitrofurantoin", "trimethoprim", "fluconazole", "ketoconazole",
        "itraconazole", "terbinafine", "acyclovir", "valacyclovir",
        "oseltamivir", "semaglutide", "tirzepatide", "empagliflozin",
        "dapagliflozin", "canagliflozin", "liraglutide", "dulaglutide",
        "sitagliptin", "linagliptin", "saxagliptin", "alogliptin",
        "pioglitazone", "rosiglitazone", "acarbose", "miglitol",
        "glimepiride", "glipizide", "glyburide", "repaglinide",
        "nateglinide", "insulin lispro", "insulin aspart", "insulin glulisine",
        "insulin glargine", "insulin detemir", "insulin degludec"
    }

    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        """
        Dynamically load MASTER_DRUG_INDEX.json to populate all 500 generic and brand names.
        """
        if cls._initialized:
            return

        import os, json
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ingestion", "data", "MASTER_DRUG_INDEX.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "docs", "MASTER_DRUG_INDEX.json"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for drug_key, entry in data.items():
                        gen_name = entry.get("generic", "").lower().strip()
                        if gen_name:
                            cls.GENERIC_NAMES.add(gen_name)
                            cls.GENERIC_NAMES.add(drug_key.lower().strip())
                        for b in entry.get("brands", []):
                            b_clean = b.lower().strip()
                            if b_clean:
                                cls.BRAND_TO_GENERIC[b_clean] = gen_name or drug_key
                    break
                except Exception:
                    pass

        cls._initialized = True

    @classmethod
    def resolve(cls, query_text: str) -> Optional[str]:
        """
        Scan the query text for drug brand names or generic names.
        Returns the canonical lowercase generic name if found, otherwise None.
        """
        if not query_text:
            return None

        cls._ensure_initialized()
            
        words = [w.strip("?,.:;!\"'()[]{}").lower() for w in query_text.split()]
        
        # 1. Direct match check on individual words or bigrams
        for word in words:
            if word in DrugNameResolver.GENERIC_NAMES:
                return word
            if word in DrugNameResolver.BRAND_TO_GENERIC:
                return DrugNameResolver.BRAND_TO_GENERIC[word]
                
        # 2. Check for multi-word generic match or substring match (e.g. "methylprednisolone")
        query_lower = query_text.lower()
        for generic in DrugNameResolver.GENERIC_NAMES:
            if generic in query_lower:
                return generic
                
        for brand, generic in DrugNameResolver.BRAND_TO_GENERIC.items():
            if brand in query_lower:
                return generic
                
        return None
