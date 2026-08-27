# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint row to determine category, priority, reason, and flag using strict keyword matching logic across Infrastructure, Environmental, Nuisance, and General dictionaries.
    input: A single complaint row containing a description (dictionary containing strings).
    output: A structured record containing the assigned category (string), priority (string), reason (string), and flag (string).
    error_handling: IF the description does not match any specific category keywords, THEN assigns category 'Other' and flag 'NEEDS_REVIEW' and notes default resolution in the reason field.

  - name: batch_classify
    description: Reads an input CSV containing complaints, loops classify_complaint logic over each row iteratively, and writes the evaluated classifications iteratively to an output CSV formatted with the required explicit headers.
    input: Filepath to an input CSV file containing multiple complaint rows (string).
    output: Outputs a file path string and writes output rows dynamically to it in CSV format (string / file I/O).
    error_handling: Wraps in try-except block to gracefully skip malformed rows, log read/write failure error messages to standard output, without crashing the overall CSV process loop.
