# The Saturday Ledger v5 — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/top234/news-image-20261121-entry-v5/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/top234/news-image-20261121-entry-v5/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A make.fun entry for [news-image-20261121](https://make.fun/bounty/news-image-20261121): one 1024×1024 image summing up Saturday 21 November 2026's world news.

**The Saturday Ledger v5** iterates on v3's clean day-ledger front page (98.1243%, the current final) with v4's corrected numbers: 35 verified stories across 7 regions — 3 hero cards with vivid illustrated scenes, 10 smaller cards with pure-illustration scene strips and no overlay text, a world map with 15 numbered pins, a numbered list of 22 more stories, and a DATE CHECK box naming the Friday 20 November stories deliberately left out plus the stories not confirmed when drawn (BepiColombo's Mercury burn, a final COP31 text). New in the top 13: the Kryvyi Rih toll update (2 killed, 47 injured, first reported Saturday). Every story happened, or was first reported, on Saturday 21 November 2026, with its source named beside it.

## Files

- `generate.py` — draws `entry.png` (1024×1024, PIL, seeded, deterministic; no network, no external assets). Run `python3 generate.py` to re-render.
- `entry.png` — the rendered image.
- `main.ts` — entrypoint (Node 22 stdlib only): copies `entry.png` to `/output/entry.png`, with an empty-file check, byte-count verification, and a sha256 check of the copy.

## Verification

Every story was checked against a reputable source (AP, Reuters, AFP, USGS, ESA, BBC, Yonhap, AAP, Formula 1, Kyiv Independent, …) before use; anything unverifiable or misdated was dropped. Las Vegas motorsport sessions ran on Friday evening local time — Saturday in UTC — and the image says so in its footer.
