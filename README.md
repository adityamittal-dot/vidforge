# Late Night History TV

Automated YouTube pipeline for **Late Night History TV** (`@tvlatenighthistory`): calm, long-form
"history for sleep" documentaries — lost civilizations, ancient mysteries, daily life in past eras,
dynasties, and myths and legends, told gently and accurately. Every video is **2.5-3 hours long**;
there are no Shorts on this channel.

The channel publishes **1 long video every day**, scheduled at **01:00 UTC** (the US
bedtime wave — see `channel.json`'s `publish.long_slots_utc`), cycling through four series:
`mysteries` (Lost Worlds & Ancient Mysteries), `life` (Life in the Past), `empires` (Empires &
Dynasties), and `myths` (Myths & Legends).

---

## Current Status (2026-10-16)

- **Schedule**: 1 long video a day at 01:00 UTC (`channel.json`); raise `per_day` once render time and
  writer cost are proven.
- **YouTube**: OAuth app `vidforge` authorised for @tvlatenighthistory; `YT_CLIENT_SECRET` and
  `YT_TOKEN` secrets set; long uploads allowed. Videos publish automatically on schedule
  (`PUBLISH_MODE` unset); repo variable `SYNTHETIC_DISCLOSURE=1`.
- **Backlog**: first script `2026-10-17-L` (How Medieval Peasants Slept Through Winter, fact-checked,
  editor scores 8-10) is in `scripts/backlog/`. Further scripts come from daily CLOUD_BATCH sessions.
- **Open**: full-length render time on Actions is being measured with `render-test.yml`; if a 3 h video
  doesn't fit the 330 min job, rendering gets sharded across jobs (see
  `research/pipeline-improvements.md`).

---

## How It Works

1. **Scripting**: Claude cloud sessions follow `WRITER.md` (and `CLOUD_BATCH.md` for a batched daily
   session) for research, retention structure, and ad-safety rules, and push validated script JSON
   files to `scripts/backlog/<id>.json` (IDs are `<date>-L`; `-L2` if a second daily slot is added)
   alongside research notes in `notes/<id>.md`. A script can also be drafted in plain markdown under
   `drafts/` and converted with `python md2script.py drafts/<slug>.md <id> [--series life]` (format in
   the script's docstring); it writes the JSON plus a `notes/<id>.md` skeleton for the fact check and
   editor review.
2. **Just-in-time release**: the `render.yml` workflow (GitHub Actions, on a 2-hourly schedule) merges
   any pending writer branches into `main`, validates every script with `validate_script.py`, and
   moves a backlog script into `scripts/queue/` once its intended publish date has arrived — so a
   video renders with whatever pipeline code is on `main` that day, not with code from when it was
   written weeks in advance. A script that fails validation is parked in `scripts/rejected/` with a
   log explaining why, instead of blocking the queue.
3. **Audio & Visual Pipeline** (`pipeline.py` orchestrates all of this per script):
   - `tts.py` generates speech with word-level timestamps using Kokoro TTS, at a slow, calm pace for
     long videos (`channel.json`'s `speed.long`).
   - `visuals.py` builds a picture pool from the Wikipedia articles named in the script's `pages`,
     plus a Wikimedia Commons file search per line's `shot.search` words, and ranks files by how well
     their names match the search words and the spoken line. Only freely licensed images are used
     (public domain, CC0, CC BY, CC BY-SA); anything non-free or with a graphic/violent file name is
     filtered out automatically. `framing.py` crops every picture to fill the frame with a slow
     push-in/pull-out/drift.
   - `video.py` renders the clips and the final video via FFmpeg. Long videos on this channel run calm
     and plain by design (`channel.json`'s `style.long`): no burned-in captions, no sound effects, no
     on-screen keyword cards, and no zoom/shake/flash — just narration, music, and slow-moving images.
4. **Scheduled Upload**: `upload.py` uploads the finished video to YouTube, assigns it to its series
   playlist, and schedules it for the next free publish slot in `channel.json`. The script's `comment`
   question is posted as the first comment once the video goes public. Numbered series ("Atlantis Part
   2: …") link each other: a new part lists the earlier parts' links in its description, and the
   previous part's description gets a "Next:" link added at the top (`pipeline.py`'s `series_parts`).
   While the repo variable `PUBLISH_MODE` is `private`, every upload stays private for review.
5. **Alerts & Archive**: After each upload, ntfy sends your phone the title, the scheduled time, and
   the YouTube Studio link, and the script moves to `scripts/done/<id>.json`.
6. **Daily Insights**: `insights.yml` runs daily, querying the YouTube Data/Analytics APIs to update
   `data/performance.md` (video stats, watch time, and YPP progress) and `data/trends.md`.

---

## Visuals, Voice & Editing

- **Visual Sourcing**: `visuals.py` pulls every usable image from the Wikipedia articles in a script's
  `pages` (and its `en.wikipedia.org` `sources`), adds a Wikimedia Commons file search on each line's
  `shot.search`, and ranks files by how many words their names share with the search words and the
  spoken line. Logos, icons, flags, locator maps, charts, diagrams, and anything with a graphic or
  violent name (blood, wounds, death, executions) are filtered out, as is anything not freely licensed.
  Line 1 opens on the most evocative close match. `images.py` generates an AI fallback image only when
  Wikipedia/Commons has nothing usable for a line. Every image shown is recorded for per-image
  attribution (see Monetization & Fair Use below).
- **Voice Narration**: Kokoro TTS with a weighted voice blend (`channel.json`'s `voice_blend`: 70%
  `bm_george` + 30% `bm_lewis`, a British storyteller tone) on CPU, slowed down for long videos
  (`speed.long` 0.9x) with longer pauses to match a bedtime pace. Names the voice has to guess are
  logged to `data/pronounce_missing.md` for the writer to add a respelling to `pronounce.json`.
- **Music**: real tracks from Scott Buckley's CC BY library plus HoliznaCC0's public-domain (CC0)
  "Lullabies For The End Of The World" album (`music.py` `TRACKS` / `CC0_TRACKS`, 11 sleep tracks),
  mapped to `music_mood`s — this
  channel always uses `"sleep"`, a quiet bed leveled well under the voice (`channel.json`'s
  `music_below_db`) with light ducking. Every video that uses a track gets the required credit line in
  its description (CC0 tracks need none). Any licensed MP3 dropped into `music/sleep/` joins the pool. If no track can be
  downloaded, the pipeline falls back to a synthesized ambient pad.
- **Dynamic Editing**: long videos on this channel are deliberately plain — full-frame historical
  images with slow motion, hard cuts every ~1-2 seconds of narration to a new matching image, chapter
  title cards and real YouTube chapters, and a quiet, uncluttered thumbnail. No burned-in captions, no
  procedural sound effects, no on-screen keyword cards, and no zoom/shake/flash (`channel.json`'s
  `style.long.calm` strips all of these at render time regardless of what a script's `fx` field says).

---

## Channel Controls

Key settings are configured in `channel.json` or through GitHub repository variables:

| Control | Where to Set | Options / Default | Description |
| :--- | :--- | :--- | :--- |
| **Publish Mode** | Repo Variable `PUBLISH_MODE` | `schedule` (default), `private`, `public` | Controls visibility of new YouTube uploads. |
| **Publish Slots** | `channel.json` (`publish`) | `02:00` UTC | Daily upload time slots (US bedtime wave) and minimum lead hours. |
| **Long Schedule** | `channel.json` (`long_schedule`) | 1 long video/day, every day | Raise `per_day` to 2 (and add a slot) once renders and writer cost are proven; `shorts_per_day` is `0` — this channel has no Shorts. |
| **Series Rotation** | `channel.json` (`rotation.long_cycle`) | `mysteries, life, empires, mysteries, life, myths` | Which series each successive long video belongs to. |
| **Voice Blend** | `channel.json` (`voice_blend`) | `{"bm_george": 0.7, "bm_lewis": 0.3}` | Weighted combination of Kokoro voice tensors. |
| **Voice Override** | Repo Variable `KOKORO_VOICE` | Voice ID (e.g. `bm_george`) | Overrides the voice blend with a single voice. |
| **AI Disclosure** | Repo Variable `SYNTHETIC_DISCLOSURE` | `0` (default) or `1` | Sets YouTube's altered/synthetic content disclosure flag; recommended `1` since the voice is AI. |
| **Background Music** | `music.py` `TRACKS` / `CC0_TRACKS`, or folder `music/sleep/` | `sleep` (the only mood this channel uses) | CC BY-licensed tracks (credited automatically) plus any licensed MP3s you add. |

---

## Owner Routines

### Daily Routine (5 Minutes)
1. **Glance at Notifications**: when a video renders and uploads, ntfy pings your phone with the video
   title and Studio link.
2. **Review Scheduled Uploads**: open YouTube Studio. Check the scheduled video and thumbnail; delete
   or reschedule if you want any adjustments before the publish time.
3. **Pin the First Comment**: a few hours after a video goes public, the pipeline posts its `comment`
   question as the first comment. Pin it in YouTube Studio (the API cannot pin).

### Weekly Routine (10 Minutes)
- Review `data/performance.md` to see which topics, eras, and titles generated the most views and
  watch time (Average View Duration/Percentage matter even more on a 2.5-3 hour video than view count
  alone).
- Review `data/trends.md` to spot emerging high-velocity search queries across the four series.

---

## Troubleshooting

- **Test a render without publishing**: run **Actions > render-test** with a script path (e.g.
  `scripts/backlog/<id>.json`). It renders without uploading or moving the script, prints the render
  time, and attaches the mp4 as a 3-day artifact. Use it to check a full video still fits the job's
  330-minute limit after pipeline changes.
- **Workflow Failures**: check **GitHub Actions > render-and-publish**. Inspect logs on any failed
  step. A long video can take a large share of the job's 330-minute timeout, so a transient failure is
  retried once before the script is counted as a failed attempt.
- **Failed Scripts**: if a script fails 3 consecutive render attempts, it is parked in
  `scripts/failed/` to avoid holding up the queue. Once resolved, move the JSON back to
  `scripts/queue/` to retry.
- **Rejected Scripts**: if a script fails `validate_script.py`, it is parked in `scripts/rejected/`
  with a `.log` explaining every error. Fix it and move it back to `scripts/backlog/` or
  `scripts/queue/`.
- **Quota Fallback**: if the main Google Cloud project hits a YouTube quota limit, uploads switch to
  the reserve project automatically (when its secrets are set — see `SETUP.md`).

---

## Monetization & Fair Use

- **YouTube Partner Program (YPP)**: requires 1,000 subscribers and either 10M Shorts views in 90 days
  or 4,000 public watch hours (note: starting 1 Feb 2027, new YPP thresholds adjust to 20M Shorts
  views or 8,000 watch hours). Long-form 2.5-3 hour videos are an efficient path to the watch-hour
  threshold.
- **Copyright & Fair Use**: every description credits the per-image sources (public domain and
  Creative Commons images from Wikipedia/Wikimedia Commons, with full per-image attribution generated
  automatically — see `visuals.py` and `channel.json`'s `credit` per series), the music (CC BY), and
  states that the narration voice is AI-generated. Content is original narration illustrated by
  historical images and artwork; no copyrighted video footage is used.

---

## Repository Layout

- `channel.json` — the channel's contract: series, schedule, voice, style, publish slots, banned
  phrases.
- `validate_script.py` — every hard rule a script must pass before it can render (run this before
  pushing any script).
- `plan.py` — computes which script IDs are still missing against the publish schedule
  (`python plan.py next N`, `python plan.py status`).
- `WRITER.md` / `CLOUD_BATCH.md` — the writer's research, schema, and quality brief.
- `scripts/backlog/`, `scripts/queue/`, `scripts/done/`, `scripts/failed/`, `scripts/rejected/` — a
  script's lifecycle, in that order.
- `notes/<id>.md` — each script's sources, angle, self-review, fact check, and editor review.
- `pipeline.py`, `tts.py`, `visuals.py`, `images.py`, `framing.py`, `video.py`, `music.py`, `upload.py`
  — the render and publish pipeline.
- `md2script.py` — converts a markdown draft in `drafts/` into script JSON.
- `.github/workflows/` — `render.yml` (release, render, publish), `render-test.yml` (render only),
  `insights.yml` (daily analytics), `check.yml` (validation on push).
- `research/` — competitor research and `pipeline-improvements.md` (tools, open-source repos, TTS and
  render benchmarks, YouTube policy notes, ranked next steps).
- `docs/` — GitHub Pages site (home, privacy policy, terms) used by the Google OAuth consent screen:
  https://adityamittal-dot.github.io/vidforge/
- `data/` — `performance.md`, `trends.md`, `community.md`, `pronounce_missing.md`, `studio_todo.md`.
