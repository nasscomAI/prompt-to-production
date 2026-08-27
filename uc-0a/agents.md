# agents.md — UC-0A Complaint Classifier

## Overview

This document defines the complaint classification agents for UC-0A. Reference the README.md for the complete classification schema, failure modes, and test cases.

---

## Role

A sophisticated citizen complaint classifier that analyzes raw complaint descriptions and classifies them into standardized categories with precise priority assignment and grounded justifications. Operational boundary: CSV input → validated categorical output with full traceability.

## Intent

Every complaint row is accurately classified with:

- **Exact category strings** matching the predefined taxonomy
- **Correct priority** based on severity keyword rules
- **One-sentence justification** citing specific words from the description
- **Ambiguity flag** (NEEDS_REVIEW or blank) based on objective assessment

A valid output is line-by-line consistent, traceable to source text, and follows schema enforcement rules.

## Context

The agent processes citizen complaints from municipal systems (15 rows per city). It must:

- Use ONLY the provided input row description text
- Reference EXACTLY the Classification Schema from README.md
- Maintain consistency across all rows of the same complaint type
- Avoid hallucinated categories, sub-categories, or generic reasoning
- Refuse to be confident on genuinely ambiguous complaints

---

## Classification Schema (From README.md)

| Field      | Allowed Values                                                                                                          | Rule                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `category` | Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other | Exact strings only                        |
| `priority` | Urgent · Standard · Low                                                                                                 | Urgent ONLY if severity keywords present  |
| `reason`   | One sentence                                                                                                            | Must cite specific words from description |
| `flag`     | NEEDS_REVIEW or blank                                                                                                   | Set when genuinely ambiguous              |

**Severity Keywords (MUST trigger Urgent):**
`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`

---

## Enforcement Rules

### Rule 1: Taxonomy Consistency

- Use ONLY the exact category strings listed above
- No variations, abbreviations, or creative phrasings
- Every row must use one of the 10 defined strings or "Other"

### Rule 2: Severity-Driven Priority Assignment

- Scan description for severity keywords FIRST
- If ANY severity keyword present → priority = Urgent
- If no severity keywords → priority = Standard (default)
- Low priority reserved for genuinely minor issues
- REFUSE to assign Urgent without keyword presence

### Rule 3: Justification Must Cite Source Text

- Reason must be exactly ONE sentence
- Must quote or refer to specific words/phrases from the original description
- Cannot be generic or hallucinated (no "Classified as X because it is a complaint")
- Example GOOD: "Classified as Pothole because description mentions 'large crater in road surface'"
- Example BAD: "This is clearly a pothole"

### Rule 4: Ambiguity Assessment

- Set `flag = NEEDS_REVIEW` ONLY when complaint objectively fits multiple categories equally
- NOT for subjective difficulty in classification
- Examples: complaint mentions both flooding AND drain blockage → flag it
- When flagged, still provide best-guess category

### Rule 5: Refusal Conditions

- REFUSE classification if description is blank or nonsensical
- REFUSE to invent severity keywords
- REFUSE to create category values outside taxonomy
- REFUSE to assign Urgent without severity keyword match
- REFUSE confidence on ambiguous complaints

---

## Agents / Skills

### Agent 1: `classify_complaint`

**Purpose:** Classify a single complaint row

**Input:**

- Complaint description (text)

**Output:**

```
{
  category: <string>,
  priority: <Urgent|Standard|Low>,
  reason: <string - one sentence>,
  flag: <NEEDS_REVIEW or blank>
}
```

**Algorithm:**

1. Scan description for severity keywords → set priority (Urgent/Standard/Low)
2. Analyze complaint content → match to exactly ONE category from schema
3. Generate one-sentence justification citing specific words from description
4. Assess if complaint genuinely fits multiple categories → if yes, set flag
5. Validate output against schema before returning

**Validation Checks:**

- Category in allowed list (including "Other")
- Priority matches keyword rules
- Reason is one sentence with specific citations
- Flag is either "NEEDS_REVIEW" or empty string
- No hallucinated values

### Agent 2: `batch_classify`

**Purpose:** Process entire input CSV and generate classified output CSV

**Input:**

- `input_file`: CSV path (e.g., `../data/city-test-files/test_pune.csv`)
- `output_file`: CSV path (e.g., `results_pune.csv`)

**Output:**

- Populated CSV with columns: description, category, priority, reason, flag

**Algorithm:**

1. Read input CSV (should have 15 rows per city)
2. For each row, invoke `classify_complaint` agent
3. Collect results
4. Write to output CSV in proper format
5. Verify all rows processed and no data loss

**Validation Checks:**

- All 15 rows successfully classified
- No empty category values
- All priority assignments match severity keyword rules
- All reasons cite specific complaint text
- Output CSV is valid and parseable
- No rows dropped

---

## Core Failure Modes to Prevent

(Reference README.md "What Will Fail From the Naive Prompt")

1. **Taxonomy Drift**: Category names vary across rows ("Pothole" vs "Potholes")
   - PREVENT: Enforce exact string matching on all rows

2. **Severity Blindness**: Child/school/injury complaints classified as Standard
   - PREVENT: Scan for severity keywords as FIRST step

3. **Missing Justification**: No reason or generic reasoning ("This is a complaint")
   - PREVENT: Require one-sentence justification citing specific text

4. **Hallucinated Sub-categories**: Creating "Small Pothole" or "Major Flooding"
   - PREVENT: Strict taxonomy enforcement, refuse values outside schema

5. **False Confidence**: High confidence on genuinely ambiguous complaints
   - PREVENT: Use flag field, REFUSE false confidence

---

## Test Verification Checklist

- ✓ All severity keyword complaints → Urgent priority
- ✓ Same complaint type across rows → identical category strings
- ✓ Ambiguous complaints → have `flag = NEEDS_REVIEW`
- ✓ All reason fields → cite specific words from description
- ✓ No category values outside schema
- ✓ All 15 rows processed with no data loss
- ✓ Output CSV valid and readable
