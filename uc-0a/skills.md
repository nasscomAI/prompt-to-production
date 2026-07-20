skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint into an approved municipal category and
      priority, with an evidence-based reason and an ambiguity review flag.
    input: >
      One CSV row as a dictionary containing at minimum complaint_id and
      description. Classification uses only the description; other row fields
      are preserved only for identification.
    output: >
      A dictionary with complaint_id, category, priority, reason, and flag.
      category is exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other.
      priority is Urgent, Standard, or Low; reason is one sentence citing words
      from the description; flag is NEEDS_REVIEW or blank.
    error_handling: >
      For a missing, blank, or genuinely ambiguous description, return category
      Other and flag NEEDS_REVIEW with a reason explaining the insufficient
      evidence. Never invent a category. If the description contains injury,
      child, school, hospital, ambulance, fire, hazard, fell, or collapse,
      priority must be Urgent regardless of category ambiguity.

  - name: batch_classify
    description: >
      Reads a complaint CSV, applies classify_complaint to every row, and writes
      a results CSV without abandoning the batch because of one invalid row.
    input: >
      input_path to a CSV with complaint rows and output_path for the results
      CSV. Input rows are expected to contain complaint_id and description.
    output: >
      A results CSV with exactly one record per input row and the columns
      complaint_id, category, priority, reason, and flag.
    error_handling: >
      Validate the required input columns and report an unreadable file or
      missing header clearly. Handle an individual malformed or null row by
      writing an Other, NEEDS_REVIEW result with an explanatory reason, then
      continue processing remaining rows. Do not write unapproved categories or
      omit a row silently.
