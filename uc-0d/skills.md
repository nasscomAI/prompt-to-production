skills:
  - name: complaint_data_loader
    description: Load complaint records from a CSV file for processing.
    input: CSV file containing complaint_id and description fields.
    output: List of complaint records stored as dictionaries.
    error_handling: If the file cannot be found or opened, return an error message and stop processing.

  - name: complaint_classifier
    description: Classify complaint descriptions into predefined categories based on keywords.
    input: Complaint description text (string).
    output: Complaint category such as Pothole, Flooding, Garbage, Streetlight, Water Supply, or Other.
    error_handling: If no keywords match the description, assign the category "Other".

  - name: priority_detector
    description: Detect the urgency level of a complaint based on risk-related keywords.
    input: Complaint description text (string).
    output: Priority level "Urgent" or "Normal".
    error_handling: If no urgency keywords are detected, return priority "Normal".

  - name: complaint_summary_generator
    description: Generate summary statistics for complaints by category and priority.
    input: List of classified complaint records.
    output: Dictionary summaries showing counts for each category and priority.
    error_handling: If records are empty, return a message indicating no data available.

  - name: result_writer
    description: Write processed complaint classification results to an output CSV file.
    input: List of processed complaint records with category and priority fields.
    output: Output CSV file containing complaint_id, category, and priority.
    error_handling: If writing to the file fails, display an error message and stop execution.