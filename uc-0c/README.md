# UC-0C — Number That Looks Right

## Overview

This project computes month-over-month (MoM) growth for ward-level budget data while preventing common analytical mistakes like aggregation errors, silent null handling, and assumed formulas.

The system enforces strict validation and produces transparent, audit-ready outputs.

---

## Input File

```
../data/budget/ward_budget.csv
```

### Dataset Details

* 300 rows
* 5 wards
* 5 categories
* Monthly data (Jan–Dec 2024)
* 5 null values in `actual_spend` (intentional)

---

## Output File

```
uc-0c/growth_output.csv
```

Output is strictly:

* Per ward
* Per category
* Per month
  (No aggregation allowed)

---

## Run Command

```bash
python app.py \
  --input ../data/budget/ward_budget.csv \
  --ward "Ward 1 – Kasba" \
  --category "Roads & Pothole Repair" \
  --growth-type MoM \
  --output growth_output.csv
```

---

## Growth Formula

MoM Growth = (Current Month - Previous Month) / Previous Month × 100

---

## Rules Enforced

### 1. No Aggregation

* The system must NOT combine:

  * multiple wards
  * multiple categories
* If attempted → execution is refused

---

### 2. Null Handling

* All null values must be detected before computation
* Growth must NOT be calculated if:

  * current value is NULL
  * previous value is NULL
* Null rows must be flagged with reason from `notes`

---

### 3. Formula Transparency

Each row must include the formula used.

Example:

```
(14.8 - 12.5) / 12.5 × 100
```

---

### 4. Growth Type is Mandatory

* `--growth-type` must be provided
* If missing → system refuses execution
* No default assumption allowed

---

## Core Components

### load_dataset

* Reads CSV file
* Validates required columns
* Detects null rows and reports them

### compute_growth

* Filters by ward and category
* Sorts by period
* Computes MoM growth
* Skips invalid rows (NULL cases)
* Adds formula per row

---

## Known Null Rows

* 2024-03 — Ward 2 – Shivajinagar — Drainage & Flooding
* 2024-07 — Ward 4 – Warje — Roads & Pothole Repair
* 2024-11 — Ward 1 – Kasba — Waste Management
* 2024-08 — Ward 3 – Kothrud — Parks & Greening
* 2024-05 — Ward 5 – Hadapsar — Streetlight Maintenance

---

## Output Format

| period | ward | category | actual_spend | prev_spend | growth_% | formula | status |

---

## Failure Case (Must Be Prevented)

Input:

```
Calculate growth from the data
```

System must:

* Refuse execution
* Ask for:

  * ward
  * category
  * growth-type

---

## Commit Format

```
UC-0C Fix [failure mode]: [reason] → [fix applied]
```

---

## Summary

This project ensures:

* No incorrect aggregation
* Proper null handling
* Transparent calculations
* Strict input validation

Designed for reliable, real-world data analysis.
