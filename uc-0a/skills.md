skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based strictly on the given text and schema rules.
    input: A dictionary representing one complaint row, containing at minimum a text field such as "complaint" or "description".
    output: A dictionary with keys: category (string), priority (string), reason (string), flag (string).
    error_handling: If the text is missing, empty, or ambiguous, return category as "Other", set flag to "NEEDS_REVIEW", and provide a reason indicating insufficient or unclear information.

  - name: batch_classify
    description: Processes an input CSV file of complaint rows, applies classify_complaint to each row, and writes the structured results to an output CSV file.
    input: Input file path (string) to a CSV containing complaint rows; each row must include a complaint text field.
    output: Output file path (string) to a CSV containing classification results with columns: category, priority, reason, flag.
    error_handling: If a row fails processing, do not crash; instead, output a fallback row with category "Other", priority "Low", reason indicating processing error, and flag "NEEDS_REVIEW".