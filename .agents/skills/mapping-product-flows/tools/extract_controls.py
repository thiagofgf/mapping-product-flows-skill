"""Extract user-facing control labels per component: aria-label, title, placeholder, and button/menu text."""
import os, re, sys, json
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'src/app'  # usage: extract_controls.py <app source dir> [out.json]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'controls.json'
if not os.path.isdir(ROOT):
    sys.exit(f'extract_controls: not a directory: {ROOT}')
SKIP = ('(platform-admin)', '__tests__', '.test.', '/api/')
attr = re.compile(r'''\b(?:aria-label|title|placeholder|label)=["'{]`?([^"'`}]{3,80})["'`}]''')
btn = re.compile(r'<(?:button|Button|DropdownMenuItem|MenuItem|Link|a)\b[^>]*>\s*(?:\{[^}]*\}\s*)*([A-Z][^<>{}\n]{2,60}?)\s*<')
label_kv = re.compile(r'''\blabel:\s*['"]([^'"]{3,60})['"]''')
out = {}
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        p = os.path.join(dp, f)
        if not f.endswith('.tsx') or any(s in p for s in SKIP): continue
        with open(p) as fh:
            src = fh.read()
        found = set(m.strip() for m in attr.findall(src) + btn.findall(src) + label_kv.findall(src))
        found = sorted(x for x in found if not x.startswith(('${', 'e.g', 'http')) and re.search('[a-z]', x))
        if found: out[os.path.relpath(p, ROOT)] = found
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with open(OUT, 'w') as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
tot = sum(len(v) for v in out.values())
print(len(out), 'components,', tot, 'labels')
for k in sorted(out, key=lambda k: -len(out[k]))[:45]: print(f'{len(out[k]):4d} {k}')
