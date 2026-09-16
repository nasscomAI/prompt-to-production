skills:
  - name: classify_complaint
    description: >
      Classify one citizen complaint row into an allowed category and priority, provide a one-sentence evidence-based reason, and set a review flag when the category is genuinely ambiguous.
    input: >
      One complaint row containing a complaint description. The category and priority_flag values are not provided.
    output: >
      One result containing category, priority, reason, and flag. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Priority must be exactly one of: Urgent, Standard, Low. Flag must be NEEDS_REVIEW or blank.
    error_handling: >
      Use category Other and flag NEEDS_REVIEW when the category cannot be determined confidently from the description alone. Set priority to Urgent whenever the description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse. The reason must be one sentence citing specific words from the description.

  - name: batch_classify
    description: >
      Read an input complaint CSV, apply classify_complaint independently to every row, and write the classified results to an output CSV.
    input: >
      An input CSV path such as ../data/city-test-files/test_[your-city].csv. The file contains complaint rows per city, with category and priority_flag columns stripped.
    output: >
      An output CSV path such as results_[your-city].csv containing one result per input row with category, priority, reason, and flag fields.
    error_handling: >
      Preserve one output row for each input row. For genuinely ambiguous complaints, output category Other and flag NEEDS_REVIEW. Do not invent categories or sub-categories, and ensure every reason is one sentence citing specific words from that row's description.
