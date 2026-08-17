# UC-0C — CRAFT log

## C — What "wrong" means in this UC

In UC-0A a failure is a mislabelled row; someone notices. Here a failure is a plausible
percentage that gets read out in a council meeting. Nobody can tell a fabricated −34.8%
from a real one by looking at it. So every rule below exists to make a number either
**re-derivable** or **absent** — never quietly approximate.

## R — Run: `"Calculate growth from the data."` on the full CSV

| Failure mode | What comes back | Why it is dangerous |
|---|---|---|
| Wrong aggregation level | one city-wide figure across all 300 rows — 5 wards × 5 categories × 12 months collapsed to a single percentage | Ward 1 Roads is +33.1% in July while Ward 1 Roads is −34.8% in October; a blended number describes no ward's actual situation and cannot be acted on |
| Silent null handling | the 5 blank `actual_spend` cells become `0.0` in a `float()` or a `sum()` | a ward that did not submit figures is reported as a ward that spent nothing. July for Ward 4 Warje shows a −100% collapse that never happened |
| Formula assumption | MoM is picked without being asked | MoM and YoY are different claims. The user was never told which one they got |
| The one nobody looks for | growth computed for the month **after** a null, against the missing base — or worse, reaching back to the last non-null month and presenting a 2-month change as monthly | this row carries no null of its own, so every "did you handle nulls?" check passes while the number is still fabricated |

## A — Enforcement rules, and what makes each one testable

| Rule | Mechanism | Verified by |
|---|---|---|
| never aggregate | `--ward`/`--category` have no defaults; `AGGREGATION_TOKENS` rejects `ALL`/`*`/`total`/`citywide` | refusal tests 2 and 3 below |
| refuse a guessed formula | `--growth-type` has no default; refused before any computation | refusal test 1, exit code 1 |
| flag nulls with their reason | blank `actual_spend` → `None`, **never** `0.0`; the `notes` text is copied into the output row | 5 × `NULL_ACTUAL`, each carrying its note |
| never compute against a missing base | `series.get(previous_key)` only — there is no fallback search backwards | 5 × `NULL_BASE` |
| show the formula | operands substituted into the `formula` column per row | `MoM = (19.7 - 14.8) / 14.8 x 100 = +33.1%` |
| every row scoped | `ward` and `category` are columns on every row, never "All" | no row in `growth_output.csv` has a blank scope |
| unknown ward/category | refuses and lists the real values | refusal test 4 |
| missing history | `INSUFFICIENT_HISTORY` per row, not `0%` | YoY test below |

The decision that carries the most weight is one line — `actual = None` instead of
`actual = 0.0` for a blank cell. Every other null rule follows from it. `0.0` is an
assertion that the ward spent nothing; `None` is the truth, which is that we do not know.

## F — Reference values reproduced exactly

```
$ python3 app.py --input ../data/budget/ward_budget.csv \
      --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
      --growth-type MoM --output growth_output.csv

2024-07 · 19.7 vs 14.8 · +33.1 · MoM = (19.7 - 14.8) / 14.8 x 100 = +33.1%   OK
2024-10 · 13.1 vs 20.1 · -34.8 · MoM = (13.1 - 20.1) / 20.1 x 100 = -34.8%   OK
```

Both match the README reference table (+33.1% monsoon spike, −34.8% post-monsoon).
`2024-01` is `NO_BASE`, not `0%`, because December 2023 is not in the dataset.

## The full table

`growth_output.csv` is generated with `--all-series`: all 25 ward × category series,
every row still scoped to exactly one ward and one category. This is not aggregation —
it is 25 separate series in one file, which is what lets all 5 nulls appear in a single
artefact.

```
  rows written : 300
    NO_BASE               25    <- January of each of the 25 series
    NULL_ACTUAL            5    <- the 5 deliberate nulls
    NULL_BASE              5    <- the month AFTER each null
    OK                   265
```

300 rows in, 300 rows out. The 5 `NULL_ACTUAL` rows are exactly the 5 the README names:

| Period | Ward | Category | Note carried into the output |
|---|---|---|---|
| 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding | Data not submitted by ward office |
| 2024-05 | Ward 5 – Hadapsar | Streetlight Maintenance | Equipment procurement delay |
| 2024-07 | Ward 4 – Warje | Roads & Pothole Repair | Audit freeze — figures under review |
| 2024-08 | Ward 3 – Kothrud | Parks & Greening | Project suspended — pending approval |
| 2024-11 | Ward 1 – Kasba | Waste Management | Contractor change — billing delayed |

And the contamination is contained — the reason propagates to the row it poisons:

```
2024-06  10.3  12.5  2024-05  11.3  +10.6  MoM = (12.5 - 11.3) / 11.3 x 100  OK
2024-07  10.3    --  2024-06    --      -  actual_spend missing               NULL_ACTUAL  Audit freeze — figures under review
2024-08  10.3  16.0  2024-07    --      -  base period has no actual_spend;   NULL_BASE    Audit freeze — figures under review
                                           growth against a missing base
                                           would be fabricated
```

August's `actual_spend` of 16.0 is perfectly present. A null-checking implementation that
only inspects the current row emits a confident August figure here. There is no honest
monthly growth for August, and the output says so.

## T — Refusals tested

```
1. --growth-type omitted
   REFUSED: --growth-type was not specified.
            MoM and YoY are different claims about the same numbers and this
            tool will not choose for you.
   exit code = 1

2. --ward omitted
   REFUSED: --ward was not specified.
            This tool will not aggregate across wards or categories — a single
            combined growth figure hides the per-ward variation that the figure
            is used to decide on.
            wards      : ['Ward 1 – Kasba', ... 'Ward 5 – Hadapsar']

3. --ward ALL
   REFUSED: --ward='ALL' is an aggregation request.

4. --ward "Ward 9 – Nagercoil"
   REFUSED: ward 'Ward 9 – Nagercoil' is not present in the data.
            available wards: ['Ward 1 – Kasba', ... 'Ward 5 – Hadapsar']

5. --growth-type YoY against a single-year dataset
   rows written : 12
     INSUFFICIENT_HISTORY  12
```

Every refusal exits non-zero and writes no partial file. Case 5 is the one worth noting:
YoY on 2024-only data could plausibly return `0.0%` for all 12 months, which is a real
number describing nothing. It reports `INSUFFICIENT_HISTORY` per row instead.

## The rule the AI would not have written unprompted

> "A period whose comparison base is null must be flagged NULL_BASE with an empty
> growth_pct. Computing growth against a missing base, or silently reaching back to the
> last non-null period, produces a number that looks right and is not."

Every generated draft handled the null *cell*. None handled the null's *shadow* — the
next period, whose own data is complete and whose growth figure is nonetheless
un-computable. "Handle missing values" is the instruction everyone writes; it is not the
same instruction as this one.
