# Builds a slideshow composition (cover, real document pages, end card) from a JSON spec, in the Prep'Up style
# of slides/fiche-algos-mp. Then shoot it with: node shoot-slides.cjs <outdir> slides-<name>
# usage: python3 make_slides.py spec.json
# spec: {"name": "genetique-bg", "pages": ["/abs/page1.png", ...], "labels": ["...", ...],
#        "pill": "...", "title_html": "...", "chips": ["..."], "meta": "...",
#        "end_title_html": "...", "end_more": "...", "credit": "...", "crop": [x0, y0, x1, y1] (fractions, optional),
#        "card_css": "extra CSS, e.g. width-fixed cards for half-page crops" (optional)}
import json, os, shutil, sys
from PIL import Image

WORK = '/home/user/rayenhassine007/prep-up/brag-output/work'
spec = json.load(open(sys.argv[1]))
name = 'slides-' + spec['name']
out = os.path.join(WORK, 'comp', name)
os.makedirs(out, exist_ok=True)
shutil.copy('/home/user/rayenhassine007/prep-up/dist/logo.png', os.path.join(out, 'logo.png'))

x0, y0, x1, y1 = spec.get('crop', [0.04, 0.03, 0.96, 0.97])
for i, p in enumerate(spec['pages'], 1):
    im = Image.open(p).convert('RGB')
    w, h = im.size
    im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).save(os.path.join(out, f'crop-{i}.png'))

tpl = open(os.path.join(WORK, 'comp', 'slides-fiche-algos-mp', 'index.html')).read()
head = tpl[:tpl.index('<body>')]
script = tpl[tpl.index('<script>'):]
brand = '<div class="brand"><img src="logo.png" alt="" /><span>Prep<span class="grad-text">\'Up</span></span></div>'
n = len(spec['pages'])
chips = ''.join(f'<span>{c}</span>' for c in spec['chips'])
body = f'''<body>
  <section class="slide cover">
    <div class="blob" style="width:700px;height:700px;background:var(--violet);left:-260px;top:-260px"></div>
    <div class="blob" style="width:640px;height:640px;background:var(--cyan);right:-280px;top:520px"></div>
    <div class="blob" style="width:560px;height:560px;background:var(--blue);left:160px;bottom:-360px"></div>
    <div class="pill">{spec['pill']}</div>
    <h1>{spec['title_html']}</h1>
    <div class="list">{chips}</div>
    <div class="meta">{spec['meta']}</div>
    <div class="swipe">Swipe <span class="grad-text">→</span></div>
    {brand}
  </section>
'''
for i, lab in enumerate(spec['labels'], 1):
    body += f'  <section class="slide page"><div class="label"><b>{lab}</b></div><div class="card"><img src="crop-{i}.png" alt="" /></div>{brand}<div class="count">{i} / {n}</div></section>\n'
body += f'''  <section class="slide end">
    <div class="blob" style="width:700px;height:700px;background:var(--violet);right:-280px;top:-260px"></div>
    <div class="blob" style="width:640px;height:640px;background:var(--blue);left:-300px;bottom:-200px"></div>
    <img class="logo" src="logo.png" alt="" />
    <h2>{spec['end_title_html']}</h2>
    <div class="url grad-text">prep-upp.com/ressources</div>
    <div class="more">{spec['end_more']}</div>
    <div class="credit">{spec['credit']}</div>
  </section>
'''
if spec.get('card_css'):
    head = head.replace('</style>', spec['card_css'] + '\n</style>')
open(os.path.join(out, 'index.html'), 'w').write(head + body + script)
print('built', name, n + 2, 'slides')
