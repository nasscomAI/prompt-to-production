# UC-0A — Complaint Classifier

Classifies city complaints into: **sanitation**, **roads**, **water**, **electricity**, **others** using rule-based keyword matching. Outputs structured JSON.

## How to Run

From the project root:

```bash
cd uc-0a
python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.json
```

Or with CSV output:

```bash
python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv --format csv
```

**Requirements:** Python 3.8+, standard library only (csv, json, re, pathlib).

---

## Your Input File
```
../data/city-test-files/test_[your-city].csv
```
15 rows per city. `category` and `priority_flag` columns are stripped — you must classify them.

## Your Output File
```
uc-0a/results_[your-city].csv
```

## Run Command
```bash
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
```

---

## Classification Schema — Your Enforcement Must Reference These Exactly

| Field | Allowed values | Rule |
|---|---|---|
| `category` | Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other | Exact strings only — no variations |
| `priority` | Urgent · Standard · Low | Urgent if severity keywords present |
| `reason` | One sentence | Must cite specific words from description |
| `flag` | NEEDS_REVIEW or blank | Set when category is genuinely ambiguous |

**Severity keywords that must trigger Urgent:**
`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`

---

## Skills to Define in skills.md
- `classify_complaint` — one complaint row in → category + priority + reason + flag out
- `batch_classify` — reads input CSV, applies classify_complaint per row, writes output CSV

---

## What Will Fail From the Naive Prompt
Run `"Classify this citizen complaint by category and priority."` first.
Then look for:
1. Category names that vary across rows for the same type of complaint
2. Injury/child/school complaints classified as Standard instead of Urgent
3. No reason field in the output
4. Category names that are not in the allowed list above
5. Confident classification on genuinely ambiguous complaints

---

## Commit Formula
```
UC-0A Fix [failure mode]: [why it failed] → [what you changed]
```
