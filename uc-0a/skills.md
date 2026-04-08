# skills.md — UC-0A Complaint Classifier Skills

This file defines the core skills used by the complaint classification system. Reference [agents.md](agents.md) and [README.md](README.md) for enforcement rules, schema, and failure modes.

---

## Skills

### Skill 1: `classify_complaint`

**Description:**
Classify a single citizen complaint row into category, priority, reason, and ambiguity flag using strict taxonomy enforcement and severity keyword matching.

**Input:**

```
{
  description: string  # Raw complaint text from input CSV
}
```

**Output:**

```
{
  category: string,     # One of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  priority: string,     # One of: Urgent, Standard, Low
  reason: string,       # One sentence citing specific words from description
  flag: string          # Either "NEEDS_REVIEW" or empty string ""
}
```

**Processing Rules:**

1. **Severity Keyword Scan (FIRST)**
   - Scan description for: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`
   - If ANY keyword found → priority = "Urgent"
   - If NO keywords found → priority = "Standard" (default)
   - Assign "Low" only for genuinely minor issues

2. **Category Assignment**
   - Analyze complaint content
   - Match to EXACTLY ONE category from allowed list
   - Use exact string values only — no variations
   - If no clear match → category = "Other"
   - Never create new category values

3. **Justification Generation**
   - Write exactly ONE sentence
   - MUST cite specific words, phrases, or details from the original description
   - Example: "Classified as Pothole because description mentions 'large crater in the middle of the road'"
   - Bad example: "This is clearly a pothole complaint"

4. **Ambiguity Assessment**
   - Evaluate if complaint objectively fits multiple categories equally
   - Set flag = "NEEDS_REVIEW" ONLY if ambiguity is genuine
   - Do NOT set flag for subjective difficulty
   - Example: Complaint mentions both "flooding" AND "clogged drain" → flag it
   - Example: Complaint clearly about streetlight malfunction → no flag

**Error Handling:**

- If description is blank or nonsensical → REFUSE classification, return error
- If category cannot be determined → use "Other" (do not hallucinate)
- If severity keyword match is unclear → default to "Standard" priority
- If ambiguity cannot be objectively assessed → do not set flag

**Validation Checklist (before output):**

- ✓ Category is in allowed list (10 defined categories OR "Other")
- ✓ Priority matches severity keyword rules
- ✓ Reason is one sentence with specific citations
- ✓ Flag is either "NEEDS_REVIEW" or empty string
- ✓ No hallucinated values or creative phrasings

---

### Skill 2: `batch_classify`

**Description:**
Process an entire CSV file of complaint descriptions and output a classified CSV with category, priority, reason, and flag columns for all rows.

**Input:**

```
{
  input_file: string,    # Path to input CSV (e.g., "../data/city-test-files/test_pune.csv")
  output_file: string    # Path to output CSV (e.g., "results_pune.csv")
}
```

**Input CSV Format:**

- Must contain a column with complaint descriptions
- Typically 15 rows per city
- Column name should be identifiable as description/complaint/text

**Output:**

```
CSV file with columns: description, category, priority, reason, flag
```

**Output CSV Format:**

- One row per input complaint
- Columns in order: description | category | priority | reason | flag
- All classifications must match `classify_complaint` rules
- No rows dropped or lost
- File must be valid and readable

**Processing Rules:**

1. **CSV Reading**
   - Read input file with proper encoding (UTF-8)
   - Identify description column (may have various names)
   - Handle missing or malformed rows gracefully

2. **Row Processing**
   - For each row in input CSV:
     - Apply `classify_complaint` skill to the description
     - Collect returned category, priority, reason, flag
     - Write to output row

3. **Consistency Checking**
   - Verify same complaint type across multiple rows uses IDENTICAL category strings
   - Example: If row 1 says "Pothole" and row 5 is similar, row 5 MUST also say "Pothole" (not "Potholes")
   - Flag manually if inconsistency detected

4. **Output CSV Writing**
   - Write all rows with proper CSV formatting
   - Preserve description text exactly as input
   - Include all output columns (category, priority, reason, flag)
   - Handle special characters and quotes properly

**Error Handling:**

- If input file not found → return error with file path
- If input CSV is malformed → attempt recovery or return detailed error
- If a single row classification fails → log error with row number and skip or flag
- If output file cannot be written → return error
- If data loss occurs → return warning/error

**Validation Checklist (before completion):**

- ✓ All input rows processed (count matches)
- ✓ No empty category values in output
- ✓ All priority assignments match severity keyword rules
- ✓ All reason fields cite specific words from descriptions
- ✓ Flag values are either "NEEDS_REVIEW" or empty
- ✓ Same complaint types use identical category strings across rows
- ✓ Output CSV valid and parseable
- ✓ No data loss — all 15 rows present

**Run Example:**

```bash
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
```

---

## Failure Mode Prevention

Each skill integrates safeguards against core failure modes:

| Failure Mode                | Prevention                                                                                             |
| --------------------------- | ------------------------------------------------------------------------------------------------------ |
| Taxonomy Drift              | `classify_complaint` enforces exact string matching; `batch_classify` verifies consistency across rows |
| Severity Blindness          | `classify_complaint` scans for keywords FIRST before category assignment                               |
| Missing Justification       | `classify_complaint` requires one-sentence citations of specific text                                  |
| Hallucinated Sub-categories | Both skills reject values outside defined taxonomy                                                     |
| False Confidence            | `classify_complaint` provides ambiguity flag; `batch_classify` logs confidence warnings                |

---

## Schema Reference

See [README.md](README.md) for:

- **Allowed Categories:** Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
- **Severity Keywords:** injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
- **Priority Values:** Urgent, Standard, Low
- **Test Data:** 15 rows per city (Pune, Ahmedabad, Hyderabad, Kolkata)
