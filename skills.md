# skills.md — UC-0C: Number That Looks Right

## Skill Set for BudgetAnalysisAgent

---

### Skill 1: load_budget_data
**Purpose:** Load and validate `ward_budget.csv`  
**Input:** File path (string)  
**Output:** Pandas DataFrame  
**Rules:**
- Confirm required columns exist: `ward`, `category`, `year`, `amount`
- Strip whitespace from string columns
- Cast `year` to int, `amount` to float
- Raise clear error if file not found or columns missing

---

### Skill 2: compute_growth_per_ward_category
**Purpose:** Calculate year-on-year growth strictly per ward per category  
**Input:** Validated DataFrame  
**Output:** DataFrame with growth metrics  
**Rules:**
- Group ONLY by `['ward', 'category']`
- Within each group, sort by `year` ascending
- Compute `change = current_amount - previous_amount`
- Compute `growth_pct = (change / previous_amount) * 100`
- If previous_amount is 0 or missing → set both to `N/A`
- Add `trend` column: `GROWTH` if change > 0, `DECLINE` if < 0, `NO_CHANGE` if == 0

---

### Skill 3: flag_anomalies
**Purpose:** Highlight suspicious budget entries  
**Input:** Growth DataFrame  
**Output:** Same DataFrame with `anomaly_flag` column  
**Rules:**
- Flag `HIGH_GROWTH` if growth_pct > 100%
- Flag `HIGH_DECLINE` if growth_pct < -50%
- Flag `MISSING_PRIOR_YEAR` if previous year data absent
- Otherwise: `OK`

---

### Skill 4: export_results
**Purpose:** Write final output to CSV  
**Input:** Final DataFrame  
**Output:** `growth_output.csv` in working directory  
**Rules:**
- File must be named exactly `growth_output.csv`
- Sort by: `ward` ASC, `category` ASC, `year` DESC
- Do not include DataFrame index in output
- Print row count and file path on success

---

### Skill 5: run_self_check
**Purpose:** Validate output before saving (CRAFT enforcement)  
**Rules:**
- Assert no row has multiple wards (i.e., ward column contains no comma or slash)
- Assert no row has multiple categories
- Assert growth_pct formula is correct for a sample row
- Print PASS/FAIL for each check
