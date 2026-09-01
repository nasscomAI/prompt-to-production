# skills.md — UC-0A Complaint Classifier
# RICE derived → manually refined per CRAFT loop

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category + priority + reason + flag using keyword matching and severity rules.
    input: Complaint row dict with keys complaint_id (string) and description (string).
    output: Dict with keys complaint_id (string), category (one of allowed taxonomy), priority (Urgent|Standard|Low), reason (string citing words from description), flag (NEEDS_REVIEW|BAD_ROW|blank).
    error_handling: If description empty → category Other + flag NEEDS_REVIEW + reason "Empty description". If no keyword matches → Other + NEEDS_REVIEW. If exception → Other + BAD_ROW.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV with exact header complaint_id,category,priority,reason,flag.
    input: Path to test_[city].csv (CSV with complaint_id,description columns); output path string.
    output: Writes results_[city].csv; returns row count written.
    error_handling: Validates header exists; replaces None with ""; enforces allowed taxonomy (corrects to Other + NEEDS_REVIEW if outside); per-row try/except logs BAD_ROW but continues; never crashes on bad rows.

  - name: taxonomy_enforcement
    description: Ensures category is exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
    input: Candidate category string.
    output: Validated category string.
    error_handling: If not in allowed list → override to Other + NEEDS_REVIEW and append correction to reason.

  - name: severity_detection
    description: Detects severity keywords to set priority Urgent.
    input: Lowercased description string.
    output: Priority Urgent if any of injury, child, school, hospital, ambulance, fire, hazard, fell, collapse present; else Standard.
    error_handling: Defaults to Standard if no keyword; never infers urgency without exact keyword match.
