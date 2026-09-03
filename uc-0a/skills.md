# skills.md — UC-0A Complaint Classifier
# Workshop: RICE prompt → generated draft → manual CRAFT refinement | Verified on Pune, Hyderabad, Kolkata, Ahmedabad

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason and flag using precedence-ordered keyword matching and severity detection, with disambiguation for heritage/waste/noise and heat/road collisions.
    input: Dict with `complaint_id: str` and `description: str` (raw CSV row). Lowercases description for matching.
    output: Dict `complaint_id: str`, `category: str` (allowed taxonomy), `priority: "Urgent"|"Standard"`, `reason: str` (cites matched keyword + quotes description[:120] + severity if present), `flag: "NEEDS_REVIEW"|"BAD_ROW"|""`.
    error_handling: Empty/whitespace description → `Other` + `NEEDS_REVIEW` + `reason="Empty description"`. No keyword match → `Other` + `NEEDS_REVIEW` + `reason="No category keyword matched..."`. Exception → `Other` + `BAD_ROW` + `reason="Error: ..."`.

  - name: batch_classify
    description: Batch orchestrator — reads `test_[city].csv`, validates header, applies `classify_complaint` per row, writes `results_[city].csv` with exact header `complaint_id,category,priority,reason,flag`.
    input: `input_path: str` (CSV with `complaint_id, description`), `output_path: str`.
    output: CSV file with one row per input (16 lines with header for 15 rows); returns count written; prints `Done. Results written to ...`.
    error_handling: Missing header → `ValueError`. `None` values normalized to `""`. Per-row `try/except` → `BAD_ROW` but never crashes. Enforces allowed taxonomy — corrects outside values to `Other` + `NEEDS_REVIEW` + `| corrected to allowed taxonomy`.

  - name: taxonomy_enforcement
    description: Validates category against fixed workshop taxonomy.
    input: Candidate category string from keyword matcher.
    output: Validated category ∈ `Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other`.
    error_handling: If not in list (e.g., hallucinated `Water Damage`) → override to `Other`, set `flag=NEEDS_REVIEW`, append correction to `reason`. Case-sensitive exact match.

  - name: severity_detection
    description: Rule-based priority assignment per enforcement; no ML inference.
    input: Lowercased `description: str`.
    output: `Urgent` if any of `injury, child, school, hospital, ambulance, fire, hazard, fell, collapse` is substring; else `Standard`.
    error_handling: No keyword → `Standard`. Never infers `Urgent` without exact keyword hit. Multi-hit reports `severity keyword(s) 'a, b' → Urgent` in reason.

  - name: disambiguation
    description: Resolves overlapping keywords (heritage zone garbage → Waste, Tagore band → Noise, road surface + temperature → Heat Hazard, overflow + garbage → Waste, drain blocked + flood → Drain Blockage).
    input: Lowercased description and candidate matches with precedence order `Strong Heritage > Drain Blockage > Flooding > Pothole > Heat Hazard > Road Damage > Waste > Streetlight > Noise`.
    output: Single category with matched phrase; fallback `Other`.
    error_handling: If ambiguous and no clear winner → `Other` + `NEEDS_REVIEW`; never combines two categories.

notes: >
  CRAFT loop: naive prompt → taxonomy drift + severity blindness + empty reason + `Water Damage` → fixed via precedence + disambiguation + `full sun`/`44°c` word-phrase + heritage strong vs generic. Verified `taxonomy PASS` on 4 cities (60 rows, 10 Urgent total).
