skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into its appropriate category and priority based on severity keywords.
    input: A string representing one citizen complaint row/description.
    output: A structured response containing category, priority, reason, and flag.
    error_handling: If the text is ambiguous or cannot be classified confidently, returns category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV containing municipal complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: A string path to the input CSV file.
    output: A string path to the generated output CSV file.
    error_handling: Raises an error if the input CSV file is inaccessible. For invalid rows, assigns default values (category "Other", flag "NEEDS_REVIEW") and logs a warning.
