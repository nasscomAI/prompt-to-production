# skills.md — UC-0A Classification Skills

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row by matching description text against 
      exact category keywords, severity triggers, and ambiguity patterns.
    input: >
      dict with keys: complaint_id (str), description (str), location (str).
      Description is the only text field used for classification.
    output: >
      dict with keys: complaint_id (str), category (str), priority (str), 
      reason (str), flag (str). All must be populated.
      category: exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, 
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
      priority: Urgent | Standard | Low.
      reason: one sentence citing 2+ specific words from description.
      flag: "NEEDS_REVIEW" or blank string.
    logic:
      1. Scan description for SEVERITY KEYWORDS: injury, child, school, hospital, 
         ambulance, fire, hazard, fell, collapse (case-insensitive).
         If ANY found → priority = Urgent.
      2. Scan for CATEGORY KEYWORDS:
         - Pothole: "pothole", "crater", "pit", "rut", "sinkhole", "cavity"
         - Flooding: "flood", "water", "inundated", "submerged", "waterlogged"
         - Streetlight: "light", "streetlight", "lamp", "sparking", "flickering"
         - Waste: "garbage", "waste", "trash", "debris", "dump", "litter"
         - Noise: "noise", "sound", "music", "loud", "disturb"
         - Road Damage: "crack", "sinking", "surface", "damaged road", "asphalt"
         - Heritage Damage: "heritage", "historic", "monument", "old city", "ancient"
         - Heat Hazard: "heat", "temperature", "sun", "burning", "thermal"
         - Drain Blockage: "drain", "blockage", "clogged", "sewer", "underground"
         - Other: no clear match or ambiguous
      3. If multiple categories match, prefer higher-specificity match.
         If tie or ambiguity: set category = Other, flag = NEEDS_REVIEW.
      4. Generate reason: extract 2+ concrete words from description that 
         justify the category. Do not use generic reason like "complaint reported".
    error_handling: >
      - Empty or null description → category = Other, flag = NEEDS_REVIEW.
      - Description without clear keywords → category = Other, flag = NEEDS_REVIEW.
      - Multiple plausible categories with equal confidence → category = Other, flag = NEEDS_REVIEW.
      - Priority: if ANY severity keyword found, MUST be Urgent (non-negotiable).

  - name: batch_classify
    description: >
      Reads CSV input file, applies classify_complaint to each row, 
      writes results CSV with all output fields.
    input: >
      input_path (str): path to test_[city].csv with columns: complaint_id, 
      date_raised, city, ward, location, description, reported_by, days_open.
      output_path (str): path to write results_[city].csv.
    output: >
      Writes CSV file with columns: complaint_id, category, priority, reason, flag.
      15 rows output (or fewer if input smaller).
    logic:
      1. Read input CSV (skip header row).
      2. For each data row, extract complaint_id and description.
      3. Call classify_complaint() for that row.
      4. Collect result dict (with all 5 output keys).
      5. Write all rows to output CSV with header: complaint_id, category, priority, reason, flag.
    error_handling: >
      - Malformed CSV (bad quote, encoding) → log error, skip row, continue.
      - Missing complaint_id or description → log error, skip row, continue.
      - classify_complaint() raises exception → log error, skip row, continue.
      - Output file already exists → overwrite without warning.
      - File write failure → raise exception and stop.

enforcement_checklist:
  - "Every output row has a category from the 10 allowed values only."
  - "Every output row has priority Urgent if ANY severity keyword is in description."
  - "Every output row has a reason field with 2+ specific words from description."
  - "Ambiguous descriptions get category=Other and flag=NEEDS_REVIEW."
  - "No output row has blank category, priority, or reason fields."
