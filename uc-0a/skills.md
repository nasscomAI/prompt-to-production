# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag fields with strict taxonomy enforcement and severity keyword detection.
    input:
      type: object
      format: "Row object with description field (string) containing complaint text"
      required_field: description
    output:
      type: object
      format: "Classification result with category, priority, reason, and flag fields"
      schema:
        category: string (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
        priority: string (one of Urgent, Standard, Low)
        reason: string (single sentence citing specific words from description)
        flag: string (either "NEEDS_REVIEW" or empty)
    error_handling:
      - If description is empty or null, reject with error "Missing description field"
      - If assigned category is not in allowed list, reject with error "Hallucinated category detected"
      - If description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) but priority is not Urgent, reject with error "Severity blindness: must assign Urgent priority"
      - If reason field does not cite specific words from description, reject with error "Missing justification: reason must cite complaint text"
      - If classification is genuinely ambiguous (multiple equally valid categories possible), set flag to "NEEDS_REVIEW" instead of choosing confidently
      - If same complaint type was classified differently in previous rows, flag as "NEEDS_REVIEW" to prevent taxonomy drift

  - name: batch_classify
    description: Reads input CSV of complaints, applies classify_complaint to each row, and writes results to output CSV with consistent taxonomy across all rows.
    input:
      type: file
      format: "CSV file with description column and any number of supporting columns"
      required_columns:
        - description
    output:
      type: file
      format: "CSV file with all input columns plus category, priority, reason, flag columns"
    error_handling:
      - If input file not found, return error with file path
      - If description column is missing, return error "Required column missing: description"
      - If any row fails classify_complaint, log error with row number and reason, skip row, continue processing
      - Validate all rows after processing: ensure category values are consistent across identical complaint types (catch taxonomy drift), ensure all rows with severity keywords have Urgent priority, ensure all flagged rows are genuinely ambiguous
      - If validation fails, report violations and do not write output until corrections made
      - If output directory does not exist, create it before writing file
