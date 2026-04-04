skills:
  - name: classify_complaint
    description: Classifies a citizen complaint description into a predefined category and priority, provides a 1-sentence reason citing the text, and flags ambiguity.
    input: String containing the citizen complaint description text.
    output: A dictionary object with 'category' (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), 'priority' (Urgent based on keywords, Standard, or Low), 'reason' (exactly one sentence citing the text), and 'flag' (NEEDS_REVIEW or empty).
    error_handling: If the category is genuinely ambiguous or cannot be confidently determined from the description alone, output category 'Other' and set flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, sequentially applies the classify_complaint skill per row enforcing strict categories/priorities, and writes out the results to an output CSV.
    input: A string filepath pointing to the input CSV file.
    output: A string filepath pointing to the generated output CSV file with appended classification columns.
    error_handling: Log file reading/writing errors; wrap row-level execution in a try-catch to apply a default 'Other' category and 'NEEDS_REVIEW' flag on failure without stopping batch execution.
