# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single raw citizen complaint mapping it to a strict category taxonomy and priority level based on severity keywords.
    input: A single citizen complaint row containing the raw text description.
    output: A structured object mapping containing exactly `category`, `priority`, `reason`, and an optional `flag` field.
    error_handling: Handles genuine textual ambiguity by optionally setting the `category` to "Other" and explicitly setting the `flag` to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV containing unresolved complaints, applies the classify_complaint skill on every single row, and writes the results to a new output CSV.
    input: String representing the file path to the input CSV document.
    output: A generated output CSV file written to a defined output file path containing the filled columns.
    error_handling: Notifies on missing input files or I/O errors and proceeds with valid rows if independent row processing fails.
