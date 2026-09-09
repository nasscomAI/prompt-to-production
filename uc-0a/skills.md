skills:
  - name: "classify_complaint"
    description: "Takes a single complaint description, maps it to a strict category taxonomy, assigns a priority based on severity keywords, and generates a one-sentence reason."
    input:
      description: "string (the raw citizen complaint text)"
    output:
      category: "string (exact match from the allowed category list)"
      priority: "string (Urgent, Standard, or Low)"
      reason: "string (one sentence citing specific words from the text)"
      flag: "string (NEEDS_REVIEW or blank)"
    error_handling: "If text is empty or unparsable, default to category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', with a reason stating text was missing."

  - name: "batch_classify"
    description: "Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV with the required columns appended."
    input:
      input_file: "string (path to the stripped test CSV dataset)"
      output_file: "string (path to the target output CSV file)"
    output:
      file_creation: "Writes categorized rows to disk"
    error_handling: "Raise FileNotFoundError if input CSV is missing. Retain all original non-target columns from the input."