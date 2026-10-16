# Content Playbook — Late Night History TV

What the sleep-history niche's winners do, measured on 2026-10-14, and how this channel copies and beats it.
`WRITER.md` is the contract; this file is the *why*. The writer reads it every session before picking topics.

Data: the latest 100 videos of 16 channels (Sleepless Historian 715k subs, Get Sleepy 726k, Good Knights Sleep 347k,
Historian Sleepy 214k, Bedtime & Historian 109k, Boring History Secrets 105k, History at Night 75k, Silence of the
Earth 61k, Sleepy History Channel 56k, Midnight History 14k and others). For the outliers we also pulled transcripts,
chapter lists, tags and YouTube's "most replayed" heatmaps.
An **outlier** is a video with far more views than its own channel's median, so it shows the topic or packaging won,
not the channel's size.

---

## 1. How these videos get into feeds

1. **Watch time per impression is the whole game.** A sleep video that's clicked plays for 1-3 hours while the viewer
   sleeps. YouTube's browse and suggested feeds reward exactly that (watch time and session time), so one clicked
   impression is worth 20-50x a normal video's. Everything below either raises the **click** (title, thumbnail,
   topic) or keeps the video **playing** (calm pacing, no ads, no jolts, a long tail).
2. **Suggested traffic comes from the other sleep channels.** People fall asleep to one channel and autoplay hands
   them the next "X for Sleep" video. So we use the niche's shared vocabulary on purpose:
   the `| History for Sleep` title label, tags like "history for sleep", "fall asleep to history",
   "boring history for sleep", and the same look of thumbnail. Looking like the category is how autoplay picks us.
3. **Comments are the engagement signal, and the niche farms them politely.** Every top opening asks
   *"tell me where you're listening from and what time it is for you."* Those videos get 700-2,600 comments
   (Mariana Trench 710, Greek Mythology 2,600, Pirate 2,100). Our validator now requires this line in the opening.
4. **Publish before bedtime.** Videos go out at 01:00 UTC (9 pm US East, 6 pm US West; 8 pm EST after Nov 1), the highest-paying audience's bedtime wave, so they are fresh
   in the feed when the night-time audience opens YouTube.
5. **Series give returning viewers.** Midnight History's best videos are a numbered series ("Antarctica Part 3": 66k,
   29x its median). A Part 2 is pre-sold to everyone who watched Part 1.

## 2. What wins, ranked by outlier strength

| Formula | Evidence (views, multiple of channel median) | Use it as |
|---|---|---|
| **"The ENTIRE Story/History of X"** | Greek Mythology 6.1M (530x); Medieval England 421k (35x); Viking Age 157k (13x); Odyssey 358k (13x) | Flagship. Myths, empires, eras. |
| **"How Did People Sleep/Survive [harsh condition] in [era]?"** | Peasants Sleep in Coldest Winter 297k (25x); Egyptians Sleep in 120°F Summers 217k (18x); Sleep in a Medieval Inn 187k (16x); Underground Dugouts 137k (11x) | Our biggest gap to exploit. The topic *is* sleep, so it matches the viewer's moment. |
| **"What It Was (Really) Like to Be/Live …"** | Pirate 1.3M; Life in 1700s London 115k; Stone Age 183k | Second-person immersion ("You wake before dawn…"). |
| **Deep-time / Earth mystery** | Dinosaurs What If 2.8M (85x); Mariana Trench 990k (30x); Jurassic 857k (26x); Water origin 619k | Our `mysteries` series stays human-history: Ice Age humans, Doggerland, Sundaland, lost lands. |
| **Unsolved mystery, framed skeptically** | Maya Collapse 1.2M; Antarctica Part 3 66k (29x); Piri Reis map 50k (22x) | "What really happened?", "What the record actually shows". Never claim the fringe theory is true. |
| **"100 Sleepy Facts About X"** | Seven Wonders 353k (10x); First Humans 311k; Lost Cities 222k | Easy chapter structure, and the number promises length. |
| **City / place biography** | Sleepy History of London 976k (124x) | "The Sleepy History of Rome / Paris / Constantinople". |

What fails: narrow genealogy (Midnight History's bloodline videos get 200-900 views), dry lists of dates and kings,
anything violent or grim as the selling point, and clickbait that jolts the viewer awake.

## 3. Titles

- Pattern: **`<curiosity or ENTIRE topic> | History for Sleep`**, 50-90 characters. The validator requires "for Sleep".
- Proven openings: "The ENTIRE History of…", "How Did … Sleep/Survive…?", "What It Was Like to…",
  "What Really Happened to…?", "100 Sleepy Facts About…", "… Part 2: …".
- Concrete beats abstract: "120°F Summers", "Coldest Winter", "2 Miles of Ice". Put one number or sensation in.
- No shock words ("Brutal", "Horrifying", "Died"): they jolt sleepers and get ads limited.

## 4. Thumbnails (pipeline: `video.thumbnail_sleep`)

All 15 top thumbnails we examined are **cinematic painted scenes**, full-bleed and warm-dark, with:
- the topic in **1-3 huge words in a gold engraved serif** ("THE VIKING AGE", "MEDIEVAL ENGLAND"), and
- a small label: "HISTORY FOR SLEEP" / "DOCUMENTARY FOR SLEEP" / "NO AD BREAKS".
- Boring History Secrets' variant uses a cartoonish suffering face (shivering peasant, sweating Egyptian), which is
  the strongest CTR device for the "How did they survive…" formula.

The script supplies `thumbnail.prompt` (one painted scene: subject, light, mood) and `thumbnail.text` (1-3 words).
The pipeline paints it and sets the type. Variant B (the stacked top-left layout) is saved for a YouTube Studio Test & Compare.

## 5. The opening ritual (first ~90 seconds, validator-enforced)

Every top video opens the same way, in this order:
1. **Welcome + "Tonight…"**: "Welcome. Tonight, our journey takes us to…"
2. **The promise**: 3-5 specific wonders or mysteries the viewer will meet (the Mariana Trench opening lists
   metallic sounds, phantom fish, glass creatures and a plastic bag). This is what stops the scroll.
3. **Soft CTA**: "If you enjoy these slow journeys, a like and a subscribe help others find us. **Tell me where
   you're listening from, and what time it is for you.**"
4. **Settling ritual**: "Now find a comfortable position. Dim the lights. Take one slow breath."
5. **"Let's begin."** Then straight into a vivid scene: a person, a place, a sensation. Never a date list.

## 6. Structure and pacing

- **Narration: ~1h45-2h05 (13,000-15,600 words), then a music-only "Sleep Music" tail** that the pipeline adds
  automatically, to ~2h50m. Sleepy History of London (976k views) is 3 h with only ~85 min of narration. People are
  asleep by then, and the music keeps the session running. This also cuts the writing per video by about a third.
- **15-25 chapters, one every 3-8 minutes.** Chapter titles are calm teasers ("The Unlikely Recruit",
  "Your Floating Home"), not spoilers.
- **Front-load.** Heatmaps of the top videos peak in the first 30-40% and fall off steadily (viewers fall asleep).
  Put the most vivid chapters, the best images and the promised wonders early. The last third can be gentler and
  slower: daily life, landscape, quiet reflection.
- **Pace:** 108-142 wpm in the winners. Ours is ~125 wpm (Kokoro 0.9x plus 0.5 s pauses).
- **Voice of the script:** warm, unhurried, sensory ("you smell wet wood and frozen mud"), gentle wonder, second
  person for the life formats. Skeptical but kind about myths. No cliffhanger jolts: re-hooks are soft questions.

## 7. Visuals

- Real Wikimedia images (art, artefacts, maps, ruins), chosen per line, plus **up to 40 painted scenes per video**
  (`shot.paint`) for the moments no photograph exists for: a family by the hearth, a ship at night, a city at dawn.
  Put the paintings on the opening, on chapter openers, and on the most immersive lines.
- ~9-10 s per picture with slow pans; the tail dims toward black.

## 8. Ads: a decision for the owner

Three channels put **"NO ADS" / "No Adverts" / "NO AD BREAKS"** in titles or thumbnails. Mid-roll ads wake sleepers,
which kills the watch time that feeds the algorithm. The options:
- **Growth first (recommended until monetised):** irrelevant before YPP anyway.
- **After YPP:** a pre-roll only, no mid-rolls, and say "No Ad Breaks" in the thumbnail label
  (`thumbnail.label`). Fewer ad dollars per view, more views and longer sessions.
- Mid-rolls only in the first 20 minutes is a middle path (set in YouTube Studio per video).

## 9. Topic bank (first 60, highest-evidence first)

Pick from here when `data/trends.md` has nothing better. Mark used ones in `notes/` so they aren't repeated.

**How did they sleep/survive (life)**
1. How Did Medieval Peasants Sleep Through the Coldest Winters? | History for Sleep
2. How Did Ancient Egyptians Stay Cool in 120°F Summers? | History for Sleep
3. What It Was Like to Spend a Night in a Medieval Inn | History for Sleep
4. How Did Vikings Survive the Long Arctic Night? | History for Sleep
5. How Did Roman Soldiers Survive Winter on Hadrian's Wall? | History for Sleep
6. How Did Sailors Sleep on 18th-Century Sailing Ships? | History for Sleep
7. How Did Ice Age Families Survive the Coldest Nights on Earth? | History for Sleep
8. How Did People Stay Warm in a Medieval Castle? | History for Sleep
9. How Did Pioneers Survive Their First Winter on the Prairie? | History for Sleep
10. How Did Monks Live Through Winter in a Medieval Monastery? | History for Sleep
11. How Did Desert Caravans Cross the Sahara? | History for Sleep
12. How Did Samurai-Era Japan Keep Warm Without Heating? | History for Sleep

**What it was like (life)**
13. What It Was Really Like to Live in Ancient Pompeii | History for Sleep
14. What It Was Like to Live in 1700s Paris | History for Sleep
15. What It Was Like to Cross the Atlantic on the Mayflower | History for Sleep
16. A Day in the Life of a Roman Family | History for Sleep
17. What It Was Like to Be a Medieval Knight's Squire | History for Sleep
18. What It Was Like to Live on the Silk Road | History for Sleep
19. What It Was Like to Live in Victorian London | History for Sleep
20. What It Was Like to Be a Lighthouse Keeper | History for Sleep

**The ENTIRE story (empires and myths)**
21. The ENTIRE History of Ancient Egypt | History for Sleep
22. The ENTIRE History of the Roman Empire | History for Sleep
23. The ENTIRE Story of Norse Mythology | History for Sleep
24. The ENTIRE History of the Byzantine Empire | History for Sleep
25. The ENTIRE Story of Egyptian Mythology | History for Sleep
26. The ENTIRE History of the Vikings | History for Sleep
27. The ENTIRE History of the Knights Templar | History for Sleep
28. The ENTIRE Story of the Odyssey | Greek Myths for Sleep
29. The ENTIRE History of the Aztec Empire | History for Sleep
30. The ENTIRE History of Ancient Mesopotamia | History for Sleep
31. The ENTIRE Story of King Arthur | Legends for Sleep
32. The ENTIRE History of the Ottoman Empire | History for Sleep
33. The ENTIRE Story of Celtic Mythology | Myths for Sleep
34. The ENTIRE History of the Mongol Empire | History for Sleep (keep the conquest gentle; ad-safe)
35. The Rise and Fall of Venice | History for Sleep
36. The Sleepy History of Constantinople | History for Sleep

**Mysteries (numbered series where marked)**
37. Atlantis Part 1: Every Clue Plato Left Us | History for Sleep
38. Atlantis Part 2: The Candidates, Ranked by the Evidence | History for Sleep
39. Doggerland: The Lost Land Beneath the North Sea | History for Sleep
40. Sundaland: The Drowned Continent of Southeast Asia | History for Sleep
41. What Really Happened to the Maya? | History for Sleep (different angle from History at Night: daily life + the end)
42. The Bronze Age Collapse: When Civilization Fell Silent | History for Sleep
43. Göbekli Tepe: The Temple Built Before Farming | History for Sleep
44. What Really Happened to the Library of Alexandria? | History for Sleep
45. The Lost Colony of Roanoke: What the Record Shows | History for Sleep
46. The Antikythera Mechanism: An Ancient Computer | History for Sleep
47. Who Built Stonehenge, and Why? | History for Sleep
48. The Indus Valley: A Civilization We Still Can't Read | History for Sleep
49. Easter Island: What Really Happened to Rapa Nui? | History for Sleep
50. The Sea Peoples: History's Most Mysterious Invaders | History for Sleep
51. Antarctica Part 1: What Lies Beneath the Ice | History for Sleep
52. The Voynich Manuscript: The Book No One Can Read | History for Sleep

**100 Sleepy Facts (any series)**
53. 100 Sleepy Facts About Ancient Rome | History for Sleep
54. 100 Sleepy Facts About the Middle Ages | History for Sleep
55. 100 Sleepy Facts About Ancient Egypt | History for Sleep
56. 100 Sleepy Facts About the Vikings | History for Sleep
57. 100 Sleepy Facts About Lost Civilizations | History for Sleep
58. 100 Sleepy Facts About the Ice Age | History for Sleep
59. 100 Sleepy Facts About Castles | History for Sleep
60. 100 Sleepy Facts About Ancient Greece | History for Sleep

## 10. Measure and adapt

`insights.yml` writes `data/performance.md` daily. After 10 videos, double down on whichever formula has the best
views per day **and** average view duration; after 30, drop the weakest series from `channel.json` `rotation`.
Re-run this competitor scan monthly. The niche moves: "How did they sleep" is hot in 2025-26.
