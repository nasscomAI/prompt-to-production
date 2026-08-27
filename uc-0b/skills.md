# UC-0B — Policy Summary Skills

## Skill 1: `retrieve_policy`
**Input**: Path to .txt policy file (policy_hr_leave.txt)
**Output**: Structured dict with numbered sections

**Algorithm**:
```
1. Read policy file
2. Parse into sections by numbering (e.g., 2.3, 2.4, ...)
3. Extract clause text for each section
4. Return dict: {"2.3": "text...", "2.4": "text...", ...}
5. Validate: Confirm all 10 critical clauses are present
```

**Critical clauses to extract**:
- 2.3 (14-day notice)
- 2.4 (written approval)
- 2.5 (LOP for unapproved absence)
- 2.6 (5-day carry-forward limit)
- 2.7 (Jan-Mar usage window)
- 3.2 (3+ days = medical cert)
- 3.4 (cert for holiday-adjacent leave)
- 5.2 (two-approver requirement for LWP)
- 5.3 (Commissioner approval for >30 days)
- 7.2 (no encashment during service)

---

## Skill 2: `summarize_policy`
**Input**: Structured sections from retrieve_policy
**Output**: String (summary text) with all clauses and section references

**Algorithm**:
```
1. For each of the 10 critical clauses:
   a. Extract the core obligation
   b. Identify binding verb (must, will, requires, etc.)
   c. Extract ALL conditions (especially AND conditions)
   d. Check for softening language (typically, may, generally)
   e. If conditions are complex:
      - Quote verbatim
      - Flag with [COMPLEX_CLAUSE]
   f. Else:
      - Summarize but preserve binding verb AND all conditions
      - Include section number (e.g., "Section 2.3")
2. Assemble summary in order of clauses
3. Validate no invented context
```

**Validation after assembly**:
- Count clauses present (must be 10)
- Scan for softening words (should, may, typically, generally)
- Check every AND clause for completeness
- Verify section numbers included

---

## Detection Rules for Multi-Condition Clauses

**Clause 5.2** (Two-approver trap):
- Source: "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
- BAD SUMMARY: "LWP requires approval from management"
- GOOD SUMMARY: "Section 5.2: LWP requires approval from both the Department Head and HR Director; manager approval alone is insufficient."

**Clause 2.6** (Forfeiture limit):
- Source: "Employees may carry forward a maximum of 5 unused annual leave days... Any days above 5 are forfeited on 31 December."
- MUST PRESERVE: Both the limit (5 days) AND the forfeiture date (31 Dec)

**Clause 3.4** (Holiday adjacency):
- Source: "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
- MUST PRESERVE: Three conditions: (1) before/after holiday, (2) or before/after leave, (3) cert required regardless of duration
