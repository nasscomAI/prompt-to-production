# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: complaint_classification
    description: Classifies a complaint into a category using keywords.
    input: Complaint text as a string.
    output: Category like Water, Sanitation, Road, or Other.
    error_handling: Returns "Other" if input is empty or unclear.

  - name: severity_detection
    description: Identifies how serious a complaint is.
    input: Complaint text as a string.
    output: Severity level such as High, Medium, or Low.
    error_handling: Returns "Low" if no severity indicators found.

  - name: csv_reader
    description: Reads complaint data from a CSV file.
    input: CSV file path.
    output: List of complaint rows.
    error_handling: Shows error if file not found.

  - name: csv_writer
    description: Writes classified data into a CSV file.
    input: Processed complaint data.
    output: Output CSV file.
    error_handling: Shows error if writing fails.