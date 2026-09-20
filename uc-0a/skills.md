# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Deterministically map one complaint row to category, priority, reason, flag using only its description text.
    input: One complaint row as a dict with complaint_id (str) and description (str, may be null/empty); matching is case-insensitive substring on the lowercased description.
    output: Dict with complaint_id (echoed), category (exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (exactly one of Urgent, Standard, Low; Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse, else Low if category is Noise without a trigger, else Standard), reason (exactly one sentence of the form "Classified as <category> because description contains '<matched phrase>'"), flag (NEEDS_REVIEW if category is Other or flood-words and drain-words both match or text is vague, else blank).
    error_handling: Null/empty/whitespace description returns Other, Standard, missing-text reason, NEEDS_REVIEW and never raises; never returns a category outside the 10-item list; never reads other rows, external APIs, or files in data/.

  - name: batch_classify
    description: Read an input test CSV, apply classify_complaint to every row, and write the classified results CSV.
    input: CSV path to a test file (e.g. data/city-test-files/test_pune.csv with complaint_id and description columns) plus an output CSV path; invoked via the existing CLI as classifier.py --input <in> --output <out>.
    output: Classified CSV with exactly the header complaint_id,category,priority,reason,flag and exactly one output row per input row, each row satisfying the classify_complaint contract above.
    error_handling: Missing input file raises FileNotFoundError; any malformed row (bad/missing description, missing complaint_id) degrades per-row to Other/Standard/NEEDS_REVIEW with complaint_id falling back to ROW-n instead of aborting; output header is always written even for empty input; CLI flags --input and --output stay required.
