# Publishing: LinkedIn carousels and the web page

Everything here is generated from the edition data, in the Evan van Dongen design system
(Paper/Ink tokens, red tab, Archivo stamp lettering, Newsreader, Economist-style charts).

## Every time a major model ships

```bash
cd everyday-ai-index
python3 publish/build.py new gpt-6           # -> editions/001-gpt-6/, data copied from the last edition
```

1. **setups.csv**: add the new model/app as a row (`short_label` ≤ 18 characters, it goes on the charts).
2. **public_scores.csv**: add its independent benchmark scores (Artificial Analysis, METR, LMArena, Terminal-Bench...).
   Refresh the other rows if the leaderboards moved.
3. **harness_scores.csv**: score the app 0–4 with `rubrics/harness_rubric.md`. Re-score apps that shipped updates.
4. **Your tests**: run the battery in every setup, grade blind with `blind.py`, save to `personal_results.csv`.
5. **edition.toml**: write the headline (≤ 6 words, a claim), standfirst and takeaway. Set `highlight` to the setup the post is about.
6. Build:
   ```bash
   python3 publish/build.py                     # method deck + every edition + web page
   ```
7. Check `output/editions/<slug>/scores.md`, then post `output/editions/<slug>/everyday-ai-index-ed<N>.pdf`.
8. Ask Claude to republish `output/site/index.html` to the same artifact link: https://claude.ai/artifact/RMNnfNFoBPEguGgtMC3Euq

## Outputs

| File | What it is |
|---|---|
| `output/method/everyday-ai-index-method.pdf` | Evergreen 8-slide carousel: how the index works |
| `output/editions/<slug>/everyday-ai-index-ed<N>.pdf` | Results carousel for one edition (6–7 slides, built from the scores) |
| `output/*/cover.png` | Slide 1 as a 1080 × 1350 image |
| `output/editions/<slug>/scores.md` | The full score table, for checking numbers before posting |
| `output/site/index.html` | The web page (artifact body): method plus every edition, with an edition switcher |

## LinkedIn notes

- Upload the PDF as a **document** post. Every page is 1080 × 1350 (4:5), the most feed space LinkedIn gives;
  no type is smaller than 24px at export size, so slides stay legible at phone width.
- LinkedIn asks for a document title when you upload: use the edition headline.
- Footers say "Full method and scores: link in the comments": put the web page link in the first comment.
- Results slides are built automatically: cover, ranking, layer breakdown, minutes per finished task,
  a "same model, different app" slide whenever one model appears in two setups, method recap, takeaway.
- `illustrative = true` in edition.toml stamps every slide "Source: illustrative data". Only real editions get posted as results.
- The method deck's harness-swing figures (Terminal-Bench, same model in three harnesses) live in
  `publish/slides.py` (`HARNESS_SWING`). Re-check them against the live leaderboard before re-posting.

## Requirements

Python 3.11+ and Node with Playwright and Chromium (`npm i -g playwright && npx playwright install chromium`).
Fonts are vendored in `assets/fonts/` (SIL Open Font License), so PDFs render the same offline.

## Design-system sync

`assets/tokens.json`, `assets/bundle.css` and `assets/icons/` are copies from the design system artifact.
If the design system changes, re-copy those three and rebuild.
