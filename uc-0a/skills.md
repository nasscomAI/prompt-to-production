# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to assign an exact category, determine priority, generate a 1-sentence justifying reason, and set review flags.
    input: A string or dictionary containing the text `description` of the citizen complaint.
    output: A structured dictionary/JSON containing four string fields `category`, `priority`, `reason`, and `flag`.
    error_handling: If the text is genuinely ambiguous or does not fit any category clearly, the `category` falls back to "Other", and the `flag` is set to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of raw complaints, applies the classify_complaint skill to each row individually, and writes out the compiled classification results to a target CSV.
    input: Two file paths as strings — one for the input CSV and one for the output CSV.
    output: A completed output CSV file saved to the disk with the new classified columns appended.
    error_handling: If a row is malformed or crashes during classification, the process catches the exception, logs a standard fallback (category "Other", priority "Low", flag "NEEDS_REVIEW", and an error reason) and proceeds to the next row without breaking the execution.
