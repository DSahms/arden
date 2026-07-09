import os, re
pattern = re.compile(r'(TODO|FIXME|HACK|XXX|not implemented|placeholder|stub|broken|full deletion|TBD|pending)', re.IGNORECASE)
results = []
skip = {'.venv','__pycache__','.git','.pytest_cache','personalock_wellness','node_modules','.chromadb','data','logs','output','images','audit_output_20260213'}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                lines = open(path, encoding='utf-8', errors='ignore').readlines()
                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        results.append(path + ':' + str(i) + ': ' + line.rstrip())
            except: pass
print('RESULTS:')
for r in results: print(r)
print('TOTAL:', len(results))
