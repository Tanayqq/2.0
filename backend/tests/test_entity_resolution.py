import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.usecases.drug_resolver import DrugNameResolver

# 100 US Brand Aliases
US_BRANDS = [
    ("lipitor", "atorvastatin"), ("tylenol", "acetaminophen"), ("advil", "ibuprofen"),
    ("motrin", "ibuprofen"), ("zoloft", "sertraline"), ("lexapro", "escitalopram"),
    ("lasix", "furosemide"), ("crestor", "rosuvastatin"), ("cozaar", "losartan"),
    ("coumadin", "warfarin"), ("ventolin", "albuterol"), ("proair", "albuterol"),
    ("norvasc", "amlodipine"), ("synthroid", "levothyroxine"), ("neurontin", "gabapentin"),
    ("prilosec", "omeprazole"), ("lopressor", "metoprolol"), ("toprol", "metoprolol"),
    ("zocor", "simvastatin"), ("singulair", "montelukast"), ("flonase", "fluticasone"),
    ("wellbutrin", "bupropion"), ("cymbalta", "duloxetine"), ("protonix", "pantoprazole"),
    ("deltasone", "prednisone"), ("flomax", "tamsulosin"), ("celexa", "citalopram"),
    "mobic", "zyloprim", "xanax", "klonopin", "valium", "ativan", "ambien", "coreg",
    "aldactone", "vasotec", "altace", "diovan", "tenormin", "inderal", "apresoline",
    "catapres", "pravachol", "mevacor", "tricor", "lopid", "zetia", "colcrys", "trexall",
    "plaquenil", "imuran", "neoral", "prograf", "orapred", "decadron", "medrol", "pulmicort",
    "spiriva", "zyrtec", "claritin", "allegra", "benadryl", "vistaril", "zofran", "reglan",
    "imodium", "pepcid", "nexium", "prevacid", "aciphex", "zithromax", "biaxin", "vibramycin",
    "keflex", "omnicef", "ceftin", "cipro", "levaquin", "avelox", "flagyl", "cleocin", "zyvox",
    "vancocin", "macrobid", "diflucan", "valtrex", "tamiflu", "ozempic", "wegovy", "mounjaro",
    "jardiance", "farxiga", "invokana", "eliquis", "xarelto", "pradaxa", "plavix", "brilinta",
    "entresto", "kerendia"
]

# 100 Indian Brand Aliases
INDIAN_BRANDS = [
    ("crocin", "paracetamol"), ("calpol", "paracetamol"), ("dolo", "paracetamol"),
    ("dolo 650", "paracetamol"), ("dolo650", "paracetamol"), ("pacimol", "paracetamol"),
    ("pcm", "paracetamol"), ("panadol", "paracetamol"), ("glycomet", "metformin"),
    ("cetapin", "metformin"), ("gluformin", "metformin"), ("clavam", "amoxicillin_clavulanate"),
    ("moxikind-cv", "amoxicillin_clavulanate"), ("moxikind cv", "amoxicillin_clavulanate"),
    ("augmentin", "amoxicillin_clavulanate"), ("pan-d", "pantoprazole_domperidone"),
    ("pan d", "pantoprazole_domperidone"), ("pantocid", "pantoprazole"),
    ("pantocid-d", "pantoprazole_domperidone"), ("razo", "rabeprazole"),
    ("rabekind", "rabeprazole"), ("veloz", "rabeprazole"), ("telma", "telmisartan"),
    ("telma-h", "telmisartan"), ("telmikind", "telmisartan"), ("telista", "telmisartan"),
    ("amlong", "amlodipine"), ("stamlo", "amlodipine"), ("cilacar", "cilnidipine"),
    ("cilaheart", "cilnidipine"), ("metolar", "metoprolol"), ("metolar-xr", "metoprolol"),
    ("nebicard", "nebivolol"), ("nebi", "nebivolol"), ("cardivas", "carvedilol"),
    ("rosuvas", "rosuvastatin"), ("razel", "rosuvastatin"), ("atorva", "atorvastatin"),
    ("atocor", "atorvastatin"), ("tenepride", "teneligliptin"), ("zita-met", "sitagliptin_metformin"),
    ("galvus", "vildagliptin"), ("galvus-met", "vildagliptin"), ("janumet", "sitagliptin_metformin"),
    ("zoryl", "glimepiride"), ("amaryl", "glimepiride"), ("glynase", "glipizide"),
    ("taxim-o", "cefixime"), ("mahacef", "cefixime"), ("zipod", "cefpodoxime"),
    ("monocepht", "ceftriaxone"), ("monocef", "ceftriaxone"), ("oframax", "ceftriaxone"),
    ("magnex", "cefoperazone_sulbactam"), ("pipzo", "piperacillin_tazobactam"),
    ("meronem", "meropenem"), ("merocrit", "meropenem"), ("faropen", "faropenem"),
    ("linospan", "linezolid"), ("lizolid", "linezolid"), ("dapto", "daptomycin"),
    ("vancogen", "vancomycin"), ("niftas", "nitrofurantoin"), ("norflox", "norfloxacin"),
    ("zocon", "fluconazole"), ("itrasys", "itraconazole"), ("canditral", "itraconazole"),
    ("ambisome", "amphotericin_b"), ("azithral", "azithromycin"), ("aaz", "azithromycin"),
    ("zady", "azithromycin"), ("claribid", "clarithromycin"), ("klacid", "clarithromycin"),
    ("doxy-1", "doxycycline"), ("monodox", "doxycycline"), ("nucoxia", "etoricoxib"),
    ("etoshine", "etoricoxib"), ("zerodol", "aceclofenac"), ("zerodol-p", "aceclofenac"),
    ("zerodol-sp", "aceclofenac"), ("hifenac", "aceclofenac"), ("ultracet", "tramadol"),
    ("tramazac", "tramadol"), ("cyclopam", "dicyclomine"), ("drotin", "drotaverine"),
    ("spasmonil", "dicyclomine"), ("duphalac", "lactulose"), ("rifagut", "rifaximin"),
    ("mesacol", "mesalamine"), ("foracort", "formoterol_budesonide"),
    ("seretide", "salmeterol_fluticasone"), ("levolin", "levosalbutamol"),
    ("asthalin", "albuterol"), ("deriphyllin", "theophylline"), ("citistar", "citicoline"),
    ("stugeron", "cinnarizine"), ("vertin", "betahistine"), ("levipil", "levetiracetam"),
    ("epitril", "clonazepam"), ("lonazep", "clonazepam"), ("frisium", "clobazam"),
    ("valparin", "sodium_valproate"), ("encorate", "divalproex"), ("sizodon", "risperidone"),
    ("oleanz", "olanzapine"), ("seroquin", "quetiapine"), ("qutan", "quetiapine"),
    ("nexito", "escitalopram"), ("clonotril", "clonazepam"), ("etilaam", "etizolam"),
    ("etizola", "etizolam"), ("alprax", "alprazolam"), ("restyl", "alprazolam"),
    ("urimax", "tamsulosin"), ("silodal", "silodosin"), ("dutas", "dutasteride"),
    ("manforce", "sildenafil"), ("megalis", "tadalafil"), ("toptada", "tadalafil"),
    ("shelcal", "calcium_vitamin_d3"), ("orofer", "iron_sucrose")
]

class TestEntityResolution:
    
    def test_us_brand_alias_resolution(self):
        passed = 0
        total = len(US_BRANDS)
        for item in US_BRANDS:
            brand = item[0] if isinstance(item, tuple) else item
            resolved = DrugNameResolver.resolve(brand)
            assert resolved is not None, f"US Brand '{brand}' failed resolution!"
            passed += 1
        assert passed == total

    def test_indian_brand_alias_resolution(self):
        passed = 0
        total = len(INDIAN_BRANDS)
        for brand, expected_generic in INDIAN_BRANDS:
            resolved = DrugNameResolver.resolve(brand)
            assert resolved == expected_generic, f"Indian Brand '{brand}' resolved to '{resolved}', expected '{expected_generic}'!"
            passed += 1
        assert passed == total

    def test_generic_name_self_resolution(self):
        generics = ["lisinopril", "atorvastatin", "metformin", "amoxicillin", "ibuprofen", "losartan", "warfarin", "albuterol", "furosemide", "vancomycin"]
        for g in generics:
            assert DrugNameResolver.resolve(g) == g, f"Generic '{g}' failed self-resolution!"
