"""Generate the use-case catalog (Markdown) from the board specs, so codes and wording match the boards exactly.
Usage: gen_md.py index.json header.md out.md
  header.md  title, base commit, personas, states legend, flag table (written by hand once)
  index.json the build_index.py spec: kpis, areas [{n, name, spec, file}], findings [[severity, text]]"""
import json, sys
def read_json(path):
    with open(path) as fh:
        return json.load(fh)


if len(sys.argv) < 4:
    sys.exit('usage: gen_md.py index.json header.md out.md')
idx = read_json(sys.argv[1])
with open(sys.argv[2]) as fh:
    header = fh.read().rstrip()
LANG = idx.get('lang', 'en')  # 'en' (default) or 'pt'
T = {'en': dict(kind={'email': ' [e-mail]', 'thirdparty': ' [third party]', 'external': ' [outside the app]', 'finding': ' [loose end]'},
                size='**Product size:**', table='| Board | Area | Use cases | Screens |', steps='Steps: ', findings='## Loose ends, by severity', ftable='| Severity | Finding |'),
     'pt': dict(kind={'email': ' [e-mail]', 'thirdparty': ' [terceiro]', 'external': ' [fora do app]', 'finding': ' [ponta solta]'},
                size='**Tamanho do produto:**', table='| Quadro | Área | Casos de uso | Telas |', steps='Passos: ', findings='## Pontas soltas, por gravidade', ftable='| Gravidade | Achado |')}[LANG]
ICON = {'prod': '🟢', 'flag': '🟡', 'dormant': '🟣', 'outside': '⚪'}
KIND = T['kind']
out = [header, '', T['size'] + ' ' + ', '.join(f'{n} {l}' for n, l in idx['kpis']) + '.', '',
       T['table'], '|---|---|---|---|']
specs = [(a, read_json(a['spec'])) for a in idx['areas']]
for a, d in specs:
    em = {s['shot'] for l in d['lanes'] for s in l['steps'] if s.get('kind') == 'email' and s.get('shot')}
    sh = {s['shot'] for l in d['lanes'] for s in l['steps'] if s.get('shot')} - em
    out.append(f"| `{a['file']}` | {a['name']} | {len(d['lanes'])} | {len(sh)} |")
out += ['', '---', '']
for a, d in specs:
    out += [f"## {a['n']} · {a['name']}", '', f"_{d.get('subtitle', '')}_", '']
    for l in d['lanes']:
        out += [f"**{l['code']} · {l['title']}** {ICON.get(l.get('state', 'prod'), '')}", l['desc']]
        steps = []
        for i, s in enumerate(l['steps']):
            via = f" ({s['via']})" if s.get('via') else ''
            extra = f": {s['desc']}" if s.get('desc') else (f": {s['note']}" if s.get('note') else '')
            steps.append(f"{i + 1}. {s['title']}{via}{KIND.get(s.get('kind'), '')}{extra}")
        out += [T['steps'] + ' → '.join(steps), '']
    for n in d.get('notes', []):
        out += [f"**{n['title']}**", '', n['body'], '']
    out += ['---', '']
out += [T['findings'], '', T['ftable'], '|---|---|']
out += [f'| {sev} | {t.replace("|", "/")} |' for sev, t in idx['findings']]
with open(sys.argv[3], 'w') as fh:
    fh.write('\n'.join(out) + '\n')
print(sys.argv[3], sum(len(d['lanes']) for _, d in specs), 'use cases')
