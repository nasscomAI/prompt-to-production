# skills.md — UC-0A: Complaint Classifier

## Skill Set for CivicClassifierAgent

---

## Skill 1: Text Classification

**Name:** `classify_complaint`
**Input:** Raw complaint text (string)
**Output:** category (string), severity (string), reason (string)

**How it works:**
- Scans the complaint text for domain keywords (road, water, electricity, garbage, etc.)
- Maps keywords to the fixed category taxonomy
- Applies the severity rubric, with hard-override rules for safety-critical keywords
- Returns a structured classification result

**Keyword-to-Category Mapping:**

| Keywords | Category |
|---|---|
| pothole, road, highway, pavement, footpath, crater, road damage, speed breaker | ROAD_DAMAGE |
| water, supply, tap, pipeline, no water, water cut, water shortage | WATER_SUPPLY |
| electricity, power cut, outage, transformer, meter, wire, electric, voltage | ELECTRICITY |
| garbage, waste, trash, rubbish, dump, litter, bins, collection | GARBAGE_COLLECTION |
| sewage, drain, drainage, overflow, blocked drain, manhole, sewer | SEWAGE_DRAINAGE |
| streetlight, street light, lamp post, dark, lighting, light not working | STREET_LIGHTING |
| mosquito, dengue, malaria, rat, pest, smell, stench, disease, health, hygiene | PUBLIC_HEALTH |
| noise, loud, music, sound, construction noise, horn, blaring | NOISE_POLLUTION |
| encroachment, illegal, hawker, footpath blocked, property | ENCROACHMENT |
| park, garden, playground, tree, bench, grass, recreation | PARKS_AND_RECREATION |
| dog, stray, animal, cattle, cow, horse, bite | STRAY_ANIMALS |

**Fallback:** If no keyword matches, assign `OTHER` with severity `LOW`.

---

## Skill 2: Severity Detection

**Name:** `detect_severity`
**Input:** Complaint text + initial category
**Output:** severity level (CRITICAL / HIGH / MEDIUM / LOW)

**Rules applied in order (first match wins):**

```
CRITICAL triggers (any one present → CRITICAL):
  - injury, accident, collapse, fire, flood inside home,
    exposed live wire, sewage overflow near hospital or school,
    building collapse, fallen tree blocking road

HIGH triggers (any one present → HIGH):
  - child, school, hospital, no water for N days (N≥3),
    road cave-in, dead animal on road, garbage pile >1 week,
    broken streetlight on highway, pothole on highway

MEDIUM triggers (default for most complaints):
  - pothole on side street, intermittent supply,
    flickering lights, noise at night, stray dog sighting

LOW triggers:
  - park maintenance, faded paint, cosmetic damage,
    noise during daytime, minor encroachment not blocking access
```

**Hard Override Rule:**
If complaint contains `injury | accident | child | school | hospital | fire |
flood | exposed wire | sewage overflow | pothole on highway | dead animal |
collapse | fallen tree blocking road` → severity is MINIMUM HIGH, never LOW or MEDIUM.

---

## Skill 3: CSV I/O

**Name:** `read_write_csv`
**Input:** Path to input CSV file
**Output:** Path to results CSV file

**Input CSV columns expected:**
```
complaint_id, complaint_text
```

**Output CSV columns produced:**
```
complaint_id, complaint_text, category, severity, reason
```

**Implementation notes:**
- Uses Python's built-in `csv` module — no pandas dependency
- Handles UTF-8 encoding with `errors='replace'`
- Wraps `reason` field in quotes to handle embedded commas
- Skips rows with missing `complaint_text` (logs a warning)
- Writes header row first, then data rows

---

## Skill 4: Batch Processing

**Name:** `batch_classify`
**Input:** List of complaint rows
**Output:** List of classified rows

**Behaviour:**
- Processes all complaints sequentially
- Never crashes on a single bad row — wraps each in try/except
- Logs row-level errors to stderr without stopping the batch
- Reports total processed / total errors at the end

---

## Skill 5: Self-Test (CRAFT Loop Support)

**Name:** `run_self_test`
**Input:** None (uses hardcoded test cases)
**Output:** Pass/Fail report printed to stdout

**Test cases included:**

| # | Complaint Text | Expected Category | Expected Severity |
|---|---|---|---|
| 1 | "Pothole on highway caused motorbike accident, rider injured" | ROAD_DAMAGE | CRITICAL |
| 2 | "No water supply for 4 days in our colony" | WATER_SUPPLY | HIGH |
| 3 | "Stray dogs near school gate, children afraid" | STRAY_ANIMALS | HIGH |
| 4 | "Park bench broken near entrance" | PARKS_AND_RECREATION | LOW |
| 5 | "Exposed electric wire hanging near footpath" | ELECTRICITY | CRITICAL |
| 6 | "Garbage not collected for 6 days, unbearable smell" | GARBAGE_COLLECTION | HIGH |
| 7 | "Loud music at night from nearby bar" | NOISE_POLLUTION | MEDIUM |
| 8 | "Sewage overflowing near government hospital" | SEWAGE_DRAINAGE | CRITICAL |

The self-test prints a pass/fail for each case and a final score.
