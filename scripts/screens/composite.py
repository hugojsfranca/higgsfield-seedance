#!/usr/bin/env python3
"""Lay the rendered interfaces onto the blank glass of the storyboard frames, in perspective.

  python3 composite.py --tool      refresh corners.html: shot data, thumbnails, picking copies
  python3 composite.py --pull      take the newest screens*.json from ~/Downloads into this folder
  python3 composite.py --all       composite every plate that has placements
  python3 composite.py KF_S09_B    composite one plate
  python3 composite.py --list      what each plate still needs

screens.json holds the placements picked in corners.html. One plate can carry several screens
(S03_C has two panels, S06_A three), so each plate holds a list:

  {"KF_S03_C": {"placements": [{"screen": "L03_incident", "corners": [[x, y], ...4]},
                               {"screen": "L04_chat",     "corners": [[x, y], ...4]}]}}

Corners are in the frame's own pixels, in any order. The older single-screen form
{"screen": ..., "corners": ...} is still read.

This is the storyboard's compositing step, not the film's: it shows what the shot will look like
once post lays the interface over the plate. Standard library plus Pillow.
"""
import argparse, csv, glob, json, math, os, re, shutil, sys, hashlib
from PIL import Image, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
os.chdir(ROOT)


# ---- geometry ---------------------------------------------------------------------------------

def order4(pts):
    """Put four corners into TL, TR, BR, BL order, whatever order they were given in."""
    if len(pts) != 4:
        return pts
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    ring = sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    k = min(range(4), key=lambda i: ring[i][0] + ring[i][1])
    return [ring[(k + i) % 4] for i in range(4)]


def coeffs(src, dst):
    """Perspective coefficients mapping the dst quad back to the source rectangle (what PIL wants)."""
    m, b = [], []
    for (sx, sy), (dx, dy) in zip(src, dst):
        m.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy]); b.append(sx)
        m.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy]); b.append(sy)
    n = 8                                   # Gaussian elimination, so there is no numpy to install
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(m[r][i]))
        if abs(m[p][i]) < 1e-12:
            raise ValueError('degenerate quad: are three of the corners on one line?')
        m[i], m[p] = m[p], m[i]
        b[i], b[p] = b[p], b[i]
        for r in range(n):
            if r != i:
                f = m[r][i] / m[i][i]
                for c in range(i, n):
                    m[r][c] -= f * m[i][c]
                b[r] -= f * b[i]
    return [b[i] / m[i][i] for i in range(n)]


# ---- files ------------------------------------------------------------------------------------

def frame_for(plate):
    """The approved take of a plate, else its newest candidate."""
    man = os.path.join(PROJ, 'assets/manifest.csv')
    if os.path.exists(man):
        for r in csv.DictReader(open(man, encoding='utf-8')):
            if r['id'] == plate:
                p = os.path.join(PROJ, 'assets', r['file'])
                if os.path.exists(p):
                    return p
    for pat in (f'keyframes/{plate}.png', f'*/keyframes/{plate}.png'):          # the approved still beside its prompt
        hit = sorted(glob.glob(os.path.join(PROJ, pat)))
        if hit:
            return hit[0]
    takes = sorted(glob.glob(os.path.join(PROJ, f'candidates/{plate}_*t[0-9]*.png')),
                   key=lambda p: int(re.search(r'_t(\d+)\.png$', p).group(1)))
    return takes[-1] if takes else None


def placements_of(entry):
    """Normalise one screens.json entry to a list of {screen, corners}, reading the old form too."""
    if not isinstance(entry, dict):
        return []
    items = entry.get('placements')
    if items is None and entry.get('corners'):
        items = [{'screen': entry.get('screen'), 'corners': entry['corners']}]
    good = []
    for it in items or []:
        c = it.get('corners') or []
        if it.get('screen') and len(c) == 4 and all(len(p) == 2 for p in c):
            good.append({'screen': it['screen'], 'corners': [[float(p[0]), float(p[1])] for p in c]})
    return good


def load_config():
    if not os.path.exists('screens.json'):
        return {}
    raw = json.load(open('screens.json', encoding='utf-8'))
    return {k: placements_of(v) for k, v in raw.items() if placements_of(v)}


def needs():
    """(shot, plate, states) for every glass the mapping asks for.

    "L03 + L04" is two separate screens on one plate. "I02_input → I03_objective" is ONE glass that
    shows two states during the shot: it is placed once, and either state can be previewed on it."""
    out = []
    if not os.path.exists('mapping.md'):
        return out                       # no interfaces mapped yet: the page still lists every plate
    for line in open('mapping.md', encoding='utf-8'):
        if line.startswith('|'):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            # a data row names a keyframe ID in its second cell; the header, the rule and "—" rows do not
            if len(c) > 2 and re.fullmatch(r'[A-Za-z0-9_.-]*[A-Za-z0-9][A-Za-z0-9_.-]*', c[1]) and c[1].lower() not in ('plate', 'keyframe'):
                for glass in c[2].split('+'):
                    states = [x.strip() for x in glass.split('→') if x.strip()]
                    if states:
                        out.append((c[0], c[1], states))
    return out


def jpeg(src, dest, width=None, quality=88):
    """Write a JPEG copy if it is missing or older than its source."""
    if os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(src):
        return
    im = Image.open(src).convert('RGB')
    if width and im.width > width:
        im = im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)
    im.save(dest, quality=quality, optimize=True)


# ---- compositing ------------------------------------------------------------------------------

def composite(plate, placements, out_dir='composites'):
    frame_path = frame_for(plate)
    if not frame_path:
        return f'{plate}: no frame generated yet'
    frame = Image.open(frame_path).convert('RGB')
    out, done = frame.copy(), []
    for pl in placements:
        screen_path = os.path.join('out', pl['screen'] + '.png')
        if not os.path.exists(screen_path):
            print(f'  {plate}: {screen_path} is not rendered yet, skipped')
            continue
        ui = Image.open(screen_path).convert('RGB')
        dst = [tuple(p) for p in order4([tuple(p) for p in pl['corners']])]

        # Squeezing a 2560 px interface into a ~150 px quad in one perspective step shreds it: the
        # transform point-samples and drops most rows. Pre-scale the interface to about twice the
        # size it will occupy, with a filter that averages properly, then warp the small version.
        span = max(max(x for x, _ in dst) - min(x for x, _ in dst),
                   max(y for _, y in dst) - min(y for _, y in dst))
        target = max(64, int(span * 2))
        if ui.width > target:
            ui = ui.resize((target, max(1, round(target * ui.height / ui.width))), Image.LANCZOS)
        src = [(0, 0), (ui.width, 0), (ui.width, ui.height), (0, ui.height)]
        try:
            k = coeffs(src, dst)
        except ValueError as e:
            print(f'  {plate} / {pl["screen"]}: {e}, skipped')
            continue
        warped = ui.transform(frame.size, Image.PERSPECTIVE, k, resample=Image.BICUBIC)
        mask = Image.new('L', ui.size, 255).transform(frame.size, Image.PERSPECTIVE, k,
                                                      resample=Image.BICUBIC)
        mask = mask.filter(ImageFilter.GaussianBlur(0.6))
        out.paste(warped, (0, 0), mask)

        # Keep the plate's own glass: its specular highlights go back over the interface, and the
        # interface is pulled 10% toward the plate's exposure so it sits in the photograph.
        glass = frame.convert('L').point(lambda v: max(0, v - 150) * 2)
        glass = ImageChops.multiply(glass, mask).filter(ImageFilter.GaussianBlur(1.2))
        out = ImageChops.screen(out, Image.merge('RGB', (glass, glass, glass)))
        out = Image.composite(Image.blend(out, frame, 0.10), out, mask)
        done.append(pl['screen'])

    if not done:
        return f'{plate}: nothing placed'
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, f'{plate}.png')
    out.save(dest)
    return f'{plate} -> {dest}  ({" + ".join(done)})'


# ---- the page's data ---------------------------------------------------------------------------

def write_tool(cfg):
    wanted = {}
    for _shot, plate, states in needs():
        wanted.setdefault(plate, [])
        if states not in wanted[plate]:
            wanted[plate].append(states)
    rows = list(csv.DictReader(open(os.path.join(PROJ, 'shotlist.csv'), encoding='utf-8')))
    os.makedirs('thumbs', exist_ok=True)
    os.makedirs('frames', exist_ok=True)

    shots, seen = [], set()
    for r in rows:
        plate = r['start_keyframe'].strip()
        if not plate or ':' in plate:     # `ENV05:ext_day` is a reference still used in the edit, not a plate
            continue
        fp = frame_for(plate)
        thumb = view = None
        fw = fh = 0
        if fp:
            # Everything the page loads has to live under ui/, or a viewer that only serves this
            # folder shows the grid and then a blank picker. The picking copy keeps the frame's
            # exact pixel size, so corners map one to one onto the original.
            thumb, view = f'thumbs/{plate}.jpg', f'frames/{plate}.jpg'
            jpeg(fp, thumb, width=600, quality=82)
            jpeg(fp, view, quality=92)
            fw, fh = Image.open(fp).size
        first = plate not in seen
        seen.add(plate)
        screens = []
        for states in wanted.get(plate, []):
            rendered = []
            for sc in states:
                full = f'out/{sc}.png'
                if os.path.exists(full):          # the grid never needs 2560 px of interface
                    jpeg(full, f'thumbs/ui_{sc}.jpg', width=1000, quality=85)
                    rendered.append(sc)
            screens.append({'name': states[0], 'states': states, 'rendered': rendered})
        shots.append({
            'shot': f"{r['scene']}.{r['shot']}", 'plate': plate, 'desc': r['description'],
            'seconds': [r['film_in'], r['film_out']], 'reuse': not first,
            'frame': view, 'thumb': thumb, 'fw': fw, 'fh': fh,
            'screens': screens, 'placements': cfg.get(plate, []),
        })

    # Placements live in the browser per address, and every project served from localhost shares one
    # address, so the storage key carries this project's own path.
    film = {'key': 'screens:' + hashlib.sha1(PROJ.encode()).hexdigest()[:10], 'title': os.path.basename(PROJ)}
    payload = 'window.FILM = ' + json.dumps(film) + ';\nwindow.SHOTS = ' + json.dumps(shots, indent=1) + ';'
    page = open('corners.html', encoding='utf-8').read()
    a, b = page.index('<!--DATA-->'), page.index('<!--/DATA-->')
    page = page[:a] + '<!--DATA-->\n<script>' + payload + '</script>\n' + page[b:]
    open('corners.html', 'w', encoding='utf-8').write(page)

    need = sum(len(s['screens']) for s in shots if not s['reuse'])
    done = sum(len(s['placements']) for s in shots if not s['reuse'])
    print(f'corners.html refreshed: {len(shots)} shots, {done} of {need} interfaces placed.')


def pull():
    cands = glob.glob(os.path.expanduser('~/Downloads/screens*.json'))
    if not cands:
        print('no screens*.json in ~/Downloads'); return 1
    newest = max(cands, key=os.path.getmtime)
    try:
        raw = json.load(open(newest, encoding='utf-8'))
        n = sum(len(placements_of(v)) for v in raw.values())
    except Exception as e:
        print(f'{newest} is not a screens.json: {e}'); return 1
    if os.path.exists('screens.json'):
        shutil.copy2('screens.json', 'screens.backup.json')
    shutil.copy2(newest, 'screens.json')
    print(f'{os.path.basename(newest)} -> ui/screens.json ({n} placements; the old file is screens.backup.json)')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('plates', nargs='*')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--tool', action='store_true', help='refresh corners.html')
    ap.add_argument('--pull', action='store_true', help='take the newest screens*.json from ~/Downloads')
    a = ap.parse_args()

    if a.pull and pull():
        return 1
    cfg = load_config()

    if a.tool:
        write_tool(cfg)
    if a.list:
        for _shot, plate, states in needs():
            has = any(p['screen'] in states for p in cfg.get(plate, []))
            missing = [x for x in states if not os.path.exists(f'out/{x}.png')]
            print(f"{plate:<18}{' → '.join(states):<40}{'placed' if has else 'NOT PLACED':<12}"
                  f"{'frame' if frame_for(plate) else 'no frame':<10}"
                  f"{'not rendered: ' + ', '.join(missing) if missing else 'rendered'}")
    plates = list(cfg) if a.all else a.plates
    for p in plates:
        if p not in cfg:
            print(f'{p}: no placements in screens.json (pick them in corners.html)')
            continue
        print(composite(p, cfg[p]))
    if not (a.tool or a.list or a.pull or plates):
        ap.error('name a plate, or use --all, --list, --tool or --pull')
    return 0


if __name__ == '__main__':
    sys.exit(main())
