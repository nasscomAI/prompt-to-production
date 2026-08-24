# UC-0A — CRAFT log

## C — Context established
Naive prompt used as the baseline:

> "Classify this citizen complaint by category and priority."

Nothing in that prompt names the taxonomy, defines Urgent, or requires a justification.
Every failure below follows from that absence, not from the model being weak.

## R — Run, and what broke

| # | Failure mode | Where it shows up in `test_pune.csv` | Root cause in the naive prompt |
|---|---|---|---|
| 1 | Taxonomy drift | `PM-202406` (underpass flooded) and `PM-202427` (bridge approach floods) describe the same defect type; nothing pins both to the string `Flooding`, so one becomes `Waterlogging` | no closed value list |
| 2 | Severity blindness | `PM-202402` "School children at risk" reads as a routine pothole. `PM-202446` "Elderly resident fell last week" reads as routine footpath wear | "priority" left undefined |
| 3 | Missing justification | no `reason` column is produced at all, so no classification can be audited | output shape never specified |
| 4 | Hallucinated sub-category | `PM-202401` "Large pothole 60cm wide" invites `Pothole - Major` / `Pothole (Severe)` | severity felt in the text with nowhere legal to put it |
| 5 | False confidence on ambiguity | `PM-202408` "Bus stand flooded … Drain blocked" gets one confident label and the second defect silently disappears | no refusal or flagging path |
| 6 | Setting classified instead of defect | `PM-202430` "Heritage street, lights out" invites `Heritage Damage` — but nothing is damaged about the heritage structure; the lights are out | no rule separating backdrop from defect |

## A — Adjusted: the enforcement rules that close each one

| Failure | Enforcement rule added to `agents.md` | Executable form in `classifier.py` |
|---|---|---|
| 1, 4 | category must be exactly one of the ten strings, no pluralisation or sub-categories | `CATEGORIES` tuple + `assert category in CATEGORIES` |
| 2 | the nine severity terms force Urgent, overriding all else | `SEVERITY_PATTERNS`, checked before priority is assigned |
| 3 | every row's reason must cite words copied from that description | reason is built from `match.group(0)` — a literal substring by construction |
| 5 | two explicit defect phrases → first-mentioned wins **and** `NEEDS_REVIEW`, runner-up named | `_find_categories` sorts by match position; `competing` list drives the flag |
| 6 | a signal counts only when it names the defect, not the setting | no bare `\broad\b` or `\bheritage\b`; Heritage Damage requires a heritage word *and* a damage verb in the same sentence |
| — | priority must never be raised from `days_open` or `reported_by` | `classify_complaint` never reads those two fields |

## F — Fixed, then tested

```
$ python3 classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
Wrote results_pune.csv
  rows in / out : 15 / 15
  urgent        : 4
  needs review  : 1
    Pothole          2
    Flooding         3
    Streetlight      3
    Waste            3
    Noise            1
    Road Damage      3
```

All 4 severity-signal rows returned Urgent, and only those 4:

| Row | Severity term matched | Priority |
|---|---|---|
| PM-202402 | "children", "School" | Urgent |
| PM-202411 | "hazard" | Urgent |
| PM-202420 | "injury" | Urgent |
| PM-202446 | "fell" | Urgent |

One row flagged, and it is the intended one — `PM-202408`, classified `Flooding`
(first-mentioned defect) with `Drain Blockage` named in the reason rather than dropped.

## T — Tested against adversarial input

The severity check is word-boundary matched, not substring matched. A substring
implementation passes the happy path and then silently misfires in production:

```
$ cat edge.csv
complaint_id,description
X-1,
X-2,"Nothing much happened here"
X-3,"Fellow resident fired a query about the firearm shop"

$ python3 classifier.py --input edge.csv --output edge_out.csv
  rows in / out : 3 / 3
  urgent        : 0
  needs review  : 3
```

- `X-3` contains the substrings `fell`, `fire` and `fire` again — a naive
  `if "fell" in description` marks it Urgent. Word boundaries return Standard. Correct.
- `X-1` has no description: emitted as `Other` / `NEEDS_REVIEW`, not dropped.
- `X-2` matches no category: refused with `Other` / `NEEDS_REVIEW` rather than pushed
  into the nearest-looking bucket.
- `rows in == rows out` in every case, which is what makes "no complaint was lost"
  checkable instead of assumed.

## The rule the AI would not have written unprompted

> "A category signal counts only when the description names the defect, not merely the
> setting. 'Heritage street, lights out' is a Streetlight defect in a heritage setting."

Keyword classification is inherently blind to the difference between what a complaint
is *about* and where it *happened*. Every generated draft treated a location noun as
evidence. This rule had to be written by hand.
