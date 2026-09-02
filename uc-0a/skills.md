# skills.md - UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    purpose: >
      Classify one citizen complaint deterministically into exactly one allowed
      category and one allowed priority, with an evidence-based reason and the
      required ambiguity flag.
    input: >
      One complaint represented as a dictionary. The input may contain
      complaint_id, date_raised, city, ward, location, description,
      reported_by, and days_open. The description is the primary evidence for
      category and priority.
    output:
      type: dictionary
      schema:
        complaint_id: "The input complaint_id copied exactly"
        category: "Exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
        priority: "Exactly one of: Urgent, Standard, Low"
        reason: "Exactly one sentence citing specific words or phrases from description"
        flag: "NEEDS_REVIEW or blank"
    expected_behavior:
      - "Return exactly the five output fields: complaint_id, category, priority, reason, and flag."
      - "Use only the exact allowed category strings; never emit synonyms, combinations, or subcategories."
      - "If description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse, return priority Urgent."
      - "Use only those documented severity triggers; do not add unsupported severity keywords or grammatical expansions."
      - "When no documented urgent trigger is present, return Standard as the deterministic non-urgent priority."
      - "If category ambiguity genuinely cannot be resolved, return category Other and flag NEEDS_REVIEW."
      - "For a clear classification, return a blank flag."
      - "Do not use days_open, reported_by, city, ward, or location to invent category or priority rules."
      - "Return the same result for the same input every time."
    constraints:
      - "The reason must be one sentence and its cited evidence must appear in the complaint description."
      - "The flag must be exactly NEEDS_REVIEW or blank."
      - "An empty or invalid complaint must not cause an exception; return Other, Standard, NEEDS_REVIEW, and a one-sentence reason explaining the missing or invalid description."

  - name: batch_classify
    purpose: >
      Read a CSV of citizen complaints, apply classify_complaint independently
      to each row, and write the classification results to an output CSV.
    input: >
      A CSV file containing complaint rows. Expected input columns are
      complaint_id, date_raised, city, ward, location, description,
      reported_by, and days_open.
    output:
      type: CSV file
      schema:
        columns: "complaint_id, category, priority, reason, flag"
        rows: "One classification result per input row whenever possible"
    expected_behavior:
      - "Read every input row and classify rows independently using classify_complaint."
      - "Write one output CSV containing exactly complaint_id, category, priority, reason, and flag."
      - "Preserve each input complaint_id exactly in its corresponding output row."
      - "Apply the same fixed categories, priorities, severity triggers, reason rule, and ambiguity rule as classify_complaint."
      - "Continue processing valid rows when another row is null or malformed."
      - "Produce an output file even when individual rows are invalid."
      - "Return the same output for the same input CSV."
    constraints:
      - "Categories must be exactly Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other."
      - "Priorities must be exactly Urgent, Standard, or Low."
      - "Urgent is mandatory when description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."
      - "Do not create combined categories or add unsupported severity rules."
      - "Each reason must be one sentence supported by specific words or phrases in that row's description."
      - "An ambiguous row must use Other and NEEDS_REVIEW; a clear row must use a blank flag."
      - "For an empty or invalid row, emit Other, Standard, NEEDS_REVIEW, and a one-sentence reason explaining the missing or invalid description."
