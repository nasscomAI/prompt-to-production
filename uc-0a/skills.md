# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into an allowed category plus severity-based priority, with a cited reason and ambiguity flag.
    input: One complaint row as a dict with at least complaint_id (str) and description (str), e.g. {"complaint_id": "PUNE-007", "description": "A child fell into an open pothole near the school gate"}.
    output: A dict {complaint_id: str, category: str, priority: str, reason: str, flag: str} where category is exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other; priority is Urgent, Standard, or Low (Urgent if any of injury, child, school, hospital, ambulance, fire, hazard, fell, collapse appears in the description); reason is one sentence citing specific words from the description; flag is NEEDS_REVIEW or blank.
    error_handling: If the description is missing, empty, or the category cannot be determined from it alone, return category "Other" and flag "NEEDS_REVIEW" instead of guessing; never invent sub-categories or drop fields.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Two file paths — input_path to ../data/city-test-files/test_[city].csv (15 rows, category and priority_flag columns stripped) and output_path for uc-0a/results_[city].csv.
    output: Writes results CSV where every row contains complaint_id, category, priority, reason, flag — one output row per input row, preserving input order.
    error_handling: Flags null/empty descriptions as NEEDS_REVIEW rows rather than crashing; if a single row fails classification it is written with category Other and flag NEEDS_REVIEW so the run still produces a complete output file.
