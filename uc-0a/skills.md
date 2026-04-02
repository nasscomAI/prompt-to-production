# UC-0A Skills: Civic Complaint Tooling

**Core failure modes:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

The AI workflow requires these two exact capabilities to process the data successfully:

---

## `classify_complaint`
**Description:** Evaluates a single citizen complaint to generate structured insights based on the RICE rules.

**Input:** A single complaint string description (one row from the CSV).

**Output Properties:**

| Field | Allowed Values | Rule |
|---|---|---|
| `category` | `Pothole` · `Flooding` · `Streetlight` · `Waste` · `Noise` · `Road Damage` · `Heritage Damage` · `Heat Hazard` · `Drain Blockage` · `Other` | Exact strings only — no variations |
| `priority` | `Urgent` · `Standard` · `Low` | Forced to `Urgent` if severity keywords are present |
| `reason` | One sentence | Must cite specific words from the description |
| `flag` | `NEEDS_REVIEW` or blank | Set when category is genuinely ambiguous |

**Severity keywords that MUST trigger Urgent:**
`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`

---

## `batch_classify`
**Description:** The bulk processing engine that applies classification synchronously across datasets.

**Behavior:**
- Opens and reads an input CSV file containing citizen complaints (e.g., `../data/city-test-files/test_pune.csv`).
- Iterates row-by-row, passing each description into `classify_complaint`.
- Formats the outputs and writes cleanly into the targeted output CSV (e.g., `results_pune.csv`) while maintaining all data structures.

**Run Command:**
```bash
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
```

---

## Known Naive-Prompt Failures
Running a bare `"Classify this citizen complaint by category and priority."` prompt will produce these errors:
1. Category names that vary across rows for the same type of complaint (taxonomy drift)
2. Injury/child/school complaints classified as Standard instead of Urgent (severity blindness)
3. No `reason` field in the output (missing justification)
4. Category names that are not in the allowed list (hallucinated sub-categories)
5. Confident classification on genuinely ambiguous complaints (false confidence)
