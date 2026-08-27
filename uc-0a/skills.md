skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row using the fixed UC-0A taxonomy and severity rules.
    input: A single complaint record with a non-empty description field.
    output: A record with category, priority, reason, and flag fields; category is one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other; priority is Urgent, Standard, or Low; reason is one sentence citing description text; flag is NEEDS_REVIEW or blank.
    error_handling: If the description is missing or blank, return category Other, priority Standard, a one-sentence reason stating that the description is missing, and flag NEEDS_REVIEW. If category evidence is genuinely ambiguous, return category Other and flag NEEDS_REVIEW; severity keywords still require Urgent priority.

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to every row, and writes the classified CSV.
    input: An input CSV path containing complaint rows and an output CSV path.
    output: A CSV at the output path with every input row preserved and category, priority, reason, and flag populated for each row.
    error_handling: Reject an unreadable CSV or one without a description column with a clear error and do not write a partial output. For valid rows with missing or ambiguous descriptions, preserve the row and use classify_complaint error handling rather than aborting the batch.
