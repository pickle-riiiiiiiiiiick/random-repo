# Everyday AI Index (EAI)

A way to rate AI tools on one question: **"How much useful work does this get done for me, with how little effort from me?"**

Most leaderboards answer a different question: "How smart is the model when an expert runs it under ideal conditions?" That's a real question, but it isn't the one a daily user is asking. This folder has a method, a config and a small scoring script that answer the first one, and keep answering it as models improve.

---

## 1. Why the leaderboards don't match what you see

You noticed that some models (often Chinese open-weight ones) rank near the top of leaderboards but feel much less useful in practice. That's a real, measurable effect, and there are several causes. None of them require anyone to be cheating.

| Cause | What happens | Evidence (as of Oct 2026) |
|---|---|---|
| **Benchmarks test the model, you use a product** | A leaderboard number is model + expert-built test harness + ideal settings. You get model + whatever app it ships in. The app (tools, memory, files, connectors, recovery from mistakes) is often what decides whether the task gets done. | On Terminal-Bench 2.0 the *same* model moves by 15–20+ points depending on the harness around it ([morphllm](https://www.morphllm.com/terminal-bench-2), [codesota](https://www.codesota.com/benchmark/terminal-bench)). Reviews of agent benchmarks report 11–15 points of scaffold-only variation on SWE-bench Verified ([layer3labs](https://www.layer3labs.io/guides/ai-agent-benchmarks)). |
| **Short, clean tasks hide the gap; long, messy ones expose it** | Most benchmarks are single questions with one right answer. Daily work is multi-step, vague, and full of interruptions. | Epoch AI puts open-weight models about 4 months behind closed models on average, with the gap small on chat preference and **wider on long agentic tasks** ([Epoch](https://epoch.ai/data-insights/open-closed-eci-gap)). |
| **Public tests get trained on** | Once a benchmark is famous, its questions (or close relatives) leak into training data, and labs tune for it. Scores rise faster than real ability. | The Stanford HAI 2026 AI Index found invalid-question rates of 2–42% on major benchmarks ([summary](https://www.tomshardware.com/tech-industry/artificial-intelligence/chinas-open-weight-ai-models-are-now-just-4-months-behind-frontier-us-offerings-mozilla-report-claims-models-still-lag-in-some-benchmarks-but-are-drastically-cheaper-to-use)). |
| **Vendor-reported numbers** | Many headline scores come from the model maker's own launch post, run with their own settings. | Independent re-runs (Artificial Analysis, Epoch, LMArena) regularly come in lower. |
| **Cheap ≠ valued** | Usage share (tokens) looks impressive because cheap models get used for bulk, low-stakes work. What people *pay* for is a better signal of what works on important tasks. | On OpenRouter, Chinese models carry roughly 44% of tokens, but premium closed models capture a far larger share of the money ([fourweekmba](https://fourweekmba.com/ai-openrouter-us-models-token-share-deepseek-volume-revenue-spl/), [tech-insider](https://tech-insider.org/chinese-ai-models-enterprise-share-2026/)). |

**The big caveat:** the opposite also happens. A harness that wins a benchmark isn't necessarily nice to use. On Terminal-Bench, research harnesses beat Claude Code with the *same* Claude model by a wide margin. They were built to win that benchmark, not to ask permission before deleting your files or to keep your project memory. So **"harness strength on a benchmark" and "harness usability" are separate things, and this index measures them separately.**

> **Disclosure:** this framework was written by Claude, an Anthropic model. That's one reason it's built so that **your own blind tests (Layer C) carry real weight** and the harness rubric uses observable checklists, not impressions. If Claude really is more useful to you, the method will show it. If it isn't, the method should show that too.

---

## 2. What you rate: a *setup*, not a model

The unit of evaluation is a **setup** = model + the product you reach it through.

Examples:
- *Claude Opus (latest) in the Claude desktop app*
- *GPT (latest) in ChatGPT*
- *Kimi / GLM / DeepSeek / Qwen through their own chat app*
- *Same Chinese model through a third-party harness (e.g. Cline, OpenRouter chat, Cursor)*
- *A local open model in LM Studio*

The same model in two products counts as two setups. That's the whole point.

---

## 3. The structure: three layers plus gates

```
                     ┌──────────────────────────────────────────────┐
  EVERYDAY SCORE  =  │  A. Model capability       (public benchmarks) │  25%
   (0–100, relative  │  B. Harness usability      (your rubric)       │  35%
    to current field)│  C. Your reality check     (your blind tasks)  │  30%
                     │  D. Cost & friction        (price, limits)     │  10%
                     └──────────────────────────────────────────────┘
                       then  ×  GATES  (privacy, reliability, honesty)
```

These are the default weights for the **"everyday user"** profile. Other profiles are in `config/weights.toml` (developer, power user, budget/privacy-first). You can change any weight in one line.

### Layer A: Model capability (25%)

Here only *independently run* benchmarks count, and only ones that test **finishing real work**, not exam answers. Benchmarks sit in **slots**. A slot is a *capability* that stays fixed; the benchmark that fills it gets swapped when it goes stale (see §5). Current picks:

| Slot | Why it matters for daily use | Current benchmark (Oct 2026) | Weight in A |
|---|---|---|---|
| **A1 Knowledge-work deliverables** | "Write the memo / build the spreadsheet / draft the plan" judged by experts against human work | **GDPval** (or the independent GDPval-AA re-run) | 20% |
| **A2 Doesn't make things up** | The #1 source of wasted time and real harm for a non-expert, who can't easily catch errors | **AA-Omniscience** (non-hallucination score), SimpleQA-style factuality | 20% |
| **A3 Multi-step tool use with a person** | Following rules, using tools, handling a customer-like conversation without going off the rails | **τ²/τ³-bench** | 15% |
| **A4 Long autonomous work** | How long a task it can carry to the end without you rescuing it | **METR time horizon** (50% and 80%) | 15% |
| **A5 Human preference, style-controlled** | Do people, blind, prefer its answers? | **LMArena** text (style control on), WebDev Arena | 15% |
| **A6 Computer / terminal agency** | Operating a computer, files, software | **Terminal-Bench 2.x**, **OSWorld-Verified** | 10% |
| **A7 Long documents** | Reading and reasoning over your long PDFs and contracts | **AA-LCR** / MRCR | 5% |

**Deliberately left out:** MMLU, GPQA, AIME, Humanity's Last Exam and similar. They measure academic ceilings, they're mostly saturated or contaminated, and a high score there barely predicts whether your Tuesday goes better. (A developer profile can add SWE-bench Pro.)

**Normalisation:** each benchmark is scored **relative to the best setup in the current field** (best = 100). Percent scores use a simple ratio, Arena ratings use the chance of beating the leader, and time horizons count how many doublings behind the leader a model is. Section 5 explains why this keeps the index from ever "maxing out".

### Layer B: Harness usability (35%), the part leaderboards ignore

Scored with an **anchored 0–4 checklist** (`rubrics/harness_rubric.md`). Each level is defined by things you can observe, like "can it read a PDF I drop in?" or "does it ask before deleting?", so two people scoring the same app should land within a point.

| Code | Dimension | Weight in B |
|---|---|---|
| B1 | **Gets it done end-to-end**: can it go from request to a usable result (file, sent draft, working code) without you copy-pasting between apps? | 18% |
| B2 | **Built-in tools**: web search with citations, code execution, file reading (PDF, images, spreadsheets), file creation | 14% |
| B3 | **Connects to your stuff**: email, calendar, drive, notes; open connector standard (MCP) | 12% |
| B4 | **Remembers context**: projects, memory, custom instructions, long conversations that don't fall apart | 12% |
| B5 | **Recovers from mistakes**: notices errors, checks its own work, fixes them when told, doesn't loop | 12% |
| B6 | **Safe control**: asks before risky actions, undo/versions, clear about what it did | 10% |
| B7 | **Speed & reliability**: latency, uptime, rate limits, no truncated answers | 10% |
| B8 | **Works everywhere you are**: web, desktop, phone, voice; sync between them | 6% |
| B9 | **Low learning curve**: does a non-expert get good results without prompt tricks? | 6% |

### Layer C: Your reality check (30%), the anchor

A **personal task battery** of 12–20 tasks taken from *your actual life* (`tasks/personal_battery.toml` has a starter set). You run every task in every setup, then **grade blind**: `blind.py` strips the setup names and shuffles the outputs.

For each task, record:
- **Outcome**: 0 = failed / unusable, 1 = usable after fixing, 2 = usable as-is
- **Your minutes**: total time you spent, including prompting, checking and fixing
- **Nudges**: how many follow-up messages it needed
- **Errors found**: factual or logic mistakes you caught

These roll up into two numbers:
- **Success rate** (weighted by outcome)
- **Minutes of your time per successful task**: the metric that matters most and **never saturates**. A perfect AI drives it toward zero, and you can always tell which one is closer.

This layer is what beats benchmark gaming. Nobody can train on *your* tasks.

### Layer D: Cost & friction (10%)

What you actually pay per month for the tier you'd use, plus hard limits (message caps, context limits, regional availability). Scored relative to the field.

### Gates (multipliers, not points)

Some problems can't be outweighed by being good elsewhere. Each gate multiplies the final score:

| Gate | Pass ×1.0 | Concern ×0.85 | Fail ×0.5 |
|---|---|---|---|
| **G1 Privacy / data jurisdiction**: where your data goes, whether it trains on it, which country's law governs it | Clear policy, opt-out, jurisdiction you accept | Unclear policy | Data goes somewhere you've decided is unacceptable for your use |
| **G2 Reliability**: works when you need it | <1 failed session / week | Frequent errors / caps | Regularly unusable |
| **G3 Honesty**: admits uncertainty, doesn't invent sources | Invented sources in 0 of your battery tasks | 1–2 tasks | 3+ tasks |

Gates are personal. Someone handling legal or health documents should set G1 strictly; someone generating party invitations might not care.

---

## 4. Weighting profiles

Defaults in `config/weights.toml`:

| Profile | A Model | B Harness | C Your tasks | D Cost | Who it's for |
|---|---|---|---|---|---|
| **everyday** (default) | 25 | 35 | 30 | 10 | Non-expert, uses AI through apps for work and life |
| **power_user** | 30 | 30 | 30 | 10 | Uses projects, connectors, agents regularly |
| **developer** | 35 | 25 | 30 | 10 | Codes through CLIs and IDEs; adds SWE-bench Pro and Terminal-Bench weight |
| **budget_privacy** | 20 | 25 | 30 | 25 | Price-sensitive or must self-host; G1 strict |

Why harness gets the biggest share for everyday users: an expert can work around a weak harness by building their own scaffolding. A daily user can't, so for them the harness *is* the experience.

---

## 5. Making it future-proof

Leaderboards die in three ways: tests saturate (everyone gets 95%), tests leak (models memorise them), and the important skills change (2023: chat; 2026: agents; later: who knows). The index handles each one:

1. **Slots are permanent, benchmarks are replaceable.** "Doesn't make things up" will matter in 2030 even after AA-Omniscience is retired. `config/benchmarks.toml` lists the current benchmark per slot and its successor candidates.

2. **Explicit retirement rules.** A benchmark gets dropped from its slot when any of these is true:
   - the top setup scores >90%, or the top 3 are within the benchmark's noise margin (saturated)
   - there's credible evidence of contamination
   - it's only available as vendor-reported numbers
   - it hasn't been updated or re-run on new models for 6+ months

   **Replacement criteria:** outcome-based (did the task get done?), independently run, held-out or refreshed regularly, harness disclosed, top score below about 70% when adopted.

3. **Relative scoring.** Every number is "position within today's field", so the index never tops out. When all models get better, the scale moves with them.

4. **Unbounded human-centred anchors.** Alongside the relative score, track two absolute numbers that keep meaning something forever:
   - **Your minutes per successful task** (→ 0 is ideal)
   - **Longest task it reliably finishes alone** (METR-style horizon; it has gone from minutes in 2024 to hours in 2026 and keeps doubling)

5. **Your battery grows with you.** Every time an AI fails at something you actually needed, add that task to the battery. Once all setups pass a task twice in a row, move it to a "retired" list. The battery keeps drifting toward the edge of what AI can do *for you*.

6. **Slots get added, not just swapped.** Review once a quarter (or when a major model ships) and ask: "Is there a new kind of thing I now expect AI to do?" (for example, phone calls on my behalf, or week-long projects). If so, add a slot to B or A and take its weight from the slot that changed least.

---

## 6. How to run it (about 3 hours per quarter)

1. **Pick 3–6 setups** to compare. Write them in `data/setups.csv`.
2. **Fill in Layer A** from independent leaderboards (Artificial Analysis, Epoch AI, LMArena, METR, Terminal-Bench, GDPval) into `data/public_scores.csv`. Leave a cell blank if there's no data. The scorer re-weights around gaps and reports **coverage** so you can see how much of a score is backed by evidence.
3. **Score Layer B**: spend 20–30 minutes in each app with `rubrics/harness_rubric.md` open and record 0–4 per dimension in `data/harness_scores.csv`.
4. **Run Layer C**: run your battery in every setup and save each output as `outputs/<setup_id>/<task_id>.md`. While you run, log your minutes and number of follow-ups per task in `data/run_log.csv`. Then:
   ```bash
   python3 blind.py make outputs/ blinded/          # strips names, shuffles
   # grade blinded/grading.csv: outcome 0/1/2, errors, invented_source
   python3 blind.py merge blinded/ --run-log data/run_log.csv --out data/personal_results.csv
   ```
5. **Fill in cost and gates** in `data/setups.csv`.
6. **Score:**
   ```bash
   python3 score.py --data data/ --profile everyday
   ```
   You get a ranked table, a per-layer breakdown, coverage, and the two absolute anchors.

To see it working right away with made-up example data:
```bash
python3 score.py --data data/example --profile everyday
```
(The example uses fictional setups on purpose. It doesn't contain real scores for real products.)

Example output (fictional data):

```
| # | Setup                                              | Score | A Model | B Harness | C Your tasks | D Cost | Gates | Coverage |
|---|----------------------------------------------------|-------|---------|-----------|--------------|--------|-------|----------|
| 1 | Frontier closed model in its own full app          | 95    | 100     | 100       | 100          | 46     | ok    | 100%     |
| 2 | Same open model in a strong third-party agent app  | 74    | 84      | 77        | 72           | 50     | ok    | 100%     |
| 3 | Budget small model in a basic app                  | 56    | 64      | 62        | 41           | 61     | ok    | 100%     |
| 4 | High-benchmark open model in its own chat app      | 41    | 84      | 44        | 40           | 85     | ×0.72 | 100%     |
| 5 | Local open model on your laptop                    | 50 ⚠  | 63      | 27        | –            | 100    | ok    | 57%      |
```

Rows 2 and 4 are the **same model** (identical Layer A). The harness alone moves it from 41 to 74. Row 5 is marked ⚠ provisional and ranked last because you haven't run your own tasks on it yet: a setup can't climb the table just because a weak spot was never measured.

---

## 7. Reading the result

- **Look at the layer breakdown, not just the total.** "High A, low B" means a strong model trapped in a weak product. Worth checking whether a better harness exists for it (e.g. a Chinese model through a good third-party agent app).
- **Coverage below 70%** (⚠) means the score leans too heavily on missing data. It's ranked after fully evidenced setups. Treat it as provisional.
- **Gaps under about 5 points are noise.** Choose on cost or preference instead.
- **When your Layer C disagrees with Layer A, believe Layer C.** For you, it's the ground truth.

---

## Files

| Path | What it is |
|---|---|
| `config/weights.toml` | Layer and dimension weights, profiles, gate multipliers |
| `config/benchmarks.toml` | Slots, current benchmarks, successors, retirement rules |
| `rubrics/harness_rubric.md` | Anchored 0–4 checklist for Layer B |
| `tasks/personal_battery.toml` | Starter task battery (edit to fit your life) |
| `data/*.csv` | Your data (empty templates) |
| `data/example/*.csv` | Fictional example data |
| `score.py` | Computes the index (Python 3.11+, no dependencies) |
| `blind.py` | Anonymises and shuffles outputs for blind grading |
| `tests/` | Tests for the scorer |

Sources consulted (Oct 2026) are linked inline. Some secondary sources were the only ones reachable, so check headline numbers against the primary leaderboards before relying on them.
