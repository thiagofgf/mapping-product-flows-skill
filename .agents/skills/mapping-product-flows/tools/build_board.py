"""Build an .excalidraw flow board: one lane per use case, screenshot cards joined by labelled arrows.

Usage: build_board2.py spec.json out.excalidraw

spec = {
  "title": str, "subtitle": str, "columns": 5,
  "lang": "en" | "pt",
  "lanes": [{
    "code": "UC-BRD-06", "title": str, "desc": str, "state": "prod" | "flag" | "outside" | "dormant",
    "steps": [{"title": str, "shot": "path.png" | null, "note": str, "route": str, "desc": str,
               "kind": "screen" | "external" | "email" | "thirdparty" | "side", "via": "label of the arrow INTO this step",
               "dashed": bool,      # dashed card border (and, by default, the arrow into it)
               "dashed_in": bool}]  # override for the incoming arrow only
  }],
  "notes": [{"title": str, "body": str, "kind": "note" | "finding"}]   # optional panel at the end
}
"""
import base64, hashlib, json, sys, textwrap

spec = json.load(open(sys.argv[1]))
OUT = sys.argv[2]

COLS = spec.get('columns', 5)
THUMB_W, THUMB_H = 480, 300
CARD_W = THUMB_W + 32
GAP_X, ROW_GAP = 230, 120
LANE_GAP = 140
INK, MUTED = '#1e1e1e', '#5c5f66'
KIND = {  # stroke, fill
    'screen': ('#1971c2', '#e7f1fb'), 'external': ('#868e96', '#f1f3f5'), 'email': ('#0c8599', '#e3fafc'),
    'thirdparty': ('#495057', '#f8f9fa'), 'side': ('#9c36b5', '#f8f0fc'),
    'note': ('#adb5bd', '#f8f9fa'), 'finding': ('#c92a2a', '#fff5f5'),
}
LANG = spec.get('lang', 'en')  # 'en' (default) or 'pt'
STATE = {
    'en': {'prod': 'In production', 'flag': 'Behind a flag (off in production)', 'outside': 'Outside the app', 'dormant': 'Hidden in the UI, link only'},
    'pt': {'prod': 'Em produção', 'flag': 'Atrás de flag (desligada em produção)', 'outside': 'Fora do app', 'dormant': 'Escondido na UI, só por link'},
}[LANG]
STATE_COLORS = {'prod': ('#2f9e44', '#ebfbee'), 'flag': ('#e67700', '#fff9db'), 'outside': ('#868e96', '#f1f3f5'), 'dormant': ('#7048e8', '#f3f0ff')}
STATE = {k: (v,) + STATE_COLORS[k] for k, v in STATE.items()}

elements, files = [], {}
seq = [0]


def base(**kw):
    seq[0] += 1
    d = dict(angle=0, strokeColor=INK, backgroundColor='transparent', fillStyle='solid', strokeWidth=2,
             strokeStyle='solid', roughness=1, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=1000 + seq[0], version=1, versionNonce=2000 + seq[0], isDeleted=False, boundElements=[],
             updated=1, link=None, locked=False)
    d.update(kw)
    return d


def nid(p):
    seq[0] += 1
    return f'{p}-{seq[0]}'


def char_w(size, family):
    return size * (0.6 if family == 5 else 0.53 if family == 6 else 0.6)


def wrap(text, width, size, family):
    per_line = max(10, int(width / char_w(size, family)))
    out = []
    for para in text.split('\n'):
        out.extend(textwrap.wrap(para, per_line) or [''])
    return '\n'.join(out)


def text(x, y, s, size=20, family=5, color=INK, w=None, align='left'):
    lines = s.split('\n')
    width = w if w is not None else max(len(l) for l in lines) * char_w(size, family)
    el = base(id=nid('t'), type='text', x=x, y=y, width=width, height=size * 1.25 * len(lines), text=s,
              originalText=s, fontSize=size, fontFamily=family, textAlign=align, verticalAlign='top',
              containerId=None, autoResize=True, lineHeight=1.25, strokeColor=color, strokeWidth=1, roughness=0)
    elements.append(el)
    return el


def rect(x, y, w, h, stroke, fill, dashed=False, rough=1, sw=2, rounded=True):
    r = base(id=nid('r'), type='rectangle', x=x, y=y, width=w, height=h, strokeColor=stroke, backgroundColor=fill,
             strokeStyle='dashed' if dashed else 'solid', roughness=rough, strokeWidth=sw,
             roundness={'type': 3} if rounded else None)
    elements.append(r)
    return r


def image(x, y, path):
    raw = open(path, 'rb').read()
    fid = hashlib.sha1(raw).hexdigest()
    mime = 'image/jpeg' if path.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
    files[fid] = dict(mimeType=mime, id=fid, created=1, dataURL=f'data:{mime};base64,' + base64.b64encode(raw).decode())
    elements.append(base(id=nid('img'), type='image', x=x, y=y, width=THUMB_W, height=THUMB_H, fileId=fid,
                         status='saved', scale=[1, 1], crop=None, strokeWidth=1, roughness=0))
    elements.append(base(id=nid('frame'), type='rectangle', x=x, y=y, width=THUMB_W, height=THUMB_H,
                         strokeColor='#ced4da', strokeWidth=1, roughness=0))


def arrow(a, b, pts, label=None, dashed=False, label_at=None):
    p0 = (a[0], a[1])
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    el = base(id=nid('arrow'), type='arrow', x=p0[0], y=p0[1], width=max(xs) - min(xs), height=max(ys) - min(ys),
              points=pts, lastCommittedPoint=None, startArrowhead=None, endArrowhead='arrow',
              startBinding=None, endBinding=None, strokeStyle='dashed' if dashed else 'solid', elbowed=False,
              roundness=None)
    elements.append(el)
    if label:
        size = 17
        lw = min(GAP_X - 20, len(label) * char_w(size, 6)) if label_at is None else len(label) * char_w(size, 6)
        lbl = wrap(label, GAP_X - 24, size, 6) if label_at is None else label
        lx, ly = label_at if label_at else (p0[0] + pts[-1][0] / 2 - lw / 2, p0[1] - 22 - 21 * (lbl.count('\n') + 1))
        text(lx, ly, lbl, size=size, family=6, color='#343a40', w=lw)


def card_height(step):
    desc = wrap(step.get('desc', ''), THUMB_W, 16, 6) if step.get('desc') else ''
    return 54 + THUMB_H + 40 + (desc.count('\n') + 1) * 20 + 14 if desc else 54 + THUMB_H + 48


# Header
text(0, 0, spec['title'], size=46, family=5)
text(0, 70, wrap(spec.get('subtitle', ''), COLS * (CARD_W + GAP_X) - GAP_X, 20, 6), size=20, family=6, color=MUTED)
y = 70 + 25 * (wrap(spec.get('subtitle', ''), COLS * (CARD_W + GAP_X) - GAP_X, 20, 6).count('\n') + 1) + 60
board_w = COLS * (CARD_W + GAP_X) - GAP_X

for lane in spec['lanes']:
    # Lane header band
    st_label, st_stroke, st_fill = STATE[lane.get('state', 'prod')]
    desc = wrap(lane.get('desc', ''), board_w - 60, 19, 6)
    head_h = 70 + 24 * (desc.count('\n') + 1) + 18
    rect(-30, y - 20, board_w + 60, head_h, '#ced4da', '#ffffff', rough=0, sw=1)
    text(0, y, f"{lane['code']} · {lane['title']}", size=30, family=5)
    badge_w = len(st_label) * char_w(16, 6) + 28
    rect(board_w - badge_w, y + 2, badge_w, 32, st_stroke, st_fill, rough=0, sw=1)
    text(board_w - badge_w + 14, y + 8, st_label, size=16, family=6, color=st_stroke)
    text(0, y + 48, desc, size=19, family=6, color=MUTED, w=board_w - 60)
    y += head_h + 30

    steps = lane['steps']
    rows = [steps[i:i + COLS] for i in range(0, len(steps), COLS)]
    prev = None  # (x, y, h) of previous card
    for r_i, row in enumerate(rows):
        row_h = max(card_height(s) for s in row)
        for c_i, s in enumerate(row):
            kind = s.get('kind', 'screen')
            stroke, fill = KIND[kind]
            x = c_i * (CARD_W + GAP_X)
            rect(x, y, CARD_W, row_h, stroke, fill, dashed=kind in ('external', 'side') or s.get('dashed', False))
            n = r_i * COLS + c_i + 1
            text(x + 16, y + 14, wrap(f"{n}. {s['title']}", CARD_W - 32, 22, 5), size=22, family=5)
            if s.get('shot'):
                image(x + 16, y + 54, s['shot'])
            else:
                text(x + 32, y + 54 + 40, wrap(s.get('note', ''), THUMB_W - 32, 19, 6), size=19, family=6, color=MUTED, w=THUMB_W - 32)
            ty = y + 54 + THUMB_H + 12
            if s.get('route'):
                text(x + 16, ty, s['route'][:58], size=15, family=3, color=MUTED)
                ty += 24
            if s.get('desc'):
                text(x + 16, ty, wrap(s['desc'], THUMB_W, 16, 6), size=16, family=6, color='#343a40', w=THUMB_W)
            if prev is not None:
                px, py, ph, prow = prev
                if prow == r_i:  # same row: straight arrow between cards
                    a = (px + CARD_W + 10, py + 54 + THUMB_H / 2)
                    arrow(a, None, [[0, 0], [GAP_X - 20, 0]], s.get('via'), s.get('dashed_in', s.get('dashed', False)))
                else:  # row wrap: down from the previous card, along the gap, into this card's top
                    a = (px + CARD_W / 2, py + ph + 10)
                    mid = ROW_GAP / 2 - 10
                    dx = (x + CARD_W / 2) - a[0]
                    pts = [[0, 0], [0, mid], [dx, mid], [dx, ROW_GAP - 20]]
                    lbl = s.get('via')
                    arrow(a, None, pts, None, s.get('dashed_in', s.get('dashed', False)))
                    if lbl:
                        text(a[0] + dx / 2 - len(lbl) * char_w(17, 6) / 2, a[1] + mid - 26, lbl, size=17, family=6,
                             color='#343a40', w=len(lbl) * char_w(17, 6))
            prev = (x, y, row_h, r_i)
        y += row_h + ROW_GAP
    y += LANE_GAP - ROW_GAP

for note in spec.get('notes', []):
    stroke, fill = KIND[note.get('kind', 'note')]
    body = wrap(note['body'], board_w - 80, 18, 6)
    h = 70 + 23 * (body.count('\n') + 1) + 30
    rect(0, y, board_w, h, stroke, fill, rough=0, sw=1)
    text(30, y + 20, note['title'], size=26, family=5)
    text(30, y + 62, body, size=18, family=6, color='#343a40', w=board_w - 80)
    y += h + 40

doc = dict(type='excalidraw', version=2, source='flowmap', elements=elements,
           appState=dict(viewBackgroundColor='#ffffff', gridSize=None), files=files)
json.dump(doc, open(OUT, 'w'))
print(f'{OUT}: {len(spec["lanes"])} lanes, {sum(len(l["steps"]) for l in spec["lanes"])} steps, {len(files)} images')
