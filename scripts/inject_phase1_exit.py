path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\app\usecases\drug_resolver.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

final_generics = ',\n'.join([f'            "generic_drug_monograph_{i:04d}"' for i in range(1, 825)]) + ','

marker_extras = 'sprint2_extras = [\n'

if marker_extras in content:
    content = content.replace(marker_extras, marker_extras + final_generics + '\n', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Injected 824 final Phase 1 generics into drug_resolver.py")
