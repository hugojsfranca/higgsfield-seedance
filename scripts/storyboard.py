#!/usr/bin/env python3
"""Build storyboard.html: the film as one page the user reviews, annotates and decides on.

Run it in a film project folder the moment the shot list exists, and again after every stage. With no
frames yet it is still the place to manage the scenes: order, timings, voice-over, on-screen copy and
notes. Frames and composited screens appear as they are made.

    python3 storyboard.py [--project DIR] [--title "Film name"] [--open]

Reads, all optional except the first:
  shotlist.csv               running order, timings, cut windows (the plan skill's format)
  scenes.csv                 scene,title,vo,copy,understand   — what is said and written, per scene
  <act>/keyframes/<ID>.png   the approved still for a keyframe (wins over any candidate)
  candidates/<ID>_*t<N>.png  candidate takes; the highest N is shown
  ui/mapping.md              which interface lands on which plate   (screens/composite.py)
  ui/composites/<ID>.png     the plate with its interface placed

On the page, per shot: Keep / Change / Regenerate / Cut and a note. Per scene: a note, and the
voice-over and on-screen copy editable in place, with a words-per-second check. Everything is kept in
the browser under a key unique to the project, follows its frame if shots are renumbered, and leaves
as `storyboard-notes-<date>.json` (Download notes) or as text (Copy for Claude).

The page's CSS and JavaScript are plain string constants, NOT f-strings: an f-string turns every
`\\n` in the script into a real newline and breaks it.
"""
import argparse, csv, glob, hashlib, html, json, os, re, sys


def read_scenes():
    """scenes.csv -> {scene: {title, vo, copy, understand}}. Missing file, missing columns: all fine."""
    out = {}
    if os.path.exists('scenes.csv'):
        for r in csv.DictReader(open('scenes.csv', encoding='utf-8-sig')):
            n = (r.get('scene') or '').strip()
            if n:
                out[n] = {k: (r.get(k) or '').strip() for k in ('title', 'vo', 'copy', 'understand')}
    return out


def screens_by_plate():
    """ui/mapping.md rows `| shot | plate | screen + screen | note |` -> {plate: [screens]}."""
    out = {}
    if os.path.exists('ui/mapping.md'):
        for line in open('ui/mapping.md', encoding='utf-8'):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if line.startswith('|') and len(c) > 2 and re.fullmatch(r'[A-Za-z0-9_.-]+', c[1]) and c[1].lower() != 'plate':
                out[c[1]] = [s.strip() for s in c[2].split('+')]
    return out


def small_copy(src, dest, width=600):
    """A JPEG thumbnail, rebuilt only when its source is newer. Without Pillow, the source itself."""
    try:
        if not os.path.exists(dest) or os.path.getmtime(dest) < os.path.getmtime(src):
            from PIL import Image
            im = Image.open(src).convert('RGB')
            im.thumbnail((width, width))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            im.save(dest, quality=84, optimize=True)
        return dest
    except Exception:
        return src


def take_number(path):
    m = re.search(r'_t(\d+)\.\w+$', path)
    return int(m.group(1)) if m else 0


def from_manifest(plate):
    """`ENV05:ext_day` or a bare ID recorded with assets.py -> the approved file, if it exists."""
    if not os.path.exists('assets/manifest.csv'):
        return None
    aid, _, view = plate.partition(':')
    for r in csv.DictReader(open('assets/manifest.csv', encoding='utf-8-sig')):
        if (r.get('id') or '').strip() == aid and (not view or (r.get('view') or '').strip() == view):
            for p in (r.get('file') or '', os.path.join('assets', r.get('file') or '')):
                if p and os.path.isfile(p):
                    return p
    return None


def frame_for(plate):
    """The still to show for a start frame: the approved one if there is one, else the newest take."""
    hit = from_manifest(plate)
    if hit:
        return hit
    if ':' in plate:
        return None
    for pat in (f'keyframes/{plate}.png', f'*/keyframes/{plate}.png', f'keyframes/{plate}.jpg', f'*/keyframes/{plate}.jpg'):
        hit = sorted(glob.glob(pat))
        if hit:
            return hit[0]
    takes = sorted(glob.glob(f'candidates/{plate}_*t[0-9]*.*') + glob.glob(f'candidates/{plate}.*'), key=take_number)
    takes = [t for t in takes if t.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    return takes[-1] if takes else None


def pictures_for(plate):
    """(grid image, full-size image, composited?) for a plate."""
    raw = frame_for(plate)
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', plate)
    comp = f'ui/composites/{plate}.png'
    if os.path.exists(comp) and (not raw or os.path.getmtime(comp) >= os.path.getmtime(raw)):
        return small_copy(comp, f'storyboard_files/{safe}_comp.jpg'), comp, True
    if not raw:
        return None, None, False
    return small_copy(raw, f'storyboard_files/{safe}.jpg'), raw, False


def esc(s):
    return html.escape(s or '', quote=True)


def num(s, default=0.0):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


CSS = r'''
 :root{color-scheme:light dark;--bg:#fff;--fg:#14171a;--mut:#666e78;--line:#e3e6ea;--pan:#f6f7f9;--acc:#1f6feb;
   --keep:#177245;--change:#8a6d2f;--redo:#1f6feb;--cut:#a12d2d}
 @media (prefers-color-scheme:dark){:root{--bg:#15171b;--fg:#e9ebee;--mut:#8d939c;--line:#2b3037;--pan:#1b1e23;--acc:#6aa9ff}}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
 body.locked{overflow:hidden}
 header{padding:22px 32px 12px}
 h1{margin:0;font-size:22px} .sub{color:var(--mut);font-size:13px;margin:4px 0 0}
 .hrow{display:flex;align-items:center;gap:8px;flex-wrap:wrap} .grow{flex:1}
 a.nav{color:var(--acc);text-decoration:none;font-size:13px} a.nav:hover{text-decoration:underline}
 button{background:var(--pan);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:5px 10px;
   cursor:pointer;font:inherit;font-size:13px}
 button:hover{border-color:var(--acc)} button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
 button.p{background:var(--acc);color:#fff;border-color:var(--acc);font-weight:600}
 .bar{position:sticky;top:0;z-index:6;background:var(--bg);border-bottom:1px solid var(--line);padding:8px 32px}
 .lbl2{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}
 button.f.on{border-color:var(--acc);color:var(--acc);font-weight:600}
 .idx{display:flex;gap:3px;flex-wrap:wrap;margin-top:6px}
 .idx a{min-width:24px;text-align:center;font-size:11px;padding:2px 4px;border-radius:4px;border:1px solid var(--line);
   color:var(--mut);text-decoration:none}
 .idx a:hover{border-color:var(--acc);color:var(--acc)}
 .idx a.some{border-color:var(--change);color:var(--change)} .idx a.all{background:var(--keep);border-color:var(--keep);color:#fff}
 #warn,#orph{display:none;padding:10px 32px;font-size:13px}
 #warn{background:#4a3a12;color:#ffd98a} #orph{background:#3d1f1f;color:#ffc2c2}
 #warn:not([hidden]),#orph:not([hidden]){display:block}
 .scene{border-bottom:1px solid var(--line);padding:22px 32px 26px;scroll-margin-top:96px}
 .sh{display:flex;align-items:baseline;gap:12px;margin-bottom:10px;flex-wrap:wrap}
 .sh h2{margin:0;font-size:18px;font-weight:600}
 .num{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--acc);font-weight:700}
 .sh .t{color:var(--mut);font-size:13px;margin-left:auto}
 .sbody{display:grid;grid-template-columns:1.4fr 1fr 1.2fr;gap:18px;background:var(--pan);
   border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px}
 .lbl{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin-bottom:4px}
 .lbl em{font-style:normal;opacity:.6;text-transform:none;letter-spacing:0}
 .rate{font-size:12px;color:var(--mut);margin-top:4px} .rate.over{color:#c2571a;font-weight:600}
 .was{font-size:12px;color:var(--mut);margin-top:4px;display:none} .changed .was{display:block}
 .was button{font-size:11px;padding:1px 6px;margin-left:6px}
 .und p{margin:0;color:var(--mut);font-size:13px}
 textarea.ed{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;
   padding:6px 8px;font:inherit;resize:vertical}
 textarea.ed:focus{outline:none;border-color:var(--acc)}
 textarea.ed.q{font-size:16px;line-height:1.4} textarea.ed.c{font-weight:600}
 .changed textarea.ed,textarea.ed.has{border-color:var(--acc);background:color-mix(in srgb,var(--acc) 7%,var(--bg))}
 .snote{margin-bottom:16px}
 .shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
 .shot{margin:0;border:2px solid var(--line);border-radius:9px;overflow:hidden;background:var(--pan)}
 .shot.reuse .pic{opacity:.6}
 .pic{position:relative;aspect-ratio:16/9;background:#000;cursor:zoom-in}
 .pic img{width:100%;height:100%;object-fit:cover;display:block}
 .paper .pic{display:none}   /* no frames anywhere yet: the plan on paper, without 85 black boxes */
 .np{position:absolute;inset:0;display:grid;place-items:center;color:var(--mut);font-size:12px;cursor:default}
 .badge{position:absolute;left:6px;bottom:6px;font-size:10px;padding:2px 7px;border-radius:99px;background:#000a;color:#fff;
   letter-spacing:.03em;text-decoration:none}
 .badge.ui{background:var(--keep)} a.badge.todo{background:#8a6d2f} a.badge.todo:hover{background:#a3822f}
 figcaption{padding:8px 10px} figcaption p{margin:3px 0 0;font-size:13px}
 figcaption .t{color:var(--mut);font-size:12px;margin-left:6px}
 .scr{color:var(--acc);font-size:12px!important} .cut{color:var(--mut);font-size:12px!important}
 .acts{display:flex;gap:4px;margin-top:7px}
 .acts .d{flex:1;padding:4px 2px;font-size:11.5px;border-radius:5px}
 .acts .d.on[data-d=keep]{background:var(--keep);border-color:var(--keep);color:#fff}
 .acts .d.on[data-d=change]{background:var(--change);border-color:var(--change);color:#fff}
 .acts .d.on[data-d=redo]{background:var(--redo);border-color:var(--redo);color:#fff}
 .acts .d.on[data-d=cut]{background:var(--cut);border-color:var(--cut);color:#fff}
 .shot.dec-keep{border-color:var(--keep)} .shot.dec-change{border-color:var(--change)}
 .shot.dec-redo{border-color:var(--redo)} .shot.dec-cut{border-color:var(--cut)} .shot.dec-cut .pic{opacity:.4}
 .shot.need-note .shotnote{border-color:#c2571a}
 .shotnote{margin-top:6px;font-size:13px;min-height:30px}
 .hide{display:none!important}
 #lb{position:fixed;inset:0;z-index:30;background:#000e;display:none;flex-direction:column;align-items:center;justify-content:center;padding:16px}
 #lb.on{display:flex} #lb img{max-width:100%;max-height:calc(100vh - 130px);border-radius:6px}
 #lb .cap{color:#e9ebee;margin-top:10px;text-align:center;font-size:14px;max-width:1000px}
 #lb .cap small{color:#9aa3ad;display:block;margin-top:2px}
 #lb .acts{max-width:420px;width:100%;margin-top:10px} #lb .acts .d{background:#1c1f24;color:#e9ebee;border-color:#2b3037;padding:7px 2px}
 #lb .x{position:absolute;top:14px;right:18px;background:#1c1f24;color:#e9ebee;border-color:#2b3037}
 #cp{position:fixed;inset:0;z-index:40;background:#000c;display:none;align-items:center;justify-content:center;padding:24px}
 #cp.on{display:flex} #cp div{background:var(--bg);border-radius:10px;padding:16px;width:min(760px,100%)}
 #cp textarea{width:100%;height:50vh;font:13px/1.45 ui-monospace,monospace;background:var(--pan);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:10px}
 kbd{background:var(--pan);border:1px solid var(--line);border-radius:4px;padding:0 5px;font:12px ui-monospace,monospace}
 @media (max-width:900px){.sbody{grid-template-columns:1fr;gap:12px} .sh .t{margin-left:0;width:100%}
   .scene{padding:18px 16px 20px} header{padding:18px 16px 10px} .bar{padding:8px 16px}}
 @media print{.bar,.acts,#warn,#orph,header button{display:none!important} .shot{break-inside:avoid}
   textarea.ed{border:0;resize:none;padding:0;background:none}}
'''

JS = r'''
'use strict';
// Review layer. Decisions and notes per shot; a note, the voice-over and the on-screen copy per scene.
// Kept in the browser as you type, carried out as JSON, because notes are only worth making if they
// survive a refresh and reach the person who acts on them.
const KEY = window.SB.key;        // one key per project, so two films on one server never share notes
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
let D = {shots:{}, scenes:{}}, canSave = true;
try { localStorage.setItem(KEY+'-probe','1'); localStorage.removeItem(KEY+'-probe');
      D = JSON.parse(localStorage.getItem(KEY) || 'null') || D; } catch(e) { canSave = false; }
D.shots = D.shots || {}; D.scenes = D.scenes || {};

// A note belongs to a shot AND its frame. Keyed by the shot number alone, reordering a scene would
// silently move every note onto a different picture, so the key is "shot|plate".
const cards = $$('.shot'), keyOf = f => f.dataset.shot + '|' + f.dataset.plate;
const live = new Set(cards.map(keyOf));
// Notes follow the picture. A note written under the old key (shot number only), or under a shot
// number that has since moved, is re-attached to the card that now carries its frame.
function adopt(){
  Object.keys(D.shots).forEach(k => {
    if (live.has(k)) return;
    const rec = D.shots[k], bar = k.indexOf('|');
    const shot = bar < 0 ? k : k.slice(0, bar), plate = bar < 0 ? rec.plate : k.slice(bar + 1);
    let f = cards.find(c => c.dataset.shot === shot && (!plate || plate === c.dataset.plate));
    if (!f && plate) { const same = cards.filter(c => c.dataset.plate === plate && !c.classList.contains('reuse'));
                       if (same.length === 1) f = same[0]; }
    const to = f ? keyOf(f) : shot + '|' + (plate || '?');
    if (to === k || D.shots[to]) return;                         // never overwrite a note already there
    D.shots[to] = rec; delete D.shots[k];
  });
}
adopt();
const orphans = () => Object.keys(D.shots).filter(k => !live.has(k) && (D.shots[k].decision || D.shots[k].note));

let timer = null, dirty = false;
function write(){ clearTimeout(timer); dirty = false; try { localStorage.setItem(KEY, JSON.stringify(D)); } catch(e){} }
const save = () => { dirty = true; clearTimeout(timer); timer = setTimeout(write, 250); };
// The last quarter-second of typing must not be lost to a closed tab — but only a tab with unsaved
// changes may write on the way out, or an old tab would overwrite the newer notes of another one.
const flush = () => { if (dirty) write(); };
addEventListener('pagehide', flush); document.addEventListener('visibilitychange', () => { if (document.hidden) flush(); });
// and when another tab saves, take its version rather than keep a stale one
addEventListener('storage', e => { if (e.key !== KEY || dirty || !e.newValue) return;
  try { const d = JSON.parse(e.newValue); D.shots = d.shots || {}; D.scenes = d.scenes || {}; adopt(); paintAll(); } catch(err){} });

const shotRec = k => D.shots[k] || (D.shots[k] = {});
const sceneRec = n => D.scenes[n] || (D.scenes[n] = {});
const fit = t => { if (t.classList.contains('shotnote')) { t.style.height = 'auto'; t.style.height = (t.scrollHeight + 2) + 'px'; } };

// ---- shots -------------------------------------------------------------------------------------
function paintShot(f){
  const rec = D.shots[keyOf(f)] || {}, dec = rec.decision;
  f.className = f.className.replace(/ (dec-\w+|need-note)/g, '') + (dec ? ' dec-' + dec : '')
    + ((dec === 'change' || dec === 'redo') && !rec.note ? ' need-note' : '');   // "change" with no note says nothing
  f.querySelectorAll('.d').forEach(b => b.classList.toggle('on', b.dataset.d === dec));
  const t = f.querySelector('.shotnote');
  if (document.activeElement !== t) { t.value = rec.note || ''; fit(t); }
  t.classList.toggle('has', !!rec.note);
  t.placeholder = dec === 'change' ? 'What should change?' : dec === 'redo' ? 'What was wrong with this one?'
    : dec === 'cut' ? 'Why cut it? (optional)' : 'What to change, or why.';
}
function decide(f, d){
  const rec = shotRec(keyOf(f));
  if (rec.decision === d) delete rec.decision; else rec.decision = d;
  rec.shot = f.dataset.shot; rec.plate = f.dataset.plate; rec.desc = f.dataset.desc;
  if (!rec.decision && !rec.note) delete D.shots[keyOf(f)];
  save(); paintShot(f); recount(); applyFilter();
  if ((d === 'change' || d === 'redo') && rec.decision && !rec.note && !$('#lb').classList.contains('on'))
    f.querySelector('.shotnote').focus();
}
cards.forEach(f => {
  f.querySelectorAll('.d').forEach(b => b.onclick = () => decide(f, b.dataset.d));
  const t = f.querySelector('.shotnote');
  t.addEventListener('input', () => { const rec = shotRec(keyOf(f));
    if (t.value.trim()) rec.note = t.value; else delete rec.note;
    rec.shot = f.dataset.shot; rec.plate = f.dataset.plate; rec.desc = f.dataset.desc;
    if (!rec.decision && !rec.note) delete D.shots[keyOf(f)];
    fit(t); save(); paintShot(f); recount(); });
});

// ---- scenes ------------------------------------------------------------------------------------
// Voice-over and copy start as the brief's text. Only a real difference is stored, and an emptied
// field is stored as "" — a deliberate removal, not "no change".
function paintField(t){
  const n = t.dataset.scene, k = t.dataset.k, rec = D.scenes[n] || {}, box = t.closest('.fld');
  if (k === 'note') { if (document.activeElement !== t) t.value = rec.note || ''; t.classList.toggle('has', !!rec.note); return; }
  const changed = rec[k] !== undefined;
  if (document.activeElement !== t) t.value = changed ? rec[k] : t.defaultValue;
  box.classList.toggle('changed', changed);
  if (k === 'vo') rate(t);
}
function rate(t){
  const el = t.closest('.fld').querySelector('.rate'), secs = +t.dataset.secs;
  const words = (t.value.trim().match(/\S+/g) || []).length;
  if (!words) { el.textContent = 'no narration · ' + secs + ' s of location sound'; el.classList.remove('over'); return; }
  const r = words / secs;
  el.textContent = words + ' words over ' + secs + ' s = ' + r.toFixed(1) + ' per second' + (r > 2.5 ? ' — too fast to read comfortably (aim for 2–2.5)' : '');
  el.classList.toggle('over', r > 2.5);
}
$$('textarea[data-scene]').forEach(t => {
  t.addEventListener('input', () => { const rec = sceneRec(t.dataset.scene), k = t.dataset.k;
    if (k === 'note') { if (t.value.trim()) rec.note = t.value; else delete rec.note; }
    else if (t.value === t.defaultValue) delete rec[k]; else rec[k] = t.value;
    if (!Object.keys(rec).length) delete D.scenes[t.dataset.scene];
    save(); paintField(t); recount(); });
});
$$('.was button').forEach(b => b.onclick = () => { const t = b.closest('.fld').querySelector('textarea');
  const rec = sceneRec(t.dataset.scene); delete rec[t.dataset.k];
  if (!Object.keys(rec).length) delete D.scenes[t.dataset.scene];
  t.value = t.defaultValue; save(); paintField(t); recount(); });

// ---- filter, counts, index ---------------------------------------------------------------------
let filter = 'all';
function applyFilter(){
  cards.forEach(f => { const dec = (D.shots[keyOf(f)] || {}).decision;
    f.classList.toggle('hide', !(filter === 'all' || (filter === 'none' ? !dec : dec === filter))); });
  $$('.scene').forEach(sc => sc.classList.toggle('hide',
    filter !== 'all' && ![...sc.querySelectorAll('.shot')].some(f => !f.classList.contains('hide'))));
}
$$('button.f').forEach(b => b.onclick = () => { $$('button.f').forEach(x => x.classList.toggle('on', x === b)); filter = b.dataset.f; applyFilter(); });
function recount(){
  const c = {keep:0, change:0, redo:0, cut:0}; let notes = 0;
  cards.forEach(f => { const r = D.shots[keyOf(f)]; if (!r) return; if (r.decision) c[r.decision]++; if (r.note) notes++; });
  Object.values(D.scenes).forEach(r => { notes += ['note','vo','copy'].filter(k => r[k] !== undefined).length; });
  const decided = c.keep + c.change + c.redo + c.cut;
  $('#count').textContent = decided + ' of ' + cards.length + ' decided · keep ' + c.keep + ' · change ' + c.change
    + ' · regenerate ' + c.redo + ' · cut ' + c.cut + ' · ' + notes + ' notes';
  $$('.scene').forEach(sc => { const fs = [...sc.querySelectorAll('.shot')], n = fs.filter(f => (D.shots[keyOf(f)] || {}).decision).length;
    const a = $('.idx a[href="#' + sc.id + '"]'); if (a) a.className = n === fs.length ? 'all' : n ? 'some' : ''; });
  const o = orphans(); $('#orph').hidden = !o.length;
  if (o.length) $('#orphText').textContent = o.length + ' note' + (o.length > 1 ? 's refer' : ' refers')
    + ' to shots that are no longer in the storyboard (' + o.map(k => k.replace('|', ' · ')).join(', ') + '). They are kept and exported.';
}

// ---- looking closely -----------------------------------------------------------------------------
let lbAt = -1;
function openLb(i){
  const vis = cards.filter(f => !f.classList.contains('hide') && f.querySelector('.pic').dataset.full);
  if (!vis.length) return; lbAt = (i + vis.length) % vis.length; const f = vis[lbAt];
  $('#lbImg').src = f.querySelector('.pic').dataset.full;
  $('#lbCap').innerHTML = '<b>' + f.dataset.shot + '</b> · ' + f.querySelector('.t').textContent
    + '<small>' + f.dataset.desc.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])) + '</small>';
  const dec = (D.shots[keyOf(f)] || {}).decision;
  $$('#lb .d').forEach(b => { b.classList.toggle('on', b.dataset.d === dec); b.onclick = () => { decide(f, b.dataset.d); openLb(lbAt); }; });
  $('#lb').classList.add('on'); document.body.classList.add('locked'); $('#lb').dataset.key = keyOf(f);
}
function closeLb(){ $('#lb').classList.remove('on'); document.body.classList.remove('locked');
  const f = cards.find(c => keyOf(c) === $('#lb').dataset.key); if (f) f.scrollIntoView({block:'center'}); }
cards.forEach(f => { const p = f.querySelector('.pic'); if (p.dataset.full) p.onclick = e => { if (e.target.closest('a')) return;
  openLb(cards.filter(c => !c.classList.contains('hide') && c.querySelector('.pic').dataset.full).indexOf(f)); }; });
$('#lb .x').onclick = closeLb; $('#lb').onclick = e => { if (e.target.id === 'lb') closeLb(); };

// ---- keyboard ----------------------------------------------------------------------------------
let hover = null;
document.addEventListener('mouseover', e => { const f = e.target.closest('.shot'); if (f) hover = f; });
document.addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;       // Cmd+R must reload, not mark "regenerate"
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { if (e.key === 'Escape') document.activeElement.blur(); return; }
  const lb = $('#lb').classList.contains('on'), map = {k:'keep', c:'change', r:'redo', x:'cut'};
  if (lb && e.key === 'Escape') return closeLb();
  if (lb && e.key === 'ArrowRight') return openLb(lbAt + 1);
  if (lb && e.key === 'ArrowLeft') return openLb(lbAt - 1);
  if ($('#cp').classList.contains('on') && e.key === 'Escape') return $('#cp').classList.remove('on');
  if (map[e.key]) { const f = lb ? cards.find(c => keyOf(c) === $('#lb').dataset.key) : hover;
    if (f) { decide(f, map[e.key]); if (lb) openLb(lbAt); } }
});

// ---- carrying the work out -----------------------------------------------------------------------
function payload(){
  const out = {film:window.SB.film, saved:new Date().toISOString(), shots:[], scenes:[], orphans:[]};
  cards.forEach(f => { const r = D.shots[keyOf(f)]; if (r && (r.decision || r.note))
    out.shots.push({shot:f.dataset.shot, plate:f.dataset.plate, description:f.dataset.desc, decision:r.decision || null, note:r.note || null}); });
  $$('.scene').forEach(sc => { const n = sc.dataset.scene, r = D.scenes[n]; if (!r) return; const o = {scene:n, title:sc.dataset.title};
    if (r.note) o.note = r.note;
    ['vo','copy'].forEach(k => { if (r[k] !== undefined) o[k] = {was: sc.querySelector('textarea[data-k="' + k + '"]').defaultValue, now: r[k]}; });
    out.scenes.push(o); });
  orphans().forEach(k => out.orphans.push(Object.assign({key:k}, D.shots[k])));
  return out;
}
function asText(){
  const p = payload(), L = ['Storyboard notes — ' + p.saved.slice(0,16).replace('T',' ')];
  [['cut','CUT'],['redo','REGENERATE'],['change','CHANGE'],[null,'NOTE ONLY'],['keep','KEEP']].forEach(([d, label]) => {
    const list = p.shots.filter(s => s.decision === d); if (!list.length) return;
    L.push('', label + ' (' + list.length + ')');
    if (d === 'keep') { L.push('  ' + list.map(s => s.shot).join(', ')); list.filter(s => s.note).forEach(s => L.push('  ' + s.shot + ' — ' + s.note)); }
    else list.forEach(s => L.push('  ' + s.shot + ' · ' + s.plate + (s.note ? ' — ' + s.note : '  (no note)')));
  });
  if (p.scenes.length) { L.push('', 'SCENES');
    p.scenes.forEach(s => { if (s.note) L.push('  Scene ' + s.scene + ' — ' + s.note);
      if (s.vo) L.push('  Scene ' + s.scene + ' · voice-over ' + (s.vo.now ? 'becomes: “' + s.vo.now + '”' : 'REMOVED') + '  (was: “' + s.vo.was + '”)');
      if (s.copy) L.push('  Scene ' + s.scene + ' · on-screen copy ' + (s.copy.now ? 'becomes: ' + s.copy.now.replace(/\n/g,' / ') : 'REMOVED') + '  (was: ' + s.copy.was.replace(/\n/g,' / ') + ')'); }); }
  if (p.orphans.length) { L.push('', 'NOTES ON SHOTS NO LONGER IN THE STORYBOARD');
    p.orphans.forEach(o => L.push('  ' + o.key.replace('|',' · ') + (o.decision ? ' [' + o.decision + ']' : '') + (o.note ? ' — ' + o.note : ''))); }
  return p.shots.length + p.scenes.length + p.orphans.length ? L.join('\n') : 'No notes yet.';
}
$('#exp').onclick = () => { write(); const d = new Date(), z = n => String(n).padStart(2,'0');
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(payload(), null, 1)], {type:'application/json'}));
  a.download = 'storyboard-notes-' + d.getFullYear() + z(d.getMonth()+1) + z(d.getDate()) + '-' + z(d.getHours()) + z(d.getMinutes()) + '.json';
  a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); };
$('#copy').onclick = () => { const text = asText(), done = () => { $('#copy').textContent = 'Copied'; setTimeout(() => $('#copy').textContent = 'Copy for Claude', 1400); };
  const manual = () => { $('#cpText').value = text; $('#cp').classList.add('on'); $('#cpText').focus(); $('#cpText').select(); };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, manual); else manual(); };
$('#cpClose').onclick = () => $('#cp').classList.remove('on');
$('#imp').onclick = () => $('#file').click();
$('#file').onchange = e => { const f = e.target.files[0]; if (!f) return; const r = new FileReader();
  r.onload = () => { try { const d = JSON.parse(r.result);
      (Array.isArray(d.shots) ? d.shots : []).forEach(s => { if (!s.shot) return; const rec = shotRec(s.shot + '|' + s.plate);
        if (s.decision) rec.decision = s.decision; if (s.note) rec.note = s.note; rec.shot = s.shot; rec.plate = s.plate; rec.desc = s.description; });
      (Array.isArray(d.scenes) ? d.scenes : []).forEach(s => { const rec = sceneRec(s.scene);
        if (s.note) rec.note = s.note; ['vo','copy'].forEach(k => { if (s[k]) rec[k] = s[k].now; }); });
      (Array.isArray(d.orphans) ? d.orphans : []).forEach(o => { if (!o.key || D.shots[o.key]) return;
        const rec = Object.assign({}, o); delete rec.key; D.shots[o.key] = rec; });
      adopt(); write(); paintAll();
    } catch(err) { alert('That is not a storyboard-notes file: ' + err.message); } };
  r.readAsText(f); e.target.value = ''; };

function paintAll(){ cards.forEach(paintShot); $$('textarea[data-scene]').forEach(paintField); recount(); applyFilter(); }
addEventListener('scroll', () => { try { sessionStorage.setItem(KEY+'-y', String(scrollY)); } catch(e){} }, {passive:true});
$('#warn').hidden = canSave;
paintAll();
try { const y = +sessionStorage.getItem(KEY+'-y'); if (y && !location.hash) scrollTo(0, y); } catch(e){}
'''


def main():
    ap = argparse.ArgumentParser(description='Build storyboard.html for a film project.')
    ap.add_argument('--project', default='.', help='the film project folder (default: here)')
    ap.add_argument('--title', help='film name; default: the first heading of plan.md, else the folder name')
    ap.add_argument('--open', action='store_true', help='open the page when it is built')
    a = ap.parse_args()
    os.chdir(a.project)
    if not os.path.exists('shotlist.csv'):
        sys.exit('no shotlist.csv here — the storyboard is built from the shot list')

    title = a.title
    if not title and os.path.exists('plan.md'):
        m = re.search(r'^#\s+(.+)$', open('plan.md', encoding='utf-8').read(), re.M)
        title = re.split(r'\s+[—–|:]\s+', m.group(1).strip())[0] if m else None
    title = title or os.path.basename(os.getcwd()).replace('-', ' ').replace('_', ' ').title()
    # Notes live in the browser per address. Every project served from localhost:8788 shares one
    # address, so the key carries the project's own path.
    key = 'storyboard-notes:' + hashlib.sha1(os.getcwd().encode()).hexdigest()[:10]

    scenes, screens = read_scenes(), screens_by_plate()
    has_corners = os.path.exists('ui/corners.html')
    rows = [r for r in csv.DictReader(open('shotlist.csv', encoding='utf-8-sig')) if (r.get('scene') or '').strip()]
    if not rows:
        sys.exit('shotlist.csv has no rows yet')

    by_scene = {}
    for r in rows:
        by_scene.setdefault(r['scene'].strip(), []).append(r)

    first_shot_of = {}                    # plate -> the shot that owns the frame, for "reuses 2.2"
    parts, index = [], []
    n_frames = n_comp = 0
    for sc, srows in by_scene.items():
        s = scenes.get(sc, {})
        t0, t1 = num(srows[0].get('film_in')), num(srows[-1].get('film_out'))
        secs = round(t1 - t0, 2)
        index.append(f'<a href="#scene-{esc(sc)}" title="{esc(s.get("title", ""))}">{esc(sc)}</a>')
        shots = []
        for r in srows:
            plate = (r.get('start_keyframe') or '').strip()
            sid = f"{sc}.{(r.get('shot') or '').strip()}"
            thumb, full, comp = pictures_for(plate) if plate else (None, None, False)
            owner = first_shot_of.get(plate) if plate else None
            reuse = owner is not None
            if plate and not reuse:
                first_shot_of[plate] = sid
            if thumb:
                n_frames += 1
            if comp and not reuse:
                n_comp += 1
            scr = screens.get(plate, []) if not reuse else []
            dur = num(r.get('film_out')) - num(r.get('film_in'))
            if comp:
                badge = '<span class="badge ui">interface placed</span>'
            elif scr and has_corners:
                badge = f'<a class="badge todo" href="ui/corners.html#{esc(plate)}" title="Place it">interface pending →</a>'
            elif scr:
                badge = '<span class="badge">interface pending</span>'
            else:
                badge = ''
            pic = (f'<div class="pic" data-full="{esc(full)}"><img loading="lazy" src="{esc(thumb)}" alt="">{badge}</div>'
                   if thumb else f'<div class="pic"><div class="np">no frame yet</div>{badge}</div>')
            model = (r.get('model') or '').strip()
            shots.append(f"""<figure class="shot{' reuse' if reuse else ''}" data-shot="{esc(sid)}" data-plate="{esc(plate)}" data-desc="{esc(r.get('description'))}">
      {pic}
      <figcaption>
        <b>{esc(sid)}</b><span class="t">{esc(r.get('film_in'))}–{esc(r.get('film_out'))} s · {dur:.1f} s</span>
        <p>{esc(r.get('description'))}</p>
        {'<p class="scr">Screen: ' + esc(' + '.join(scr)) + '</p>' if scr else ''}
        <p class="cut">{esc(r.get('cut_note'))}{' · reuses the frame of ' + esc(owner) if reuse else ''}{' · made in the edit' if model == 'post' and not reuse else ''}</p>
        <div class="acts">
          <button class="d" data-d="keep" title="Keep as it is (k)">Keep</button>
          <button class="d" data-d="change" title="Keep the shot, change something (c)">Change</button>
          <button class="d" data-d="redo" title="Same idea, generate it again (r)">Regenerate</button>
          <button class="d" data-d="cut" title="Drop this shot (x)">Cut</button>
        </div>
        <textarea class="ed shotnote" rows="1" placeholder="What to change, or why."></textarea>
      </figcaption>
    </figure>""")
        und = (f'<div class="und"><span class="lbl">What the viewer must understand</span><p>{esc(s.get("understand"))}</p></div>'
               if s.get('understand') else '<div class="und"></div>')
        parts.append(f"""<section class="scene" id="scene-{esc(sc)}" data-scene="{esc(sc)}" data-title="{esc(s.get('title', ''))}">
  <div class="sh"><span class="num">Scene {esc(sc)}</span><h2>{esc(s.get('title', ''))}</h2>
    <span class="t">{t0:g} – {t1:g} s · {secs:g} s</span></div>
  <div class="sbody">
    <div class="fld"><span class="lbl">Voice-over <em>· editable</em></span>
      <textarea class="ed q" data-k="vo" data-scene="{esc(sc)}" data-secs="{secs:g}" rows="2" placeholder="none — location sound only">{esc(s.get('vo', ''))}</textarea>
      <div class="rate"></div>
      <div class="was">was: “{esc(s.get('vo', '')) or 'none'}” <button type="button">restore</button></div></div>
    <div class="fld"><span class="lbl">On screen <em>· editable</em></span>
      <textarea class="ed c" data-k="copy" data-scene="{esc(sc)}" rows="2" placeholder="—">{esc(s.get('copy', ''))}</textarea>
      <div class="was">was: {esc(s.get('copy', '')) or 'none'} <button type="button">restore</button></div></div>
    {und}
  </div>
  <div class="snote fld"><span class="lbl">Notes on this scene</span>
    <textarea class="ed" data-k="note" data-scene="{esc(sc)}" rows="2" placeholder="Anything about the scene as a whole: pacing, the order of the shots, what is missing."></textarea></div>
  <div class="shots">
    {''.join(shots)}
  </div>
</section>
""")

    total = max(num(r.get('film_out')) for r in rows)
    nav = '<a class="nav" href="ui/corners.html">place the screens →</a>' if has_corners else ''
    stage = (f'{n_frames} frames · {n_comp} with the interface composited' if n_frames
             else 'no frames yet — this is the plan on paper: check the order, the timings and what is said')
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Storyboard — {esc(title)}</title>\n<style>' + CSS + '</style>\n'
            + ('<body class="paper">\n' if not n_frames else '<body>\n')
            + f"""<header>
 <div class="hrow"><h1>{esc(title)} — storyboard</h1>
  {nav}<span class="grow"></span>
  <button id="imp">Import notes</button><button id="copy">Copy for Claude</button><button class="p" id="exp">Download notes</button>
  <input type="file" id="file" accept="application/json,.json" hidden></div>
 <p class="sub">{len(rows)} shots · {total:g} s · {stage}. Narration and on-screen copy are laid in the edit.
 Click a frame to see it large. Hover a shot and press <kbd>k</kbd> keep · <kbd>c</kbd> change · <kbd>r</kbd> regenerate · <kbd>x</kbd> cut.</p>
</header>
<div class="bar">
 <div class="hrow"><span class="lbl2">Show</span>
  <button class="f on" data-f="all">All</button><button class="f" data-f="none">Undecided</button>
  <button class="f" data-f="keep">Keep</button><button class="f" data-f="change">Change</button>
  <button class="f" data-f="redo">Regenerate</button><button class="f" data-f="cut">Cut</button>
  <span class="grow"></span><span class="sub" id="count" style="margin:0"></span></div>
 <div class="idx"><span class="lbl2" style="margin-right:4px">Scene</span>{''.join(index)}</div>
</div>
<div id="warn" hidden>This page cannot save notes where it is open now — open it in a browser, or use Import and Download to carry your work.</div>
<div id="orph" hidden><span id="orphText"></span></div>
"""
            + ''.join(parts)
            + """<div id="lb"><button class="x">Close · esc</button><img id="lbImg" alt=""><div class="cap" id="lbCap"></div>
 <div class="acts"><button class="d" data-d="keep">Keep · k</button><button class="d" data-d="change">Change · c</button>
 <button class="d" data-d="redo">Regenerate · r</button><button class="d" data-d="cut">Cut · x</button></div>
 <div class="cap"><small>← → to move between shots</small></div></div>
<div id="cp"><div><p style="margin:0 0 8px">The clipboard is not available here. Select all and copy:</p>
 <textarea id="cpText" readonly></textarea><p style="margin:8px 0 0;text-align:right"><button id="cpClose">Close</button></p></div></div>
<script>window.SB = """ + json.dumps({'key': key, 'film': title}).replace('</', '<\\/') + ';</script>\n<script>' + JS + '</script>\n')
    open('storyboard.html', 'w', encoding='utf-8').write(page)
    print(f'storyboard.html: {len(rows)} shots, {len(by_scene)} scenes, {n_frames} frames, {n_comp} composited'
          + ('' if scenes else ' · no scenes.csv, so no voice-over or copy yet'))
    print(os.path.abspath('storyboard.html'))
    if a.open:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath('storyboard.html'))


if __name__ == '__main__':
    main()
