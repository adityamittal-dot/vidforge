"""Real historical visuals: paintings, photographs, maps and artefacts from the Wikipedia articles a script is about,
plus a Wikimedia Commons file search per line (MediaWiki API), with an AI image (images.py) only as the last resort.
Only freely licensed files are used (public domain, CC0, CC BY, CC BY-SA); every file shown is recorded in CREDITS
so the pipeline can publish per-image attribution.

The writer can check files with the CLI:
  python visuals.py search en.wikipedia.org "Piri Reis map"
  python visuals.py check en.wikipedia.org "File:Piri reis world map 01.jpg"
"""
import argparse, io, json, os, re, time
import requests
from PIL import Image


UA = {"User-Agent": "vidforge/1.0 (+https://github.com/adityamittal-dot/vidforge)"}
# Wikipedia/Commons clutter: icons, flags, locator maps, charts, diagrams, scans of text, modern tourist snaps
BAD = re.compile(r"logo|icon|\bflag of\b|coat of arms|locator|location map|\borthographic\b|relief map|"
                 r"\bchart\b|\bgraph\b|diagram|\btimeline\b|signature|\bstub\b|\bbanner\b|button|commons-|wiki|"
                 r"disambig|symbol|pictogram|\bseal of\b|qr code|screenshot|selfie|\.gif$|\.svg$|\.tiff?$|\.pdf$|"
                 r"\.djvu$", re.I)
EXTS = (".png", ".jpg", ".jpeg", ".webp")
# Licences that allow reuse in a monetised video with attribution; anything else (NC, ND, fair use) is skipped.
FREE = re.compile(r"public domain|^pd|cc0|cc[- ]by(-sa)?[- ]\d|cc[- ]by(-sa)?$|gfdl|no restrictions|attribution", re.I)
NONFREE = re.compile(r"\bnc\b|non-?commercial|\bnd\b|no ?deriv|fair use|non-free|copyrighted", re.I)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "channel.json"), encoding="utf-8") as _f:
    _CH = json.load(_f)
# AI-fallback picture style (channel.json "image_style")
ANIME_STYLE = _CH.get("image_style", "detailed historical illustration, no text, no watermark")
EXTMETA = "LicenseShortName|Artist|Credit|ObjectName"
CREDITS = {}   # {file title: {"artist", "license", "url"}} for every file a video showed


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", str(html or ""))).strip()[:120]


def credit_of(t, i):
    m = i.get("extmetadata") or {}
    return {"artist": _plain(m.get("Artist", {}).get("value")) or "unknown",
            "license": _plain(m.get("LicenseShortName", {}).get("value")) or "see file page",
            "url": i.get("descriptionurl", "")}


def _record(t, i):
    CREDITS[t] = credit_of(t, i)


def _search_host(wiki):
    """Wikipedia articles hold few pictures each; the file search runs on Wikimedia Commons (millions of files)."""
    return "commons.wikimedia.org" if wiki.endswith("wikipedia.org") else wiki


def _api(wiki, **params):
    host = wiki.split('://')[-1].strip('/')
    url = f"https://{host}/w/api.php" if host.endswith(("wikipedia.org", "wikimedia.org")) else f"https://{host}/api.php"
    for attempt in range(3):
        try:
            r = requests.get(url, params={"format": "json", **params}, headers=UA, timeout=60)
            time.sleep(0.3)                                  # be polite to the wiki
            if r.ok:
                return r.json()
        except (requests.RequestException, ValueError):
            pass
        time.sleep(1.5 * (attempt + 1))
    return {}


def _title(t):
    t = t.strip().replace("_", " ")
    return t if t.startswith(("File:", "Image:")) else "File:" + t


def info(wiki, titles):
    """{title: {"url", "width", "height"}} for up to 30 file titles."""
    pages = _api(wiki, action="query", prop="imageinfo", iiprop="url|size|extmetadata", iiextmetadatafilter=EXTMETA,
                 iiurlwidth=2400, titles="|".join(titles[:30])).get("query", {}).get("pages", {})
    return {p["title"]: p["imageinfo"][0] for p in pages.values() if p.get("imageinfo")}


def search(wiki, words, limit=30):
    """File titles for `words`, best first. Commons search needs every word to match, so a long query that finds
    nothing is retried with its first 3, then first 2 words ("Roman legionary winter camp" -> "Roman legionary")."""
    ws, out = words.split(), []
    for n in [len(ws)] + [k for k in (3, 2) if k < len(ws)]:
        hits = _api(_search_host(wiki), action="query", list="search", srnamespace=6, srsearch=" ".join(ws[:n]),
                    srlimit=min(limit, 50)).get("query", {}).get("search", [])
        out += [h["title"] for h in hits if h["title"] not in out and h["title"].lower().endswith(EXTS)]
        if len(out) >= 10:
            break
    return out[:limit]


# Violent/graphic frames get videos ad-limited (2026-10-09-L used the bloody Baratie chest slash): never use files
# whose name points at blood, wounds, deaths or executions, whatever the shot search asked for.
GORE = re.compile(r"blood|bleed|wound|injur|corpse|dead\b|death|dies\b|died|dying|killed|kills\b|murder|execut|"
                  r"stab|impale|sever|decapitat|behead|gore\b|torture|massacre|slaughter|suicide|funeral|grave\b|"
                  r"cut down|struck down|slashe[sd]|pierc|skewer|scar\b|scarred|vomit|carnage", re.I)
MERCH = re.compile(r"^(File:|Image:)?[^ ]+-[^ ]+\.\w+$")    # "DXGLM9-Zoro.png", "POPSailingAgain-Zoro.png": product shots


def free_licence(i):
    """True for files whose licence allows reuse with attribution (Commons/Wikipedia extmetadata). Wikis without
    licence metadata (Fandom) pass."""
    m = i.get("extmetadata")
    if not m:
        return True
    lic = _plain(m.get("LicenseShortName", {}).get("value"))
    return bool(lic) and bool(FREE.search(lic)) and not NONFREE.search(lic)


def acceptable(title, i):
    return (title.lower().endswith(EXTS) and not BAD.search(title) and not GORE.search(title)
            and free_licence(i)
            and i.get("width", 0) >= 600 and i.get("height", 0) >= 400)


def _url(i):
    """A <=2400 px rendition when the API offers one (Commons originals can be 100+ MB scans)."""
    return i.get("thumburl") or i["url"]


def _download(url, out):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.ok:
                im = Image.open(io.BytesIO(r.content))
                if im.mode in ("RGBA", "LA", "P"):
                    im = im.convert("RGBA")
                    bg = Image.new("RGB", im.size)
                    bg.paste(im, mask=im.split()[3])
                    im = bg
                im.convert("RGB").save(out, "JPEG", quality=92)
                if os.path.getsize(out) > 5000:
                    return True
        except Exception as e:
            print(f"  download failed ({e})", flush=True)
        time.sleep(1.5 * (attempt + 1))
    return False


def page_images(wiki, page):
    """{file title: imageinfo} for every acceptable image used on a wiki article (fight, arc, character pages)."""
    out, cont = {}, {}
    for _ in range(4):
        r = _api(wiki, action="query", titles=page, generator="images", gimlimit=200, prop="imageinfo",
                 iiprop="url|size|extmetadata", iiextmetadatafilter=EXTMETA, iiurlwidth=2400, redirects=1, **cont)
        for p in r.get("query", {}).get("pages", {}).values():
            if p.get("imageinfo") and acceptable(p["title"], p["imageinfo"][0]):
                out[p["title"]] = p["imageinfo"][0]
        cont = r.get("continue", {})
        if not cont:
            break
    return out


def script_pages(script):
    """Wiki articles the Short is about: the writer's "pages", plus every source URL on the same wiki."""
    from urllib.parse import unquote, urlparse
    wiki = script.get("wiki", "")
    pages = list(script.get("pages") or [])
    for u in script.get("sources", []):
        p = urlparse(u)
        if wiki and p.netloc.endswith(wiki) and p.path.startswith("/wiki/"):
            pages.append(unquote(p.path[6:]).replace("_", " "))
    return list(dict.fromkeys(t for t in pages if t and not t.startswith(("Special:", "Category:"))))


STOP = set("""a an and are as at be but by for from had has have he her his i if in into is it its just me my no not
of on or our over she so than that the their them then there these they this to up was we were what when which who why
will with you your file png jpg jpeg webp image picture photo vs""".split())
DULL = re.compile(r"infobox|\bpage \d+|manuscript page|\bfolio\b|\btext\b|inscription detail|"
                  r"museum (front|entrance|exterior)|\bsign\b|plaque|signature|avatar", re.I)


def _tokens(s):
    words = re.findall(r"[a-z0-9]+", s.lower().replace("'s ", " ").replace("’s ", " "))
    return {w[:-1] if len(w) > 4 and w.endswith("s") else w for w in words if w not in STOP and len(w) > 1}


def rank(wiki, shot, text, pool):
    """Wiki files for one narration line, best first, as [(score, title, imageinfo, strong)].
    Score = words shared with the shot's search words (x3) and with the spoken line (x1); the wiki's own
    search hits and images on the Short's own wiki articles get a bonus; infoboxes, portraits and concept art
    (static, seen everywhere) lose points. strong = shares 2+ words with the line, or 1 and sits on those articles."""
    want, said = _tokens(shot.get("search", "")), _tokens(text)
    first = re.findall(r"[a-z0-9]+", shot.get("search", "").lower())
    subject = {first[0][:-1] if len(first[0]) > 4 and first[0].endswith("s") else first[0]} - STOP if first else set()
    cands = dict(pool)
    hits = {}
    if wiki and shot.get("search"):
        titles = search(wiki, shot["search"])
        infos = info(wiki, titles)
        for n, t in enumerate(titles):
            if t in infos and acceptable(t, infos[t]):
                cands[t] = infos[t]
                hits[t] = max(1.0, 3.0 - n * 0.1)
    out = []
    for t, i in cands.items():
        name = _tokens(t.rsplit(".", 1)[0])
        matched = len((want | said) & name)
        s = 3 * len(want & name) + len(said & name) + hits.get(t, 0) + (1 if t in pool else 0)
        if DULL.search(t):
            s -= 2
        if len(name) <= 1:                               # "Rome.jpg": a bare name says nothing about the line
            s -= 1.5
        if subject and not subject & name:               # search starts with its subject: "Zoro ..." must show Zoro,
            s -= 3                                       # not "Douglas Bullet Using Supreme King Haki"
            matched = min(matched, 1)
        if s > 0:
            out.append((s, t, i, matched >= 2 or (t in pool and matched >= 1)))
    out.sort(key=lambda x: -x[0])
    return out


class Picks(dict):
    """{file title: times used} that also remembers pick order, for the render log."""
    def __init__(self):
        super().__init__()
        self.order = []

    def __setitem__(self, k, v):
        self.order.append(k)
        super().__setitem__(k, v)


def pick(shot, text, wiki, pool, used, n, out_paths):
    """Fill out_paths[:n] with distinct images for one line's beats. Returns the paths actually filled.
    Beat 1: the writer's exact file, else the best-ranked wiki file. Later beats need a real match (a search word
    in the file name), so a line only cuts to a new picture when that picture is about the line."""
    got, mine = [], set()
    if wiki and shot.get("image"):
        t = _title(shot["image"])
        i = info(wiki, [t]).get(t)
        if i and i.get("width", 0) >= 300 and _download(_url(i), out_paths[0]):
            _record(t, i)
            used[t] = used.get(t, 0) + 1
            got.append(out_paths[0])
            mine.add(t)
    ranked = rank(wiki, shot, text, pool) if wiki else []
    best = ranked[0][0] if ranked else 0
    # unused first, then pictures used once; a file never appears more than twice in a Short
    order = [r for r in ranked if not used.get(r[1])] + [r for r in ranked if used.get(r[1]) == 1]
    if not got and order and not order[0][3]:          # weak best match (a bare "Zoro" search): an on-topic article
        strong = [r for r in order if r[3]]            # image, even one shown before, beats a random file
        order = strong[:1] + order if strong else order
    for s, t, i, strong in order:
        if len(got) >= n:
            break
        if t in mine or (got and not strong):         # extra cuts only for pictures that are clearly about the line
            continue
        if got and s < max(3, best * 0.35):
            break
        if _download(_url(i), out_paths[len(got)]):
            _record(t, i)
            used[t] = used.get(t, 0) + 1
            got.append(out_paths[len(got)])
            mine.add(t)
            pool.setdefault(t, i)                      # what this Short already showed is on-topic for later lines
    return got


def pick_hook(shot, text, wiki, pool, used, out_path, tries=4):
    """First picture of a Short: among the best-matching files, the most colourful close-up (framing.hook_score).
    Top theory Shorts open on a vivid face, not on a grey crowd shot."""
    import framing
    ranked = rank(wiki, shot, text, pool) if wiki else []
    if not ranked:
        return None
    best, scored = ranked[0][0], []
    for s, t, i, _ in [r for r in ranked if r[0] >= ranked[0][0] * 0.6][:tries]:
        tmp = f"{out_path}.cand{len(scored)}.jpg"
        if _download(_url(i), tmp):
            try:
                with Image.open(tmp) as im:
                    scored.append((framing.hook_score(im) * (0.8 + 0.2 * s / best), t, tmp, i))
            except Exception:
                pass
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    _, t, tmp, i = scored[0]
    os.replace(tmp, out_path)
    _record(t, i)
    for _, _, other, _ in scored[1:]:
        try:
            os.remove(other)
        except OSError:
            pass
    used[t] = used.get(t, 0) + 1
    return t


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("wiki"); s.add_argument("words"); s.add_argument("-n", type=int, default=15)
    c = sub.add_parser("check"); c.add_argument("wiki"); c.add_argument("title")
    a = ap.parse_args()
    if a.cmd == "search":
        titles = search(a.wiki, a.words)
        infos = info(a.wiki, titles)
        good = [t for t in titles if t in infos and acceptable(t, infos[t])]
        for t in good[:a.n]:
            print(f"{t}  {infos[t]['width']}x{infos[t]['height']}")
        if not good:
            print("no usable images; try other words (place/person + object, e.g. 'Pompeii fresco')")
    else:
        t = _title(a.title)
        i = info(a.wiki, [t]).get(t)
        print(f"OK {i['width']}x{i['height']}" if i else "MISSING")
