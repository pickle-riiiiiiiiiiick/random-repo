# ARCHIMED Investment Director case study: Project Lumière

A practice buyout case for an Investment Director interview at ARCHIMED, the healthcare private equity firm. Project Lumière and all of its figures are fictional.

- **Case brief and model answer:** [ARCHIMED Investment Director Case Study](https://claude.ai/code/artifact/e0da298b-7815-4cf1-9da0-8b52a2c28d3d). This is a Claude Docs page and is private to its owner unless shared.
- **Model:** `Project_Lumiere_LBO.xlsx` has eight tabs and 1,782 live formulas, with no circular references.

## Headline answer

Go to round 2 at €540m upfront, which is 13.5x underwritten FY2026E EBITDA of €40.0m. Add an earn-out of up to €40m. Walk away above €560m upfront. The vendor's €600m is 15.0x our EBITDA.

| Exit at end of FY2031 | Base | Management | Downside |
| --- | --- | --- | --- |
| IRR | 20.0% | 24.0% | 3.3% |
| MOIC | 2.49x | 2.93x | 1.18x |

## Using the model

- Change only the **Inputs** tab. Blue text is an input, yellow cells are the levers to flex, black is a formula and green is a link to another tab.
- The three cases run side by side on `LBO_Base`, `LBO_Mgmt` and `LBO_Down`. The `Returns` tab holds the comparison, value bridge, bid ladder and sensitivity grids.
- Useful levers on Inputs:
  - entry multiple: C9
  - leverage: C28
  - earn-out: C21
  - growth and margin flex: C52–C53
  - exit multiples: D59–F59
- `Returns!C87` shows 1 when every model check passes.
