# Cloud batch session (paid from the Claude cloud-session credit)

All Late Night History TV writing happens here. Start it **by hand** at claude.ai/code on this repo,
never as a scheduled routine (routines are billed differently from an interactive cloud session —
check your plan before scheduling one). Paste:

```text
Follow CLOUD_BATCH.md exactly.
```

Before step 1, read `CONTENT_PLAYBOOK.md` (the niche's *why* — ranked formulas, the opening ritual's
evidence, the 60-title topic bank) and `WRITER.md` (the contract this session writes to).

---

**Budget guidance.** Each long script is ~1h45-2h05 of narration (13,000-15,600 words, 850-1,700
lines, at least 15 chapters — `channel.json`'s `style.long.min_chapters`); the pipeline appends a
music-only tail automatically so the published video is ~2h50m, but you only write the narration. This
is still a much bigger write than a Shorts-era script, so cost per script is correspondingly higher.
**One session should write 2 long scripts (one full day's worth: `<date>-L` and `<date>-L2`)**, not
more — pushing 2 fully-researched, fact-checked, editor-reviewed scripts per session is a better use of
budget than rushing 3-4 thin ones. If you're running low on budget partway through, finish and push the
one script you have rather than leaving two half-written. Check current model pricing before picking
models for the session and the subagents below; the roles and division of labor matter more than the
exact model names.

## Roles
- You (main session): plan, hand out IDs, push. Research and write the scripts yourself, or hand each
  one to a writer subagent — either way, you are responsible for the final quality bar before pushing.
- Fact-check subagent: one pass per long video, reading the finished script and its own WebSearch
  results, acting as a skeptical historian (WRITER.md section 6).
- Editor subagent: one pass per long video, after the fact-check pass, reading only the finished
  script (no new research), scoring it against WRITER.md's bar.

## Steps
0. **Rescue first.** For every `scripts/rejected/<id>.json` whose `.log` only fails the editor gate
   ("editor review scored"), `git mv` it back to `scripts/backlog/` and give it straight to the editor
   pass (step 3). That's far cheaper than writing it again. Count it as one of this session's two and
   skip its ID below.
1. Run `python plan.py next 4` (prints up to 2 days' worth; you only need the first 2 IDs — one day)
   and `python -c "import json,glob;print('\n'.join(json.load(open(f))['title'] for f in
   sorted(glob.glob('scripts/*/*.json'))[-60:]))"` (recent titles, to avoid repeating a topic or
   angle).
2. Pick each video's specific topic yourself up front (civilization/era/mystery + angle, one line
   each), checked against the recent-titles list, against `CONTENT_PLAYBOOK.md`'s ranked formula table
   (section 2) and 60-title topic bank (section 9), and against WRITER.md's competitor benchmarks
   (section 3) for the assigned series. The two long IDs for a day must differ in series and angle.
3. For each long ID, research and write per WRITER.md:
   - Research with WebSearch (no fixed call cap — a 13,000-15,600 word documentary needs real breadth
     of sourcing; budget roughly 10-20 searches per script, more for `mysteries` topics that need both
     the claim and the mainstream explanation checked).
   - Write the script chapter by chapter directly into `scripts/backlog/<id>.json`, keeping a running
     word count, and write `notes/<id>.md` alongside it (Sources, Angle, Self-review — section 8).
   - Run `python validate_script.py scripts/backlog/<id>.json` and fix every error before moving on.
4. **Fact-check pass.** Spawn a subagent with this brief:
   > Read WRITER.md section 6 (Fact check step) and `scripts/backlog/<id>.json`. Act as a skeptical
   > historian: list every factual claim in the script and verify each with WebSearch. Flag anything
   > wrong, unverifiable, or — for `mysteries`-series scripts — any claim that states a fringe theory
   > as settled fact instead of a theory. Report the flagged list back; don't edit the file yourself.
   Fix whatever it flags yourself, then write `notes/<id>.md`'s `## Fact check` section listing the
   claims checked and any fixes made.
5. **Editor pass.** Spawn a second subagent with this brief:
   > Read WRITER.md section 6 (Editor review) and `scripts/backlog/<id>.json`. Score it 1-10 on hook,
   > pacing, originality, accuracy/specificity, and title/thumbnail curiosity, written as `hook: 9/10`.
   > Be honest — this is a ~2h50m sleep documentary (1h45-2h05 of narration you wrote, plus the
   > pipeline's automatic music tail) competing with channels getting 1M+ views, not a quick draft.
   > Report the scores and specific weak spots; don't edit the file yourself.
   Rewrite whatever scores under 8 (restructure a whole chapter if needed, don't just tweak lines),
   then re-run the editor pass. At most two rewrite rounds. If it still scores under 8 after that, do
   not push that video — push the other one and say so in your summary. Record the final scores in
   `notes/<id>.md` under `## Editor review`.
6. Only commit scripts that pass `python validate_script.py` and have every editor score at 8+. A
   script that still fails: leave it out of the commit and list it in your reply. Never push a "WIP"
   commit. Commit once: `git add scripts/backlog notes && git commit -m "script: <ids>"`, then push to
   the branch this session is set up to use.
7. Reply with `python plan.py status` and the pushed IDs. Nothing else.
