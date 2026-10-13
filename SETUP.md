# Setup Guide — Late Night History TV

Follow this checklist to stand up the pipeline for the new channel, `@tvlatenighthistory`. This is a
**new** YouTube channel, so it needs its own Google Cloud OAuth client and its own credentials — unlike
a channel handoff where secrets carry over, start from a clean slate here.

---

### 1. Create a Google Cloud OAuth Client for This Channel

1. In the [Google Cloud Console](https://console.cloud.google.com/), create a new project (or reuse an
   existing one you control) dedicated to this channel's YouTube API access.
2. Enable the **YouTube Data API v3** for that project.
3. Configure the OAuth consent screen (External is fine for personal use; you don't need to publish
   it, just add your own Google account as a test user if it stays in "Testing").
4. Create an **OAuth 2.0 Client ID** of type **Desktop app**. Download the client secret JSON — this
   is what `auth.py` expects as `yt_client_secret.json`.
5. Make sure you're signed in to the Google account that manages the `@tvlatenighthistory` YouTube
   channel when you run the auth step below, so the token is issued against the right channel.

---

### 2. Authorize Locally and Collect the Token

On your laptop (not in CI):

```bash
python auth.py
```

A browser opens. Sign in with the Google account for `@tvlatenighthistory` and grant access. The
script prints the full token JSON — copy everything it prints.

**Optional reserve credentials** (a second Google Cloud project pointing at the *same* YouTube
channel, so the pipeline can fall back to it if the primary project's daily quota is exhausted):
1. Repeat step 1 with a second Google Cloud project.
2. Save its client secret as `yt_reserve_client_secret.json` and run:
   ```bash
   python auth.py reserve
   ```
3. Copy the printed token for the `YT_RESERVE_TOKEN` secret (step 3).

---

### 3. Set Repository Secrets

In **Settings > Secrets and variables > Actions > Secrets**, add:

- `YT_CLIENT_SECRET`: the full contents of the client secret JSON from step 1.
- `YT_TOKEN`: the full token JSON printed by `python auth.py` in step 2.
- `NTFY_TOPIC`: a topic name for push notifications to your phone (pick any unguessable string; you'll
  subscribe to `ntfy.sh/<topic>` in the ntfy app).

Optional:
- `YT_RESERVE_CLIENT_SECRET` and `YT_RESERVE_TOKEN`: the reserve credential set from step 2, if you set
  one up.
- `CF_ACCOUNT_ID` and `CF_API_TOKEN`: Cloudflare credentials, used only as a last-resort AI image
  fallback when a line's `shot.search` finds nothing usable on Wikipedia/Wikimedia Commons (this
  channel's visuals are historical images first — see `visuals.py`).

---

### 4. Phone-Verify the Channel

YouTube requires the channel to be **phone-verified** before it can:
- upload videos longer than 15 minutes (every video on this channel is 2.5-3 hours, so this is
  mandatory, not optional), and
- set custom thumbnails.

In YouTube Studio, go to **Settings > Channel > Feature eligibility** (or the verification prompt that
appears when you try to upload a long video) and verify with a phone number. Do this before the first
real render — a render that completes without a verified channel will fail to upload and the
thumbnail step will be skipped (`upload.py` logs this and continues rather than crashing the run).

---

### 5. Run Setup Verification

1. Go to **Actions** in your GitHub repository.
2. Select the **check-setup** workflow from the left sidebar.
3. Click **Run workflow**.
4. Confirm every required diagnostic check outputs **PASS** (YouTube credentials, channel match if you
   configured reserve credentials, `NTFY_TOPIC`, the Wikipedia/Wikimedia image API, and the font file
   used for thumbnails). The Cloudflare/Pollinations image-fallback checks are marked optional and
   won't block a PASS overall.

---

### 6. Set the `PUBLISH_MODE` Variable (Safe Launch)

In **Settings > Secrets and variables > Actions > Variables**, add `PUBLISH_MODE` with value
`private` for your first few renders. Every render then uploads privately and nothing goes public
until you review and publish it yourself in YouTube Studio. Once you're confident the pipeline is
producing videos you're happy with, delete the variable (or set it to `schedule`) to resume automatic
scheduled publishing at the slots in `channel.json` (`publish.long_slots_utc`: 01:00 and 04:00 UTC).

---

### 7. Set `SYNTHETIC_DISCLOSURE` (Recommended)

This channel's narration voice is AI-generated (Kokoro TTS). In **Settings > Secrets and variables >
Actions > Variables**, add `SYNTHETIC_DISCLOSURE` with value `1`. The pipeline passes this through to
YouTube's altered/synthetic content disclosure flag at upload time (`upload.py`), which is the honest
and currently recommended setting for an AI-narrated channel.

---

### 8. Script Writing

Scripts are written by Claude cloud sessions following `WRITER.md` (single-session) or
`CLOUD_BATCH.md` (one cloud-credit session per day, writing both of the day's long videos). They land
in `scripts/backlog/<id>.json` with the matching `notes/<id>.md`; `render.yml` releases each one into
`scripts/queue/` once its date arrives and renders it from there. You can also author a script by hand
following `WRITER.md`'s schema (section 5) and drop it directly into `scripts/backlog/` or
`scripts/queue/`.

---

### 9. YouTube Studio One-Time Settings

Open [YouTube Studio](https://studio.youtube.com/) and set:

1. **Branding**: channel banner, avatar, and handle (`@tvlatenighthistory`). Channel description
   mentioning calm long-form history for sleep.
2. **Upload defaults**: **Settings > Upload defaults > Basic info / Advanced settings**. Set
   **Category** to **Education** or **Entertainment** (whichever better fits once you have a few
   videos live), and **Video language** to **English**.
3. **Playlists**: create one playlist per series (`mysteries`, `life`, `empires`, `myths`) matching the
   `playlist` names in `channel.json`, since the pipeline assigns each upload to its series playlist.

---

### 10. Test First Render

1. Go to **Actions > render-and-publish > Run workflow**.
2. Leave the **upload** checkbox unchecked to test-render without publishing anything.
3. Run the workflow against whatever is in `scripts/queue/`.
4. A long video can take a large part of the job's time budget (the job has a 330-minute timeout for
   exactly this reason — one 2.5-3 hour sleep video per run). Once finished, download the workflow
   artifact to check the generated thumbnail and metadata.

---

### 11. Enable Watch-Hour & Retention Analytics (AVD/AV%, YPP watch hours)

`insights.py` can add Average View Duration, Average View Percentage, and a watch-hours-toward-YPP
header to `data/performance.md` via the YouTube Analytics API (`yt-analytics.readonly`), but only once
your stored token has been granted that scope. Since this is a fresh OAuth client, a fresh
`python auth.py` run (step 2) already requests this scope (`upload.py`'s `SCOPES`) — nothing extra to
do unless you rotate the token later without re-running `auth.py`, in which case repeat step 2 and
update the `YT_TOKEN` secret. The next `insights.yml` run picks it up automatically; if the scope is
ever missing, `insights.py` logs a note and skips just that section, and everything else in
`data/performance.md` still updates normally.

---

### 12. Optional: Background Music

Drop any licensed MP3s into the mood folder `music/sleep/` (this channel uses only the `sleep` mood —
see `channel.json`'s `music_mood`). `music.py` already ships a small library of CC BY-licensed calm
tracks mapped to `sleep`; anything you add joins that pool automatically.
