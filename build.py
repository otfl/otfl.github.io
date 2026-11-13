"""Builds the OTFL website.

You normally never run this yourself: every time you save a change on GitHub,
GitHub runs it automatically and publishes the site (see .github/workflows/deploy.yml).

It reads the text files in data/, the photos in images/, fills template.html,
and writes the finished website into the _site/ folder.
Photos are automatically resized and compressed, so you can upload phone photos as they are.
"""
import html, os, re, shutil, sys
import yaml
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_site')
E = html.escape
problems = []


def load(name):
    path = os.path.join(ROOT, 'data', name + '.yml')
    try:
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        sys.exit(f'\n*** There is a formatting mistake in data/{name}.yml ***\n{e}\n'
                 'Tip: if a line of text contains a colon followed by a space (": "), put the whole text in quotes.\n')


def photo(folder, name, alt):
    if not name:
        return ''
    if not os.path.exists(os.path.join(ROOT, 'images', folder, name)):
        problems.append(f'images/{folder}/{name} is named in a data file but the photo is not in that folder')
    return f'<img src="images/{folder}/{E(name)}" alt="{E(alt)}" loading="lazy" decoding="async">'


# ---------- text helpers ----------
def chem(s):
    """Subscript the numbers in chemical formulas: TiO2, Sm2Co17, Cu2-xS, Sm2(Co,Fe,Cu,Zr)17."""
    def sub(m):
        t = m.group(0)
        if not re.search(r'[A-Z]', t) or not re.search(r'\d', t):
            return t
        return re.sub(r'(?<=[A-Za-z\)])(\d+(?:[\-–]x)?|[\-–]x)', r'<sub>\1</sub>', t)
    s = re.sub(r'\b[A-Z][A-Za-z0-9\-–]*\d[A-Za-z0-9]*\b', sub, s)
    return re.sub(r'(\([A-Z][a-z]?[^()]*,[^()]*\))(\d+)\b', r'\1<sub>\2</sub>', s)


def bold_pi(s):
    return re.sub(r'(Emila Panda|E\. Panda)', r'<b>\1</b>', s)


def t(s):
    return chem(E(str(s or '')))


def initials(n):
    n = re.sub(r'^(Dr\.|Mr\.|Ms\.|Prof\.)\s*', '', n)
    return ''.join(w[0] for w in n.split()[:2])


def clean_name(n):
    return re.sub(r'^(Mr\.|Ms\.)\s*', '', n)


def link(url, text, cls='mono'):
    return f'<a class="{cls}" href="{E(url)}">{text}</a>' if url else ''


# ---------- load ----------
site = load('site')
news = load('news') or []
team = load('team')
pubs = load('publications')
grants = load('grants') or []
awards = load('awards') or []
courses = load('courses') or []
research = load('research')
facilities = load('facilities') or []
gallery = load('gallery') or []


# ---------- sections ----------
def person_card(p, role):
    pic = photo('team', p.get('photo'), p['name']) or f'<div class="ph">{initials(p["name"])}</div>'
    parts = [f'<span class="mono prole">{role}</span><h4>{E(clean_name(p["name"]))}</h4>']
    if p.get('status'): parts.append(f'<p class="pnote">{E(p["status"])}</p>')
    if p.get('note'): parts.append(f'<p class="pnote">{E(p["note"])}</p>')
    if p.get('email'): parts.append(f'<p class="mono pmail">{E(p["email"])}</p>')
    if p.get('details'): parts.append('<ul class="pedu">' + ''.join(f'<li>{t(d)}</li>' for d in p['details']) + '</ul>')
    if p.get('thesis'):
        th = t(p['thesis'])
        if p.get('thesis_link'): th = f'<a href="{E(p["thesis_link"])}">{th}</a>'
        parts.append(f'<p class="pthesis"><span class="mono">{E(p.get("thesis_type", "Thesis"))}</span> {th}</p>')
    return f'<article class="pcard rv"><div class="pimg">{pic}</div><div class="pbody">{"".join(parts)}</div></article>'


def alumni_card(p):
    pic = photo('team', p.get('photo'), p['name']) or f'<div class="ph">{initials(p["name"])}</div>'
    name = E(clean_name(p['name']))
    if p.get('link'): name = f'<a href="{E(p["link"])}">{name}</a>'
    note = E(p.get('note') or p.get('status') or '')
    th = ''
    if p.get('thesis'):
        th = t(p['thesis'])
        if p.get('thesis_link'): th = f'<a href="{E(p["thesis_link"])}">{th}</a>'
        th = f'<p class="athesis">{th}</p>'
    return f'<article class="acard rv"><div class="aimg">{pic}</div><div><h4>{name}</h4><p class="anote">{note}</p>{th}</div></article>'


def pub_list(items):
    out = []
    for p in items or []:
        y = p.get('year') or ''
        a = link(p.get('link'), ('DOI' if 'doi' in str(p.get('link', '')) else 'Link') + ' ↗', 'doi mono')
        out.append(f'<li class="pub" data-y="{y}" data-s="{E(str(p["text"]).lower())}"><span class="py mono">{y}</span><p>{bold_pi(t(p["text"]))}</p>{a}</li>')
    return ''.join(out)


gl = team['group_leader']
R = {
    '{{STATEMENT}}': E(site['statement']),
    '{{ABOUT}}': E(site['about']),
    '{{ABOUT_FIGURE}}': E(site['about_figure']),
    '{{ABOUT_FIGURE_ALT}}': E(site.get('about_figure_caption', '')),
    '{{ABOUT_FIGURE_CAPTION}}': t(site.get('about_figure_caption', '')),
    '{{HERO_PHOTO}}': E(site['hero_photo']),
    '{{HERO_CAPTION}}': t(site.get('hero_caption', '')),
    '{{GROUP_PHOTO}}': E(site['group_photo']),
    '{{OPENINGS}}': E(site['openings']),
    '{{EMAIL}}': E(site['email']),
    '{{ADDRESS}}': '<br>'.join(E(a) for a in site['address']),
    '{{MAPS}}': E(site['maps_link']),
    '{{PI_NAME}}': E(gl['name']), '{{PI_TITLE}}': E(gl['title']), '{{PI_PHOTO}}': E(gl['photo']), '{{PI_EMAIL}}': E(gl['email']),
    '{{PI_EDU}}': ''.join(f'<li>{E(x)}</li>' for x in gl['education']),
    '{{PI_APPT}}': ''.join(f'<li>{E(x)}</li>' for x in gl['appointments']),
    '{{PI_HON}}': E(gl['honors']),
    '{{PHD}}': ''.join(person_card(p, 'PhD scholar') for p in team.get('phd_scholars') or []),
    '{{MTECH}}': ''.join(person_card(p, 'MTech student') for p in team.get('mtech_students') or []),
    '{{STAFF}}': ''.join(person_card(p, 'Research staff') for p in team.get('research_staff') or []),
    '{{ALUMNI}}': ''.join(alumni_card(p) for p in team.get('alumni') or []),
    '{{OTHERS}}': ''.join(f'<li>{E(o)}</li>' for o in team.get('other_alumni') or []),
    '{{RESEARCH}}': ''.join(
        f'<article class="rarea rv"><span class="mono rn">{i + 1:02d}</span><h3>{E(a["title"])}</h3><ul>'
        + ''.join(f'<li>{t(x)}</li>' for x in a.get('items') or []) + '</ul></article>'
        for i, a in enumerate(research['areas'])),
    '{{HIGHLIGHTS}}': ''.join(
        f'<figure class="hl"><div class="hlimg">{photo("highlights", h["image"], h["title"])}</div><figcaption>'
        f'<span class="mono">{E(h.get("journal", ""))}</span><h4>{t(h["title"])}</h4>{link(h.get("link"), "Read paper ↗")}</figcaption></figure>'
        for h in research.get('highlights') or []),
    '{{FACILITIES}}': ''.join(
        f'<div class="fgroup"><h3 class="fh rv">{E(g["group"])}</h3><div class="fgrid">'
        + ''.join(f'<figure class="fcard rv"><div class="fimg">{photo("facilities", it.get("photo"), it["name"])}</div><figcaption>{E(it["name"])}</figcaption></figure>' for it in g['items'])
        + '</div></div>' for g in facilities),
    '{{JOURNAL}}': pub_list(pubs.get('journal')),
    '{{CONF}}': pub_list(pubs.get('conference')),
    '{{PATENTS}}': pub_list(pubs.get('patents')),
    '{{GRANTS}}': ''.join(
        f'<li class="grant rv"><span class="mono gy">{E(str(g.get("years", "")))}</span><div><h4>{t(g["title"])}</h4>'
        f'<p>{E(g.get("funder", ""))} <span class="mono gr">· {E(g.get("role", "PI"))}</span></p></div></li>' for g in grants),
    '{{AWARDS}}': ''.join(f'<li class="rv">{t(a)}</li>' for a in awards),
    '{{COURSES}}': ''.join(
        f'<li class="rv"><span class="mono ccode">{E(c.get("code", ""))}</span><span>{E(c["name"])}'
        + (f' <span class="cnote">({E(c["note"])})</span>' if c.get('note') else '') + '</span></li>' for c in courses),
    '{{NEWS}}': ''.join(
        f'<li class="nrow"><span class="mono nd">{E(str(n["date"]))}</span><p>{t(n["text"])}'
        + (f' {link(n.get("link"), "Read ↗")}' if n.get('link') else '') + '</p></li>' for n in news),
    '{{GALLERY}}': ''.join(
        f'<button class="gitem" data-full="images/gallery/{E(g)}" aria-label="Open photo">{photo("gallery", g, "OTFL group photo")}</button>' for g in gallery),
    '{{NJ}}': str(len(pubs.get('journal') or [])), '{{NC}}': str(len(pubs.get('conference') or [])),
    '{{NP}}': str(len(pubs.get('patents') or [])), '{{NG}}': str(len(grants)), '{{NNEWS}}': str(len(news)),
}
page = open(os.path.join(ROOT, 'template.html'), encoding='utf-8').read()
for k, v in R.items():
    page = page.replace(k, v)
left = re.findall(r'\{\{\w+\}\}', page)
if left:
    sys.exit(f'Template placeholders not filled: {left}')

# ---------- write output + resized images ----------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(page)
open(os.path.join(OUT, '.nojekyll'), 'w').close()

MAXW = {'team': 700, 'gallery': 1600, 'facilities': 1200, 'highlights': 1200, 'site': 2200}
for folder in os.listdir(os.path.join(ROOT, 'images')):
    src_dir = os.path.join(ROOT, 'images', folder)
    if not os.path.isdir(src_dir):
        continue
    dst_dir = os.path.join(OUT, 'images', folder)
    os.makedirs(dst_dir, exist_ok=True)
    for name in os.listdir(src_dir):
        src, dst = os.path.join(src_dir, name), os.path.join(dst_dir, name)
        try:
            im = ImageOps.exif_transpose(Image.open(src))
            w = MAXW.get(folder, 1600)
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            if name.lower().endswith(('.jpg', '.jpeg')):
                im.convert('RGB').save(dst, quality=82, optimize=True, progressive=True)
            else:
                im.save(dst, optimize=True)
        except Exception:
            shutil.copy(src, dst)

for p in problems:
    print('WARNING:', p)
print(f'Built _site/index.html: {len(news)} news items, {R["{{NJ}}"]} journal papers, {len(gallery)} gallery photos.')
