# vidforge research: borrowable OSS, TTS alternatives, ffmpeg speed, music sources, niche tactics, extra tooling

Context grounding pulled from the repo before researching: `channel.json` long-video settings are
`words: 13000-15600` (~125 wpm target), `speed.long: 0.9`, `voice_blend: {bm_george:0.7, bm_lewis:0.3}`,
render style `beat:10.0s, crf:23, fps 30, calm:true (no captions/sfx/cards/zoom)`, target 170 min + 25 min
music tail. `tts.py` runs Kokoro via a local pipeline with an edge-tts fallback and a `pronounce.json`
lexicon. `video.py` renders per-beat clips with Ken Burns motion then (presumably) concatenates. This
grounds the recommendations below in what's actually plugging into what.

---

## 1. Open-source faceless/documentary pipelines worth raiding for ideas

| Repo | Stars/Licence | What it does | What to borrow |
|---|---|---|---|
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | MIT, ~75k+ stars by mid-2026 | topic → script → search terms → TTS → subtitle alignment → stock/local clips → MoviePy compose → ffmpeg render → output. Supports 12+ LLM providers incl. local Ollama. | Its **search-terms-per-line → stock-footage ranking** step is structurally the same problem vidforge's `visuals.py` solves for Wikipedia/Commons images — worth diffing their term-extraction/ranking prompt against vidforge's word-overlap ranker for ideas (e.g. synonym expansion, multi-candidate scoring with an LLM-written search query instead of raw line words). |
| [RayVentura/ShortGPT](https://github.com/RayVentura/ShortGPT) | MIT, ~8k stars | `ContentVideoEngine` for longer videos: audio gen, background-footage sourcing, caption timing, asset prep; uses TinyDB for persistent state across a multi-step pipeline (so a crashed run resumes instead of restarting). | The **TinyDB-backed step persistence** pattern is directly applicable: vidforge's 330-min GH Actions job limit means a single long render that dies at minute 300 currently likely restarts from scratch. A lightweight local checkpoint file (which beats/segments already rendered) would let `pipeline.py` resume rather than reprocess a whole 3h video on retry. |
| [SamurAIGPT/Text-To-Video-AI](https://github.com/SamurAIGPT/Text-To-Video-AI) | MIT | Minimal "generate video from text" reference pipeline — simpler to read than ShortGPT for the script→visual-query step. | Good as a second reference implementation of per-sentence visual search query generation via LLM, cross-check against vidforge's current word-match ranker. |
| [Softcatala/open-dubbing](https://github.com/Softcatala/open-dubbing) | Apache-2.0 | ML-driven dub: translate + synchronize audio dialogue into other languages, align timing to original. | Candidate base for multi-language audio dubbing (see §6) — reuses Whisper-style alignment plus TTS resynthesis, which maps onto vidforge's existing word-level timestamp approach. |
| [jianchang512/pyvideotrans](https://github.com/jianchang512/pyvideotrans) | GPL-3.0-ish (check repo), active (updated 2026) | One-click ASR → subtitle translation → TTS → video re-mux pipeline, supports many TTS engines incl. Edge-TTS, Kokoro-compatible engines. | Reference for building a translate-and-redub step for the music/narration track without re-rendering visuals (mux a new audio track over the same beat-timed video). |
| ["awesome-faceless" list (sasharun)](https://github.com/topics/faceless-youtube) | curated list, 80+ tools | Directory of TTS/text-to-video/editing/automation tools for faceless channels, actively updated (last update cited July 2026). | Use as an ongoing tool-discovery bookmark rather than a dependency — skim quarterly for new CPU-friendly TTS/upscale tools. |

**Honest caveat:** none of these are built for 2.5-3h *calm slideshow* documentaries — they're all optimized
for Shorts/TikTok clip assembly with stock *video* footage, not still-image Ken Burns rendering at
multi-hour length. The useful parts are narrow: query-generation-for-visuals, checkpointing, and dubbing —
not whole-pipeline adoption.

---

## 2. TTS alternatives/improvements to Kokoro for long calm British-male CPU narration

Current: Kokoro-82M, `bm_george`/`bm_lewis` blend, 0.9x speed, CPU, ~125 wpm effective pace. A 2.5h video
at 13,000-15,600 words needs the *synthesis* step itself to stay well under the 330-min job budget,
leaving time for image ranking/download and ffmpeg render.

| Model | CPU speed (RTF = seconds-of-audio-per-second-of-compute; lower is faster) | Verdict for this pipeline |
|---|---|---|
| **Kokoro-82M (current)** | ONNX mean RTF ≈0.64-0.66 (i.e. ~1.5-1.6x faster than real-time) on modern x86; community benchmark on 2 ARM cores showed RTF 0.91-0.93 (close to real-time, i.e. *slow* on weak CPUs). On a 4-core GH Actions runner expect roughly 1.5-3x realtime throughput once batched — synthesizing ~2h of audio costs roughly 40-80 min of CPU time. [Kokoro v1 benchmark gist](https://gist.github.com/efemaer/23d9a3b949b751dde315192b4dcf0653), [kokoro-82m-coreml](https://huggingface.co/FluidInference/kokoro-82m-coreml) | Already a reasonable choice; the main lever left is **batch longer chunks and run via the `kokoro-onnx` CPU runtime** (`thewh1teagle/kokoro-onnx`) instead of the PyTorch path if not already — ONNX was consistently faster in every benchmark found. |
| **Piper** | Faster time-to-first-sample (1.72s FTTS vs Kokoro's 3.66s) and a lower "core-hour ratio" (0.35x vs Kokoro 1.28x) in the KittenTTS CPU comparison thread — i.e. **Piper is meaningfully cheaper per minute of audio on CPU**. [KittenML/KittenTTS#40](https://github.com/KittenML/KittenTTS/issues/40) | Real candidate for cutting render-job CPU minutes, **but** quality/naturalness over a 2h continuous listen was rated worse than Kokoro in the same roundup ("Piper is light, fast... Kokoro is heavier, smoother and closest to natural narration... holds up for long-form listening"). Also thinner British-male voice selection out of the box than Kokoro's `bm_*` set. Worth a direct A/B test since CPU-minutes saved could be substantial (330-min ceiling), but don't swap blind — the playbook's retention numbers depend on narration quality holding attention for hours. |
| **Kyutai Pocket TTS** (released Jan 2026, 100M params) | Explicitly built to "run on a CPU in real-time" per Kyutai's own framing — smallest of the new crop. [kyutai.org/tts](https://kyutai.org/tts/) | Promising low-latency option; unclear if it ships a British-male voice preset or needs voice cloning from a reference clip (it does support voice cloning). Would need a reference audio clip of a calm British male narrator licensed for this use — more setup than Kokoro's bundled voices. Worth a proof-of-concept run, not a swap yet. |
| **F5-TTS** | CPU RTF ≈37 (i.e. ~37x *slower* than real-time) on Xeon per the project's own issue thread. [SWivid/F5-TTS#81](https://github.com/SWivid/F5-TTS/issues/81) | Too slow for CPU at this length — a 2h narration would take ~74+ CPU-hours. Disqualified for GH Actions CPU runners. |
| **ZipVoice-Distill (4 NFE)** | RTF ≈1.22 on a single Xeon thread, ~33x faster than F5-TTS. | Same flow-matching family as F5-TTS but distilled for speed; worth a bench if Piper's quality loss is unacceptable — sits between Piper's speed and Kokoro's quality, but no evidence yet of a ready British-male voice, and it's less battle-tested than Kokoro/Piper. |
| **StyleTTS2 / Orpheus-3B / Dia-1.6B** | No usable CPU RTF numbers found; one benchmark had Orpheus-3B fail to produce output at all in testing, and StyleTTS2 numbers were GPU-only (601ms TTFB). Orpheus and Dia are also 1.6-3B-parameter LLM-style TTS stacks — expect them to be *far* slower than Kokoro's 82M on CPU-only runners by simple parameter-count scaling. | Not realistic for a free CPU GH Actions runner at this length; shelve until/unless a GPU runner is affordable. |
| **Chatterbox** | Already rejected per your memory note. | Not re-litigated here. |

**Recommendation:** keep Kokoro as the production voice (quality + proven British male voices + already
integrated), but (a) confirm you're on the ONNX runtime path not PyTorch for the CPU speed win, and (b)
spend one spare pipeline run A/B-testing Piper's `en_GB` male voice purely as a time-budget safety valve if
a 330-min job is ever close to timing out — not as a quality upgrade.

---

## 3. Faster ffmpeg rendering for 3h slideshow video on 4-core CPU runners

Current setup already does per-beat clips (`beat: 10.0s`) + CRF 23 + calm style (no zoom/shake per
`channel.json`). Concrete speed levers, in priority order:

1. **Render-once-concat-with-copy, never re-encode the whole timeline.** Render each beat/segment to
   identical codec/resolution/fps/pixel format, then `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4`.
   This is already implied by the per-beat clip approach — verify `video.py`'s final assembly step uses
   `-c copy` for the concat and does *not* re-encode the full 3h timeline a second time for music mixing;
   mux audio in a **separate pass** (`-c:v copy -c:a aac -shortest`) so changing music never forces a video
   re-encode. [ffmpeg-micro.com slideshow guide](https://www.ffmpeg-micro.com/blog/ffmpeg-create-slideshow-from-images)
2. **`-tune stillimage` + raise CRF slightly for stills.** For static Ken-Burns pans over photos, x264's
   stillimage tuning plus CRF in the 20-23 range (already used) is close to optimal; going lower than CRF
   20 wastes CPU time encoding detail invisible on a still pan.
3. **Avoid `zoompan`'s sub-pixel jitter tax.** If any zoom/pan filter is still used anywhere in the
   pipeline (it's disabled for `calm: true` long videos per `channel.json`, so may only matter for Shorts),
   `zoompan` truncates crop coordinates to whole source pixels, causing visible stutter on slow pans unless
   the source is upscaled first (`scale=8000:-2` before `zoompan`) — expensive. Since long-form here is
   explicitly "no zoom/shake" already, this is low-priority, but worth knowing if `framing.py`'s drift
   effect secretly uses zoompan internally — a cheaper alternative is `crop` with an animated `x`/`y`
   expression, which doesn't have the rounding problem and is lighter on CPU.
4. **GitHub Actions matrix parallelism across beats.** A matrix-job strategy (`strategy.matrix`) can
   split a 3h video's ~1000+ beats into N parallel jobs (e.g. 4-8 shards), each rendering a slice of beat
   clips on its own free-tier runner, then a final cheap job concatenates with `-c copy`. This trades
   wall-clock time for job count (still free on public repos) and sidesteps the 330-min single-job ceiling
   entirely rather than just making it tighter. This is the single highest-leverage change available if
   render time is ever the bottleneck, since GH Actions public-repo minutes are free and parallel jobs
   don't share the 330-min cap. Needs the pipeline split into "render beat-clips for shard N" / "concat all
   shards" steps with clip lists passed as artifacts between jobs.
5. **Pin thread count explicitly** (`-threads 4` or match runner core count) — GH Actions' standard
   Linux runners are documented at 4 vCPU; letting x264 auto-detect is usually fine but pinning avoids any
   oversubscription if other pipeline steps (image download/resize) run concurrently in the same job.

---

## 4. Free CC0/CC-BY ambient/sleep music sources, scriptable

| Source | Licence terms | How to pull it by script |
|---|---|---|
| **Free Music Archive — HoliznaCC0 catalog** | CC0 (public domain, zero attribution needed) | FMA has a public API; HoliznaCC0 specifically publishes "Space / Sleep / Meditation" albums as CC0, so no credit-line bookkeeping needed at all for these tracks (simpler than vidforge's current CC-BY credit-line generation for every track). [freemusicarchive.org/music/holiznacc0](https://freemusicarchive.org/music/holiznacc0/space-sleep-meditation) |
| **Pixabay Music** | Pixabay's own royalty-free licence (free for commercial use, no attribution legally required, though crediting is polite) | Pixabay has a (rate-limited) content API requiring a free API key; "sleep"/"deep sleep" categories are well-stocked. [pixabay.com/music/search/sleep](https://pixabay.com/music/search/sleep/) |
| **Chosic** | Filterable by "no attribution required" directly in the UI | No official API; scriptable via scraping the filtered listing page (`?attribution=no`) if automating selection, otherwise manual curation into `music/sleep/` as the README already supports. [chosic.com/free-music](https://www.chosic.com/free-music/all/?sort=&attribution=no) |
| **Lots of Sounds** | Explicitly CC0, "no attribution required," REST API with one API key, 12,000+ sounds | Best fit for *scripted* pulling since it's a documented REST API rather than a scrape target — good for ambient bed/texture layers (rain, wind, fire) under narration rather than full music tracks. [lotsofsounds.com](https://www.lotsofsounds.com/) |
| **Musopen / Internet Archive / Library of Congress (Citizen DJ)** | Public domain / CC0 classical and archival recordings | Good for calmer orchestral beds if you ever want more musical variety than ambient pads; Internet Archive has a stable scrape-friendly API (`archive.org/advancedsearch.php`). |
| **Uppbeat** | Free tier requires attribution + a free account; paid tier removes it | Already attribution-compatible with vidforge's existing credit-line generator, but needs an account/download-token flow, not a bare script-fetchable URL — lower priority than the CC0 sources above given vidforge already auto-generates CC-BY credit lines, but CC0 sources remove that bookkeeping need entirely for new tracks. |

**Recommendation:** add a small `music/sleep_pool_fetch.py`-style script that pulls HoliznaCC0 (CC0, FMA)
and Lots of Sounds (CC0, REST API) tracks into the existing `music/sleep/` folder — this *reduces* the
credit-line surface area (CC0 needs none) compared to today's CC-BY-only sourcing, while growing the pool
so the same handful of tracks don't repeat across every video (viewers who binge the channel will notice
repeats).

---

## 5. What top sleep-history channels actually do, and YouTube's AI-content monetization risk

The repo's own `CONTENT_PLAYBOOK.md` (dated 2026-10-14, two days before this research) already captures the
competitive analysis in detail — title formulas, opening ritual, thumbnail style, pacing, chapter cadence —
so the net-new findings from outside research are:

- **RPM/CPM reality check:** sleep/ambient content sits at the low end of CPM niches (~$3-6 CPM gross,
  meaning roughly $1.50-3 RPM after YouTube's 55% creator share), per niche-CPM roundups. [outlierkit CPM
  data](https://outlierkit.com/blog/most-profitable-youtube-niches), [fluxnote sleep-sounds
  earnings](https://fluxnote.io/guides/how-much-sleep-sounds-channel-makes). Sleep-sounds-specific channels
  were cited earning $500-$9k/month in this band, scaling almost purely on view volume, not per-view rate —
  which matches the playbook's own thesis that watch-time-per-impression (not CTR tricks) is the whole
  game. Mid-roll ads past 20 minutes are worth ~1.3x a standard upload's ad load, which argues *for* the
  pipeline's long 2.5-3h format and *against* trimming length to "tighten" content.
- **YouTube's 2026 "inauthentic content" policy is the real risk to watch, not covered in the playbook.**
  On 2026-07-15 YouTube renamed "repetitious content" to **"inauthentic content"** in the YPP policy, with
  a first major enforcement wave in January 2026 that terminated 16 channels (4.7B lifetime views, 35M
  subs combined) for mass-produced, template-based AI content. [TechCrunch coverage](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/),
  [air.io policy timeline](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline).
  The three flagged categories are: (1) generic/repetitive/template-based content, (2) off-putting or
  distressing content, (3) AI personas discussing sensitive topics like health/finance. YouTube's own
  guidance: **"AI is fine if you disclose it and add genuine human value... faceless compilations with a
  static image, an AI voiceover, and nothing else exemplify the type of content at risk."**
  - vidforge is already doing several of the right things per this framing: real narration (not a TTS
    reading a listicle), real Wikipedia/Commons sourcing with per-image attribution, a disclosed synthetic
    voice (`SYNTHETIC_DISCLOSURE` repo variable), chapter structure, and a distinct editorial angle per
    video (skeptical-but-kind mystery framing, etc.) rather than a templated "static image + AI voice"
    loop.
  - **Risk area to actively manage:** the "static image, slow pan, nothing else for 3 hours" format is
    structurally close to what YouTube calls out as the archetype of inauthentic content, even though the
    *content itself* (researched narration, curated historical images, per-video angle) is not generic.
    Mitigate by leaning harder into things that read as "genuine value add" to an automated reviewer/human
    spot-check: real citations/sources in the description (already planned via per-image credits), unique
    per-video chapter titles (already required), and avoiding any appearance of templated filler (e.g. the
    "music-only sleep tail" should stay clearly labeled as a tail, not disguised as more narration).
- **Series numbering compounds pre-sold watch time** (Midnight History's "Antarctica Part 3" got 29x its
  channel's median) — the playbook already flags this; worth enforcing a *consistent* part-numbering and
  cross-linking (link Part 1→2→3 in description/end screen) since none of the research surfaced an
  automated end-screen/cross-link step in the current pipeline description.

---

## 6. Other tooling worth adding

| Tool/feature | Fit |
|---|---|
| **YouTube Studio "Test & Compare"** | Confirmed **manual-only** — there is no public API for title/thumbnail A/B testing as of 2026; it's a Studio UI feature (up to 3 title/thumbnail variants per video, 2-week test, picks the winner by watch-time share). [support.google.com A/B test help](https://support.google.com/youtube/answer/16391400?hl=en-GB) **Caveat that matters for this pipeline:** manually editing the title/thumbnail while a test is running auto-cancels it — so any future metadata-touch-up automation (SEO re-title scripts, thumbnail regeneration) must check for/avoid touching videos with an active Test & Compare run, or it will silently kill the test. Since the pipeline already generates `thumbnail.prompt`/`thumbnail.text` + a Variant B for this exact purpose (per the playbook), the only gap is a reminder/checklist step so the owner's 5-minute daily routine includes *starting* the Test & Compare manually — it can't be triggered from `upload.py`. |
| **Auto chapters/timestamps/SEO description** | Already implemented via validator-enforced chapter cadence; no need for a third-party generator (e.g. the Apify "YouTube Chapters & Timestamps Generator") since vidforge generates chapters from its own script JSON at the source, which is strictly better (ground truth, not a transcript-inferred guess). |
| **Real-ESRGAN upscaling of low-res Commons/Wikipedia images** | CPU-only speed is rough: ~30-60 seconds per image in `realesrgan-ncnn-vulkan`'s CPU fallback mode. [aireiter.com Real-ESRGAN guide](https://aireiter.com/blog/real-esrgan-guide-download-gui) At ~9-10s screen-time per image and ~1000+ images per 3h video, upscaling every image would cost **8-16+ hours of CPU time per video** — completely incompatible with the 330-min job budget. **Only viable if scoped narrowly**: upscale a small curated set (e.g. the ~15-25 chapter-opener images and thumbnail source image only, not the full pool) as a separate, lower-frequency batch job (e.g. a weekly cache-building workflow, not per-video), writing results into a local upscaled-image cache keyed by Commons filename that `visuals.py` checks before falling back to the raw file. Running it on GPU (e.g. free-tier Colab or a Cloudflare Workers AI image model, which the pipeline already uses for AI fallback scenes) would be far more practical than CPU `realesrgan-ncnn-vulkan` for this volume. |
| **Auto-translation / multi-language dubbing** | [Softcatala/open-dubbing](https://github.com/Softcatala/open-dubbing) (Apache-2.0) or [pyvideotrans](https://github.com/jianchang512/pyvideotrans) give a template: Whisper-style alignment (vidforge already has word-level timestamps from Kokoro, so this step is half-done) → text translation (even a cheap LLM call) → re-TTS in target language → remux audio only over the *same* rendered video (no re-render of visuals needed, since the long-form style has no burned-in captions to translate). Spanish/Portuguese/Hindi dubs of the same video could multiply reach without redoing the expensive visual-render step at all — this is a genuinely low-cost addition given the existing per-beat clip + separate-audio-mux architecture, and a natural "weekly batch" job (pick the best-performing video of the week, dub it) rather than per-video-at-render-time. |
| **SEO/trend tooling** | `data/trends.md` already exists in the pipeline (per `insights.yml`). No external tool found that beats querying YouTube Data/Analytics API directly the way the pipeline already does; third-party SEO tools (VidIQ, etc.) add cost without a scriptable edge over the Data API the pipeline already has access to. |
| **Checkpointing / resumable long renders** | Borrowed idea from ShortGPT's TinyDB persistence (§1) — a small local JSON/SQLite recording which beat-clips are already rendered would let a retried job (the README mentions "retried once before the script is counted as a failed attempt") skip already-done work instead of re-rendering from zero, directly extending effective headroom under the 330-min cap. |

---

## Sources (consolidated)

- [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), [MoneyPrinterTurbo GitHub Builder Guide](https://www.verdent.ai/guides/moneyprinterturbo-github)
- [RayVentura/ShortGPT](https://github.com/RayVentura/ShortGPT), [ShortGPT docs](https://docs.shortgpt.ai/)
- [SamurAIGPT/Text-To-Video-AI](https://github.com/SamurAIGPT/Text-To-Video-AI)
- [Softcatala/open-dubbing](https://github.com/Softcatala/open-dubbing)
- [jianchang512/pyvideotrans](https://github.com/jianchang512/pyvideotrans)
- [awesome-faceless topic listing](https://github.com/topics/faceless-youtube)
- [On-device TTS Comparison 2026 — Picovoice](https://picovoice.ai/blog/on-device-tts/)
- [KittenML/KittenTTS CPU benchmark thread](https://github.com/KittenML/KittenTTS/issues/40)
- [micdrop.dev Kokoro vs Piper vs Pocket TTS](https://micdrop.dev/blog/local-tts-node-kokoro-vs-piper)
- [Kokoro v1 benchmark gist](https://gist.github.com/efemaer/23d9a3b949b751dde315192b4dcf0653)
- [SWivid/F5-TTS RTF issue](https://github.com/SWivid/F5-TTS/issues/81)
- [ZipVoice arXiv](https://arxiv.org/pdf/2506.13053)
- [Kyutai TTS](https://kyutai.org/tts/)
- [ffmpeg-micro.com slideshow + zoompan guides](https://www.ffmpeg-micro.com/blog/ffmpeg-create-slideshow-from-images), [zoompan jitter](https://www.ffmpeg-micro.com/blog/ffmpeg-zoompan-filter-ken-burns-zoom-and-pan-without-the-jitter)
- [HoliznaCC0 on Free Music Archive](https://freemusicarchive.org/music/holiznacc0/space-sleep-meditation)
- [Pixabay sleep music](https://pixabay.com/music/search/sleep/)
- [Chosic no-attribution filter](https://www.chosic.com/free-music/all/?sort=&attribution=no)
- [Lots of Sounds CC0 API](https://www.lotsofsounds.com/)
- [TechCrunch: YouTube clarifies AI slop policy, July 2026](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)
- [air.io 2026 YouTube monetization policy timeline](https://air.io/en/monetization/youtube-monetization-policy-changes-2026-a-complete-dated-timeline)
- [outlierkit profitable niches/CPM data](https://outlierkit.com/blog/most-profitable-youtube-niches)
- [fluxnote sleep sounds earnings](https://fluxnote.io/guides/how-much-sleep-sounds-channel-makes)
- [YouTube A/B test titles & thumbnails help](https://support.google.com/youtube/answer/16391400?hl=en-GB)
- [aireiter.com Real-ESRGAN CPU guide](https://aireiter.com/blog/real-esrgan-guide-download-gui)
- [xinntao/Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan)

## Follow-up: Kokoro ONNX benchmark (2026-10-16, measured locally, 8-core CPU)

Same 553-word passage, bm_george 0.7 + bm_lewis 0.3, speed 0.9:

| Runtime | RTF (lower is faster) |
|---|---|
| PyTorch `kokoro` (current) | 0.513 |
| `kokoro-onnx` fp32 | 0.597 |
| `kokoro-onnx` int8 | 0.455 |

Decision: stay on PyTorch. fp32 ONNX is slower; int8 is only ~11% faster and loses Kokoro's
word timestamps, its misaki G2P (kokoro-onnx phonemizes with espeak only) and some quality from quantization.
