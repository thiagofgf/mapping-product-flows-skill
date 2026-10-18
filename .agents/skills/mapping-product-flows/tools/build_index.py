"""Overview board: totals, one tile per area board (thumbnail + counts + use-case list), legend, ranked findings.
Usage: build_index.py index.json out.excalidraw   (index.json: {title, subtitle, kpis:[[n,label]], areas:[{n,name,spec,file}], legend:[[label,stroke,fill]], findings:[[severity,text]], lang:"en"|"pt"}); severity is high|medium|low (or alto|médio|baixo)"""
import base64, hashlib, json, sys, textwrap
spec = json.load(open(sys.argv[1])); OUT = sys.argv[2]
INK, MUTED = '#1e1e1e', '#5c5f66'
LANG = spec.get('lang', 'en')  # 'en' (default) or 'pt'
T = {'en': dict(sev={'high': 'High', 'medium': 'Medium', 'low': 'Low'}, uc='use cases', screens='screens', emails='e-mails', findings='Loose ends, by severity',
                state={'prod': 'In production', 'flag': 'Behind a flag', 'dormant': 'Hidden in the UI', 'outside': 'Outside the app'}),
     'pt': dict(sev={'high': 'Alto', 'medium': 'Médio', 'low': 'Baixo'}, uc='casos de uso', screens='telas', emails='e-mails', findings='Pontas soltas, por gravidade',
                state={'prod': 'Em produção', 'flag': 'Atrás de flag', 'dormant': 'Escondido na UI', 'outside': 'Fora do app'})}[LANG]
SEV_KEY = {'high': 'high', 'alto': 'high', 'medium': 'medium', 'médio': 'medium', 'medio': 'medium', 'low': 'low', 'baixo': 'low'}
SEV_COLORS = {'high': ('#c92a2a', '#fff5f5'), 'medium': ('#e67700', '#fff9db'), 'low': ('#495057', '#f8f9fa')}
STATE = {k: (T['state'][k],) + c for k, c in {'prod': ('#2f9e44', '#ebfbee'), 'flag': ('#e67700', '#fff9db'), 'dormant': ('#7048e8', '#f3f0ff'), 'outside': ('#868e96', '#f1f3f5')}.items()}
els, files, seq = [], {}, [0]
def base(**kw):
    seq[0] += 1
    d = dict(angle=0, strokeColor=INK, backgroundColor='transparent', fillStyle='solid', strokeWidth=2, strokeStyle='solid', roughness=1, opacity=100,
             groupIds=[], frameId=None, roundness=None, seed=5000 + seq[0], version=1, versionNonce=6000 + seq[0], isDeleted=False, boundElements=[], updated=1, link=None, locked=False)
    d.update(kw); return d
def cw(size, fam): return size * (0.6 if fam == 5 else 0.53)
def wrap(t, w, size, fam):
    n = max(10, int(w / cw(size, fam))); out = []
    for para in t.split('\n'): out.extend(textwrap.wrap(para, n) or [''])
    return '\n'.join(out)
def text(x, y, s, size=20, fam=6, color=INK, w=None):
    if not s:
        return 0  # an empty text element breaks the Excalidraw scene restore
    lines = s.split('\n'); width = w if w is not None else max(len(l) for l in lines) * cw(size, fam)
    els.append(base(id=f't{seq[0]}', type='text', x=x, y=y, width=width, height=size * 1.25 * len(lines), text=s, originalText=s, fontSize=size, fontFamily=fam,
                    textAlign='left', verticalAlign='top', containerId=None, autoResize=True, lineHeight=1.25, strokeColor=color, strokeWidth=1, roughness=0))
    return size * 1.25 * len(lines)
def rect(x, y, w, h, stroke, fill, sw=1, rough=0, dashed=False):
    els.append(base(id=f'r{seq[0]}', type='rectangle', x=x, y=y, width=w, height=h, strokeColor=stroke, backgroundColor=fill, strokeWidth=sw, roughness=rough,
                    strokeStyle='dashed' if dashed else 'solid', roundness={'type': 3}))
def image(x, y, w, h, path):
    raw = open(path, 'rb').read(); fid = hashlib.sha1(raw).hexdigest()
    mime = 'image/jpeg' if path.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
    files[fid] = dict(mimeType=mime, id=fid, created=1, dataURL=f'data:{mime};base64,' + base64.b64encode(raw).decode())
    els.append(base(id=f'i{seq[0]}', type='image', x=x, y=y, width=w, height=h, fileId=fid, status='saved', scale=[1, 1], crop=None, strokeWidth=1, roughness=0))
    els.append(base(id=f'f{seq[0]}', type='rectangle', x=x, y=y, width=w, height=h, strokeColor='#ced4da', strokeWidth=1, roughness=0))
COLS, TW, GAP = 4, 760, 50
W = COLS * TW + (COLS - 1) * GAP
y = 0
text(0, y, spec['title'], 52, 5); y += 80
y += text(0, y, wrap(spec['subtitle'], W, 22, 6), 22, 6, MUTED) + 40
kw = (W - (len(spec['kpis']) - 1) * 30) / len(spec['kpis'])
for i, (n, label) in enumerate(spec['kpis']):
    x = i * (kw + 30); rect(x, y, kw, 150, '#ced4da', '#ffffff')
    text(x + 30, y + 22, str(n), 64, 5); text(x + 30, y + 104, label, 22, 6, MUTED)
y += 190
lx = 0
for label, stroke, fill in spec['legend']:
    bw = len(label) * cw(18, 6) + 36; rect(lx, y, bw, 40, stroke, fill); text(lx + 18, y + 9, label, 18, 6, stroke); lx += bw + 16
y += 80
for row in range(0, len(spec['areas']), COLS):
    chunk = spec['areas'][row:row + COLS]; tiles = []
    for a in chunk:
        d = json.load(open(a['spec']))
        lanes = d['lanes']; shots = [s['shot'] for l in lanes for s in l['steps'] if s.get('shot')]
        emails = len({s['shot'] for l in lanes for s in l['steps'] if s.get('kind') == 'email' and s.get('shot')})
        ucs = '\n'.join(wrap(f"{l['code']}  {l['title']}", TW - 60, 17, 6) for l in lanes)
        tiles.append((a, lanes, shots, emails, ucs))
    IMG_H = (TW - 56) / 1.6  # thumbnail height, same expression used to draw it
    th = max(110 + IMG_H + 26 + 22 * (t[4].count('\n') + 1) + 30 for t in tiles)
    for c, (a, lanes, shots, emails, ucs) in enumerate(tiles):
        x = c * (TW + GAP); st = lanes[0].get('state', 'prod') if lanes else 'prod'; sl, ss, sf = STATE.get(st, STATE['prod'])
        rect(x, y, TW, th, '#adb5bd', '#ffffff', sw=2, rough=1)
        text(x + 28, y + 24, f"{a['n']} · {a['name']}", 32, 5)
        bw = len(sl) * cw(16, 6) + 26; rect(x + TW - bw - 24, y + 28, bw, 30, ss, sf); text(x + TW - bw - 11, y + 34, sl, 16, 6, ss)
        uniq = len(set(shots)) - emails
        text(x + 28, y + 74, f"{len(lanes)} {T['uc']} · {uniq} {T['screens']}" + (f" · {emails} {T['emails']}" if emails else '') + f"  ·  {a['file']}", 18, 6, MUTED)
        thumb = a.get('thumb') or (shots[0] if shots else None)
        if thumb:
            image(x + 28, y + 110, TW - 56, IMG_H, thumb)
        text(x + 28, y + 110 + IMG_H + 26, ucs, 17, 6, '#343a40', w=TW - 56)
    y += th + GAP
y += 30
fh = 84 + sum(max(34, 19 * 1.25 * (wrap(t, W - 220, 19, 6).count('\n') + 1) + 10) for _, t in spec['findings']) + 30
rect(0, y, W, fh, '#c92a2a', '#fffafa')
text(30, y + 24, T['findings'], 32, 5); fy = y + 84
for sev, t in spec['findings']:
    k = SEV_KEY[sev.lower()]; s, f = SEV_COLORS[k]; rect(30, fy, 110, 30, s, f); text(45, fy + 5, T['sev'][k], 17, 6, s)
    h = text(160, fy + 3, wrap(t, W - 220, 19, 6), 19, 6, '#343a40', w=W - 220); fy += max(34, h + 10)
json.dump(dict(type='excalidraw', version=2, source='flowmap', elements=els, appState=dict(viewBackgroundColor='#ffffff', gridSize=None), files=files), open(OUT, 'w'))
print(OUT, len(spec['areas']), 'areas')
