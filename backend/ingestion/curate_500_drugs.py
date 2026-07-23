import os
import json
import requests
from typing import Dict, List, Set

# ── EXCLUDED CATEGORIES (Non-Therapeutics & Diagnostics) ───────────────────
EXCLUDED_PATTERNS = [
    "zinc oxide", "alcohol", "salicylic acid", "menthol", "benzalkonium",
    "sodium fluoride", "titanium dioxide", "homosalate", "octisalate",
    "octocrylene", "avobenzone", "isopropyl alcohol", "oxygen", "nitrous oxide",
    "barium sulfate", "gadoterate", "iohexol", "iopamidol", "technetium",
    "sodium chloride 0.9", "dextrose 5%", "sterile water", "vaccine",
    "toxoid", "calcium carbonate", "antacid", "hand sanitizer", "sunscreen"
]

# ── 10 MEDICAL SPECIALTY TAXONOMY (500 CLINICAL PRESCRIPTION DRUGS) ─────────
SPECIALTY_TAXONOMY: Dict[str, List[str]] = {
    "Cardiology": [
        # Anticoagulants, Antiplatelets, Statins, ACEi, ARBs, Beta Blockers, Antiarrhythmics, Heart Failure
        "apixaban", "rivaroxaban", "dabigatran", "edoxaban", "warfarin", "clopidogrel", "ticagrelor", "prasugrel",
        "atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin", "ezetimibe", "fenofibrate", "gemfibrozil",
        "sacubitril_valsartan", "lisinopril", "enalapril", "ramipril", "benazepril", "captopril", "losartan", "valsartan",
        "candesartan", "irbesartan", "olmesartan", "telmisartan", "amlodipine", "nifedipine", "felodipine", "diltiazem",
        "verapamil", "metoprolol", "atenolol", "carvedilol", "bisoprolol", "propranolol", "labetalol", "nebivolol",
        "spironolactone", "eplerenone", "furosemide", "torsemide", "bumetanide", "hydrochlorothiazide", "chlorthalidone",
        "indapamide", "hydralazine", "isosorbide_mononitrate", "isosorbide_dinitrate", "nitroglycerin", "ranolazine",
        "amiodarone", "dronedarone", "flecainide", "propafenone", "sotalol", "digoxin", "ivabradine", "vericiguat",
        "macitentan", "ambrisentan", "riociguat", "selexipag", "epoprostenol", "treprostinil", "bosentan", "cilostazol",
        "pentoxifylline", "alirocumab", "evolocumab", "inclisiran", "bempedoic_acid", "icosapent_ethyl", "omega_3_acid",
        "clonidine", "guanfacine", "doxazosin", "terazosin", "prazosin"
    ],
    "Endocrinology": [
        # GLP-1 RAs, SGLT2i, DPP4i, Insulins, Thyroid, Adrenal, Bone Metabolism
        "semaglutide", "tirzepatide", "dulaglutide", "liraglutide", "exenatide", "lixisenatide", "orlistat",
        "metformin", "dapagliflozin", "empagliflozin", "canagliflozin", "ertugliflozin", "sitagliptin", "linagliptin",
        "alogliptin", "saxagliptin", "glimepiride", "glipizide", "gliclazide", "glyburide", "pioglitazone", "rosiglitazone",
        "repaglinide", "nateglinide", "acarbose", "miglitol", "pramlintide", "insulin_glargine", "insulin_lispro",
        "insulin_aspart", "insulin_degludec", "insulin_detemir", "insulin_glulisine", "insulin_regular", "insulin_nph",
        "levothyroxine", "liothyronine", "methimazole", "propylthiouracil", "carbimazole", "bromocriptine", "cabergoline",
        "hydrocortisone", "fludrocortisone", "dexamethasone", "prednisone", "alendronate", "risedronate", "ibandronate",
        "zoledronic_acid", "denosumab", "teriparatide", "abaloparatide", "romosozumab", "raloxifene"
    ],
    "Psychiatry": [
        # SSRIs, SNRIs, Antipsychotics, Mood Stabilizers, Anxiolytics, ADHD
        "sertraline", "escitalopram", "citalopram", "fluoxetine", "paroxetine", "fluvoxamine", "duloxetine",
        "venlafaxine", "desvenlafaxine", "levomilnacipran", "bupropion", "mirtazapine", "trazodone", "vilazodone",
        "vortioxetine", "aripiprazole", "quetiapine", "olanzapine", "risperidone", "paliperidone", "ziprasidone",
        "lurasidone", "cariprazine", "brexpiprazole", "clozapine", "haloperidol", "fluphenazine", "chlorpromazine",
        "lithium", "valproic_acid", "lamotrigine", "carbamazepine", "oxcarbazepine", "alprazolam", "clonazepam",
        "lorazepam", "diazepam", "temazepam", "oxazepam", "chlordiazepoxide", "buspirone", "hydroxyzine", "zolpidem",
        "zopiclone", "eszopiclone", "ramelteon", "suvorexant", "lemborexant", "methylphenidate", "dexmethylphenidate",
        "amphetamine", "dextroamphetamine", "lisdexamfetamine", "atomoxetine", "viloxazine", "modafinil", "armodafinil",
        "pitolisant", "solriamfetol"
    ],
    "Neurology": [
        # Anticonvulsants, Parkinson's, MS, Migraine, Dementia
        "levetiracetam", "brivaracetam", "gabapentin", "pregabalin", "topiramate", "lacosamide", "lamotrigine",
        "phenytoin", "fosphenytoin", "phenobarbital", "primidone", "clobazam", "vigabatrin", "perampanel",
        "carbidopa_levodopa", "pramipexole", "ropinirole", "rotigotine", "apomorphine", "selegiline", "rasagiline",
        "safinamide", "entacapone", "opicapone", "amantadine", "trihexyphenidyl", "donepezil", "rivastigmine",
        "galantamine", "memantine", "lecanemab", "donanemab", "sumatriptan", "rizatriptan", "eletriptan", "zolmitriptan",
        "galcanezumab", "fremanezumab", "erenumab", "eptinezumab", "rimegepant", "atogepant", "ubrogepant", "lasmiditan",
        "dimethyl_fumarate", "diroximel_fumarate", "fingolimod", "siponimod", "ozanimod", "ocrelizumab"
    ],
    "Pulmonology": [
        # Bronchodilators, Inhaled Corticosteroids, Biologics, Anticholinergics
        "albuterol", "levalbuterol", "salmeterol", "formoterol", "vilanterol", "indacaterol", "fluticasone",
        "budesonide", "beclomethasone", "mometasone", "ciclesonide", "tiotropium", "umeclidinium", "ipratropium",
        "aclidinium", "glycopyrrolate", "montelukast", "zafirlukast", "zileuton", "roflumilast", "theophylline",
        "omalizumab", "mepolizumab", "benralizumab", "reslizumab", "dupilumab", "tezepelumab", "pirfenidone",
        "nintedanib", "acetylcysteine", "dornase_alfa", "ivacaftor", "lumacaftor", "tezacaftor", "elexacaftor",
        "cetirizine", "levocetirizine", "loratadine", "desloratadine", "fexofenadine"
    ],
    "Gastrointestinal": [
        # PPIs, H2 Blockers, IBD, Antiemetics, Motility
        "omeprazole", "pantoprazole", "esomeprazole", "lansoprazole", "rabeprazole", "dexlansoprazole", "famotidine",
        "cimetidine", "nizatidine", "ondansetron", "granisetron", "palonosetron", "aprepitant", "fosaprepitant",
        "metoclopramide", "domperidone", "prochlorperazine", "promethazine", "dicyclomine", "hyoscyamine", "lubiprostone",
        "linaclotide", "plecanatide", "eluxadoline", "loperamide", "diphenoxylate_atropine", "bismuth_subsalicylate",
        "mesalamine", "sulfasalazine", "balsalazide", "olsalazine", "infliximab", "adalimumab", "vedolizumab",
        "ustekinumab", "tofacitinib", "upadacitinib", "sucralfate", "misoprostol", "ursodiol", "obeticholic_acid",
        "lactulose", "rifaximin", "peg_3350", "senna"
    ],
    "Infectious_Disease": [
        # Antibiotics, Antifungals, Antivirals
        "amoxicillin", "amoxicillin_clavulanate", "ampicillin", "ampicillin_sulbactam", "piperacillin_tazobactam",
        "cephalexin", "cefazolin", "cefuroxime", "cefdinir", "ceftriaxone", "cefepime", "ceftaroline", "meropenem",
        "ertapenem", "imipenem_cilastatin", "aztreonam", "ciprofloxacin", "levofloxacin", "moxifloxacin", "azithromycin",
        "clarithromycin", "erythromycin", "doxycycline", "minocycline", "tetracycline", "clindamycin", "linezolid",
        "tedizolid", "vancomycin", "daptomycin", "dalbavancin", "fidaxomicin", "nitrofurantoin", "trimethoprim_sulfamethoxazole",
        "metronidazole", "fluconazole", "itraconazole", "voriconazole", "posaconazole", "isavuconazonium", "echinocandin",
        "caspofungin", "micafungin", "anidulafungin", "terbinafine", "nystatin", "amphotericin_b", "acyclovir",
        "valacyclovir", "famciclovir", "ganciclovir", "valganciclovir", "oseltamivir", "baloxavir", "remdesivir",
        "paxlovid", "sofosbuvir_velpatasvir", "glecaprevir_pibrentasvir", "tenofovir_alafenamide", "emtricitabine"
    ],
    "Oncology": [
        # Targeted Therapies, Immunotherapy, Cytotoxics, Endocrine Therapy
        "pembrolizumab", "nivolumab", "atezolizumab", "durvalumab", "ipilimumab", "trastuzumab", "pertuzumab",
        "bevacizumab", "rituximab", "cetuximab", "panitumumab", "imatinib", "dasatinib", "nilotinib", "bosutinib",
        "ponatinib", "osimertinib", "erlotinib", "gefitinib", "afatinib", "alectinib", "brigatinib", "lorlatinib",
        "ibrutinib", "acalabrutinib", "zanubrutinib", "venetoclax", "palbociclib", "ribociclib", "abemaciclib",
        "olaparib", "niraparib", "rucaparib", "encorafenib", "dabrafenib", "trametinib", "trametinib", "cobimetinib",
        "tamoxifen", "letrozole", "anastrozole", "exemestane", "fulvestrant", "bicalutamide", "enzalutamide",
        "apalutamide", "darolutamide", "abiraterone", "leuprolide", "goserelin", "degarelix", "relugolix", "cyclophosphamide",
        "methotrexate", "capecitabine", "fluorouracil", "gemcitabine", "carboplatin", "cisplatin", "oxaliplatin",
        "paclitaxel", "docetaxel", "cabazitaxel", "doxorubicin", "epirubicin", "irinotecan", "topotecan", "etoposide",
        "vincristine", "vinblastine", "vinorelbine", "bortezomib", "carfilzomib", "lenalidomide", "pomalidomide",
        "thalidomide", "elotuzumab", "daratumumab", "isatuximab"
    ],
    "Rheumatology_Immunology": [
        # DMARDs, Biologics, JAKi, Immunosuppressants
        "methotrexate", "hydroxychloroquine", "sulfasalazine", "leflunomide", "tofacitinib", "upadacitinib",
        "baricitinib", "adalimumab", "etanercept", "infliximab", "certolizumab", "golimumab", "tocilizumab",
        "sarilumab", "secukinumab", "ixekizumab", "brodalumab", "ustekinumab", "guselkumab", "risankizumab",
        "tildrakizumab", "belimumab", "rituximab", "abatacept", "azathioprine", "cyclosporine", "tacrolimus",
        "mycophenolate_mofetil", "allopurinol", "febuxostat"
    ],
    "Nephrology_Urology": [
        # BPH, OAB, Hyperkalemia, CKD
        "tamsulosin", "silodosin", "alfuzosin", "finasteride", "dutasteride", "solifenacin", "darifenacin",
        "fesoterodine", "oxybutynin", "tolterodine", "trospium", "mirabegron", "vibegron", "bethanechol",
        "patiromer", "sodium_zirconium_cyclosilicate", "sevelamer", "lanthanum", "sucroferric_oxyhydroxide",
        "calcitriol", "paricalcitol", "doxercalciferol", "cinacalcet", "etelcalcetide", "finerenone"
    ]
}

def curate_500_drugs():
    all_drugs: List[str] = []
    drug_to_specialty: Dict[str, str] = {}

    for specialty, drug_list in SPECIALTY_TAXONOMY.items():
        for d in drug_list:
            d_norm = d.lower().strip()
            # Exclusion check
            if any(pat in d_norm for pat in EXCLUDED_PATTERNS):
                print(f"Skipping excluded item: {d_norm}")
                continue
            if d_norm not in drug_to_specialty:
                all_drugs.append(d_norm)
                drug_to_specialty[d_norm] = specialty

    print(f"Total curated clinical prescription therapeutics: {len(all_drugs)}")

    # Ensure target of 500 by fetching top prescription generic names from openFDA if under
    if len(all_drugs) < 500:
        print(f"Fetching additional clinical generic drugs from openFDA to reach 500 target...")
        url = "https://api.fda.gov/drug/label.json?count=openfda.generic_name.exact&limit=1000"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                results = r.json().get("results", [])
                for item in results:
                    term = item["term"].lower().strip()
                    # Filter out numbers, multi-ingredients, and excluded patterns
                    if (
                        len(term) > 3
                        and not any(char.isdigit() for char in term)
                        and "," not in term
                        and "/" not in term
                        and not any(pat in term for pat in EXCLUDED_PATTERNS)
                        and term not in drug_to_specialty
                    ):
                        d_clean = term.replace(" ", "_")
                        all_drugs.append(d_clean)
                        drug_to_specialty[d_clean] = "General Therapeutics"
                        if len(all_drugs) >= 500:
                            break
        except Exception as e:
            print(f"openFDA fetch warning: {e}")

    # Write drugs_500.txt
    out_txt = os.path.join(os.path.dirname(__file__), "drugs_500.txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        for d in all_drugs[:500]:
            f.write(f"{d}\n")

    # Write taxonomy_500.json
    out_json = os.path.join(os.path.dirname(__file__), "data", "taxonomy_500.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "total_count": len(all_drugs[:500]),
            "drug_to_specialty": {d: drug_to_specialty.get(d, "General Therapeutics") for d in all_drugs[:500]},
            "specialties": {s: [d for d in all_drugs[:500] if drug_to_specialty.get(d) == s] for s in SPECIALTY_TAXONOMY.keys()}
        }, f, indent=2)

    print(f"Successfully generated {out_txt} and {out_json} with {len(all_drugs[:500])} drugs!")

if __name__ == "__main__":
    curate_500_drugs()
