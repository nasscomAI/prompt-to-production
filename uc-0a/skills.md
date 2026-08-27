skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag.
    input: A string representing a single citizen complaint description.
    output: A structured object containing category, priority, reason, and flag.
    error_handling: If the description is genuinely ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: File path to the input CSV file.
    output: Writes the classification results to a new output CSV file. Nomenclature has to be like results_pune.csv  Where the name of the city will be taken from the input file name.
    error_handling: Skip malformed rows or fail gracefully if the file is missing or unreadable.
