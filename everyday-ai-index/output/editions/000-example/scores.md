# Everyday AI Index (profile: everyday)

| # | Setup | Score | A Model | B Harness | C Your tasks | D Cost | Gates | Coverage |
|---|---|---|---|---|---|---|---|---|
| 1 | Frontier closed model in its own full app | **95** | 100 | 100 | 100 | 46 | ok | 100% |
| 2 | Same open model in a strong third-party agent app | **74** | 84 | 77 | 72 | 50 | ok | 100% |
| 3 | Budget small model in a basic app | **56** | 64 | 62 | 41 | 61 | ok | 100% |
| 4 | High-benchmark open model in its own chat app | **41** | 84 | 44 | 40 | 85 | ×0.72 | 100% |
| 5 | Local open model on your laptop | **50** ⚠ | 63 | 27 | – | 100 | ok | 57% |

## Absolute anchors (these don't depend on the field)

| Setup | Success on your tasks | Your minutes per success | Harness rubric (0–100) | METR horizon (h) |
|---|---|---|---|---|
| Frontier closed model in its own full app | 93% | 12.4 | 90 | 14.0 |
| Same open model in a strong third-party agent app | 73% | 20.3 | 69 | 6.0 |
| Budget small model in a basic app | 45% | 40.2 | 56 | 2.0 |
| High-benchmark open model in its own chat app | 45% | 43.8 | 40 | 6.0 |
| Local open model on your laptop | – | – | 24 | – |

## Notes

- **High-benchmark open model in its own chat app**: gates: G1_privacy=concern, G3_honesty=concern
- **Local open model on your laptop**: layer C has no data; its weight was spread over the others; G3 honesty unverified (no personal results); coverage 57% is below 70%: treat as provisional

_Scores are relative to the best setup in this comparison (= 100 per layer). Gaps under ~5 points are noise. ⚠ = provisional (coverage below 70%), ranked after fully evidenced setups._
