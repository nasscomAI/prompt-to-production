# skills.md — UC-0A: Complaint Classifier

## Skill 1: Text-Based Category Detection

**Name:** `detect_category`

**Description:**
Reads the raw complaint text and identifies which civic domain the issue belongs to.

**Input:** Plain text complaint string

**Logic:**
- Scan for domain keywords (see keyword map below)
- Match the most specific category first
- If multiple categories match, pick the primary one based on the main subject

**Keyword Map:**

| Category | Keywords |
|---|---|
| Roads | road, pothole, footpath, bridge, divider, pavement, speed breaker, accident, vehicle |
| Water | water, pipe, drainage, sewage, leakage, flood, supply, borewell, tank |
| Electricity | power, electricity, light, streetlight, transformer, outage, wire, shock, electrocution |
| Sanitation | garbage, waste, trash, dustbin, sweeper, drain, smell, dumping, cleanliness |
| Safety | fire, explosion, danger, threat, harassment, crime, theft, violence |
| Health | hospital, clinic, medicine, disease, epidemic, ambulance, dengue, malaria |
| Parks & Public Spaces | park, garden, playground, bench, tree, encroachment |

---

## Skill 2: Severity Classification

**Name:** `classify_severity`

**Description:**
Determines the urgency level of a complaint based on the nature of the issue and high-risk trigger words.

**Input:** Category + complaint text

**Severity Triggers (in priority order):**

1. **Critical** — Any of: `injury`, `injured`, `dead`, `death`, `fire`, `flood`, `hospital`, `child`, `school`, `emergency`, `electrocution`, `explosion`, `collapse`
2. **High** — Any of: `accident`, `contamination`, `no water`, `power cut`, `outage`, `dangerous`, `overflowing`, `blocked road`
3. **Medium** — Any of: `pothole`, `broken`, `irregular`, `dim light`, `delayed`, `overflow`
4. **Low** — Everything else (cosmetic, non-urgent, general feedback)

**Rule:** Always check Critical triggers first. Do not override Critical with a lower severity.

---

## Skill 3: Department Routing

**Name:** `route_department`

**Description:**
Maps the classified category to the responsible municipal department.

**Routing Table:**

| Category | Department |
|---|---|
| Roads | PWD (Public Works Department) |
| Water | Water Board |
| Electricity | BESCOM / Electricity Board |
| Sanitation | BBMP / Municipal Corporation |
| Safety | Fire & Emergency Services / Police |
| Health | Health Department |
| Parks & Public Spaces | BBMP / Municipal Corporation |

**Fallback:** If category is unclear, assign `Municipal Corporation (General)` and log for manual review.

---

## Skill 4: CSV I/O Handler

**Name:** `handle_csv`

**Description:**
Reads the input CSV, applies classify skills row by row, and writes the output CSV.

**Input file format:**
```
complaint_id, complaint_text
```

**Output file format:**
```
complaint_id, complaint_text, category, severity, department
```

**Rules:**
- Preserve all original columns
- Never skip a row — if classification fails, write `Unknown` and log the row index
- Output file must be named `results_[city].csv`

---

## Skill 5: Audit Logger

**Name:** `log_audit`

**Description:**
Appends a plain-text log entry for each classification decision, useful for CRAFT loop debugging.

**Format:**
```
[ROW 12] TEXT: "Water pipe burst near school" → CATEGORY: Water | SEVERITY: Critical | DEPT: Water Board
```

**Purpose:** Enables tutors and reviewers to trace every classification decision back to the input text.
