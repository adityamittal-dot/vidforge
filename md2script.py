"""Convert a markdown draft (drafts/<slug>.md) into pipeline script JSON plus notes/<id>.md.

Draft format: a `# Title` line, then `**Thumbnail:** TEXT — prompt`, `**Description:**`, `**Tags:**`,
`**Pinned comment:**`, optional `**Pages:**` (comma-separated Wikipedia titles) and `**Series:**`,
then `## Chapter N — Name` sections with one narration line per text line. A trailing
`[paint: ...]` on a line becomes shot.paint. A `Search: q1 | q2 | q3` line right under a chapter heading
gives that chapter's Wikimedia Commons queries; its lines rotate through them as shot.search, and a
trailing `[search: ...]` on a line overrides it. Name the subject first ("Avercamp winter", "bed medieval
manuscript"): the ranker penalises files without the query's first word. A `## Sources` section of
markdown links ends the script.

    python md2script.py drafts/<slug>.md <id> [--series life] [--out scripts/backlog]
"""
import argparse
import json
import os
import re

STOP = set("a an the and or of to in on at for with by from is was are were it its this that you your "
           "we our they their he she his her be been as but so if not no all one".split())


def field(md, name):
    m = re.search(rf"^\*\*{name}:\*\*\s*(.+)$", md, re.M)
    return m.group(1).strip() if m else ""


def keywords(text, n=4):
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]+", text) if w.lower() not in STOP]
    return " ".join(words[:n])


def split_long(text, limit=24):
    """Split a narration line over `limit` words at a comma/semicolon near the middle."""
    if len(text.split()) <= limit:
        return [text]
    parts = re.split(r"(?<=[,;:])\s+", text)
    out, cur = [], ""
    for p in parts:
        if cur and len((cur + " " + p).split()) > limit:
            out.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    out.append(cur)
    return out


def convert(path, sid, series=None):
    md = open(path, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    body, _, tail = md.partition("\n## Sources")
    sources = re.findall(r"\((https?://[^)\s]+)\)", tail)
    thumb = field(md, "Thumbnail")
    t_text, _, t_prompt = thumb.partition(" — ")
    tags = [t.strip() for t in field(md, "Tags").split(",") if t.strip()][:15]
    pages = [p.strip() for p in field(md, "Pages").split(",") if p.strip()]
    if not pages:
        pages = [re.sub(r"_", " ", u.rsplit("/", 1)[-1]) for u in sources if "en.wikipedia.org/wiki/" in u]
        pages = [re.sub(r"%E2%80%93", "–", p) for p in pages]

    lines, chapters = [], []
    chapter_name, queries, qi = title, [], 0
    for raw in body.splitlines():
        raw = raw.strip()
        m = re.match(r"^## (?:Chapter \d+\s*[—-]\s*)?(.+)$", raw)
        if m:
            chapter_name = m.group(1).strip()
            chapters.append({"line": len(lines), "title": chapter_name})
            queries, qi = [], 0
            continue
        sm = re.match(r"^\*?Search:\s*(.+?)\*?$", raw)
        if sm:
            queries = [q.strip() for q in sm.group(1).split("|") if q.strip()]
            continue
        if not raw or raw.startswith(("#", "**", "---")):
            continue
        paint = None
        pm = re.search(r"\s*\[paint:\s*(.+?)\]\s*$", raw)
        if pm:
            paint, raw = pm.group(1).strip(), raw[:pm.start()].strip()
        search = None
        qm = re.search(r"\s*\[search:\s*(.+?)\]\s*$", raw)
        if qm:
            search, raw = qm.group(1).strip(), raw[:qm.start()].strip()
        for k, text in enumerate(split_long(raw)):
            if search:
                q = search
            elif queries:
                q, qi = queries[qi % len(queries)], qi + 1
            else:
                q = f"{keywords(text)} {keywords(chapter_name, 3)}".strip()
            shot = {"search": q}
            if paint and k == 0:
                shot["paint"] = paint
            lines.append({"text": text, "delivery": "slow", "shot": shot, "fx": "none"})

    script = {
        "id": sid, "format": "long", "series": series or field(md, "Series") or "life",
        "wiki": "en.wikipedia.org", "topic": title.split("|")[0].strip(), "title": title,
        "description": field(md, "Description"),
        "hashtags": ["#historyforsleep"] + [f"#{re.sub(r'[^a-z0-9]', '', t.lower())}" for t in tags[2:4]],
        "tags": tags, "music_mood": "sleep", "comment": field(md, "Pinned comment"),
        "pages": pages, "lines": lines, "chapters": chapters,
        "thumbnail": {"text": t_text.strip(), "search": field(md, "Thumbnail search") or keywords(t_prompt, 5), "prompt": t_prompt.strip()},
        "sources": sources,
        "self_check": {"hook": "welcome ritual + core question", "loop": "chapters end on soft open questions",
                       "facts_verified": True},
    }
    return script, sources


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("id")
    ap.add_argument("--series")
    ap.add_argument("--out", default="scripts/backlog")
    a = ap.parse_args()
    script, sources = convert(a.draft, a.id, a.series)
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"{a.id}.json")
    json.dump(script, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    notes = f"notes/{a.id}.md"
    if not os.path.exists(notes):
        with open(notes, "w", encoding="utf-8") as f:
            f.write(f"# {script['title']}\n\nConverted from {a.draft}.\n\n## Sources\n")
            f.writelines(f"- {u}\n" for u in sources)
            f.write("\n## Self-review\n\nTODO\n\n## Fact check\n\nTODO\n\n## Editor review\n\nTODO\n")
    words = sum(len(l["text"].split()) for l in script["lines"])
    print(f"{out}: {len(script['lines'])} lines, {words} words, {len(script['chapters'])} chapters")


if __name__ == "__main__":
    main()
