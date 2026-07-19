
---

### `skills.md`
```markdown
# skills.md — Complaint Classifier Skills

This document outlines the specific skills implemented to perform accurate citizen complaint classification. These skills are designed to address the specific core failure modes of standard LLMs.

---

## Skill 1: `classify_complaint`

### Description
Analyzes a single complaint description and returns structured results adhering to strict municipal guidelines.

### Logic Flow

[Complaint Description Input] │ ▼ ┌─────────────────────────┐ │ Check Description │ │ for Severity Words │ └────────────┬────────────┘ │ ┌─────────┴─────────┐ ▼ ▼ [Severity found] [Severity NOT found] Priority = Urgent Priority = Standard/Low │ │ └─────────┬─────────┘ │ ▼ ┌─────────────────────────┐ │ Map to exact 10 │ │ Allowed Categories │ └────────────┬────────────┘ │ ▼ ┌─────────────────────────┐ │ Determine Ambiguity │ │ If ambiguous, set flag │ │ to "NEEDS_REVIEW" │ └────────────┬────────────┘ │ ▼ ┌─────────────────────────┐ │ Generate Justification │ │ (Cite specific words) │ └────────────┬────────────┘ │ ▼ [Structured Output Dictionary]


### Constraints Enforced
1. **Taxonomy Enforcement**: Only allows exact strings: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
2. **Severity Blindness Prevention**: Scans the text for safety keywords (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`). If present, priority is instantly upgraded to `Urgent`.
3. **Evidence-Based Reason**: Evaluates and cites keywords from the description in a single-sentence explanation.
4. **Ambiguity Prevention**: Checks if multiple categories match or if description is highly vague, and sets `flag` to `NEEDS_REVIEW` to avoid false confidence.

---

## Skill 2: `batch_classify`

### Description
Orchestrates file-level processing. It reads an input CSV file containing citizen complaints, processes each row using the `classify_complaint` skill, aggregates the outputs, and writes the finalized results into a specified output CSV file.

### Logic Flow
1. **File Input Validation**: Verifies if the file exists and is readable.
2. **Column Inspection**: Identifies the text description column (defaults to `description`, fallback to any text field).
3. **Row-by-Row Execution**: Applies `classify_complaint` to each row. Handles rate-limiting or API failure by automatically falling back to a deterministic, keyword-based local classifier.
4. **Data Standardization**: Ensures that the columns `category`, `priority`, `reason`, and `flag` are generated.
5. **File Output Generation**: Writes the enriched dataframe to `results_[your-city].csv`.
