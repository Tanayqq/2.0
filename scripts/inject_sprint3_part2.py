path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

part2_sprint3 = '''        "cetirizine_hcl", "loratadine_tab", "fexofenadine_180mg", "desloratadine", "levocetirizine_5mg", "olopatadine",
        "azelastine", "epinastine", "bepotastine", "alcaftadine", "ketotifen", "emedastine", "cromolyn_sodium", "nedocromil",
        "lodoxamide", "pemirolast", "fluticasone_furoate", "mometasone_furoate", "triamcinolone_acetonide", "budesonide_rhinocort",
        "ciclesonide_omnaris", "beclomethasone_beconase", "flunisolide", "azelastine_fluticasone", "olopatadine_mometasone",
        "ipratropium_nasal", "oxymetazoline", "phenylephrine_nasal", "xylometazoline", "naphazoline", "tetrahydrozoline",
        "pseudoephedrine", "phenylephrine_oral", "phenylpropanolamine", "ephedrine", "guaifenesin", "dextromethorphan",
        "benzonatate", "codeine_phosphate", "hydrocodone_bitartrate", "dimehydrinate", "meclizine", "promethazine_hcl",
        "doxylamine", "pyridoxine_doxylamine", "scopolamine_patch", "droperidol", "haloperidol_decanoate", "fluphenazine",
        "fluphenazine_decanoate", "perphenazine", "trifluoperazine", "thioridazine", "mesoridazine", "chlorpromazine",
        "promazine", "triflupromazine", "acetophenazine", "flupentixol", "zuclopenthixol", "chlorprothixene", "thiothixene",
        "loxapine", "amoxapine", "clozapine_fazaclo", "olanzapine_zyprexa", "quetiapine_seroquel", "risperidone_risperdal",
        "ziprasidone_geodon", "aripiprazole_abilify", "paliperidone_invega", "iloperidone_fanapt", "asenapine_saphris",
        "lurasidone_latuda", "cariprazine_vraylar", "brexpiprazole_rexulti", "lumateperone_caplyta", "pimavanserin_nuplazid",
        "lithium_carbonate", "lithium_citrate", "valproate_sodium", "divalproex_sodium", "carbamazepine_tegretol",
        "oxcarbazepine_trileptal", "lamotrigine_lamictal", "topiramate_topamax", "gabapentin_neurontin", "pregabalin_lyrica",
        "fluoxetine_prozac", "sertraline_zoloft", "paroxetine_paxil", "fluvoxamine_luvox", "citalopram_celexa", "escitalopram_lexapro",
        "venlafaxine_effexor", "desvenlafaxine_pristiq", "duloxetine_cymbalta", "levomilnacipran_fetzima", "milnacipran_savella",
        "bupropion_wellbutrin", "mirtazapine_remeron", "trazodone_desyrel", "nefazodone", "vilazodone_viibryd", "vortioxetine_trintellix",
        "amitriptyline", "nortriptyline", "imipramine", "desipramine", "doxepin", "clomipramine", "protriptyline", "trimipramine",
        "phenelzine", "tranylcypromine", "isocarboxazid", "selegiline_emsam", "rasagiline_azilect", "safinamide_xadago",'''

marker_extras = 'sprint2_extras = [\n'

if marker_extras in content:
    content = content.replace(marker_extras, marker_extras + part2_sprint3 + '\n', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Injected Sprint 3 Part 2 generics into drug_resolver.py")
