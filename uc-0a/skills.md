# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Accepts a single complaint row and returns standardized classification (category, priority, reason, flag).
    input: |
      Dictionary/row with keys: complaint_id, description, [other fields].
      Example: {"complaint_id": 1, "description": "Pothole on Main Street has injured two children"}
    output: |
      Dictionary with keys: complaint_id, category, priority, reason, flag.
      Example: {"complaint_id": 1, "category": "Pothole", "priority": "Urgent", 
                "reason": "Injury to children mentioned.", "flag": ""}
    error_handling: |
      - If description is empty/null: category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW
      - If category cannot be determined: category=Other, priority=Standard, reason="Classification ambiguous", flag=NEEDS_REVIEW
      - If description contains severity keywords: priority=Urgent (mandatory)
      - If reason cannot cite specific words from description: flag=NEEDS_REVIEW and output reason="Could not justify classification from description"

  - name: batch_classify
    description: Reads input file (CSV or Excel), applies classify_complaint to each row, writes results to output file in specified format.
    input: |
      - input_file: path to data file (.csv or .xlsx)
        Example: ../data/city-test-files/test_pune.csv OR test_pune.xlsx
        Columns: complaint_id, description, [other fields]
        Format: 15 rows per city
      - output_file: path to output file (.csv or .xlsx)
        Example: uc-0a/results_pune.csv OR results_pune.xlsx
      - output_format: optional flag to specify output format (csv or xlsx)
        If not specified, output format matches input format
    output: |
      - output_file: CSV or Excel file with classification results
        Columns: complaint_id, category, priority, reason, flag
        Format: same number of rows as input
        If xlsx: includes Excel formatting with headers, auto-width columns
    error_handling: |
      - If input_file does not exist: raise FileNotFoundError with message "Input file not found: [path]"
      - If input_file format not supported (.csv or .xlsx): raise ValueError "Unsupported file format. Use .csv or .xlsx"
      - If input_file is empty: process 0 rows, write empty output with header only
      - If any row fails classify_complaint: log error, output row with flag=NEEDS_REVIEW
      - If output_file cannot be written: raise IOError with message "Cannot write to output file: [path]"
      - Verify all output categories are in allowed list; if not, raise ValueError listing invalid categories
      - For xlsx output: validate Excel file integrity before returning

  - name: detect_severity_keywords
    description: Scans complaint description for severity keywords and returns list of detected keywords.
    input: |
      String: complaint description text (e.g., "A child fell into the drain and was injured")
    output: |
      List of keywords found (e.g., ["child", "fell", "injured"]) or empty list if none found.
      Each keyword match is case-insensitive.
    error_handling: |
      - If description is empty/null: return empty list []
      - If description is not a string: convert to string, then scan

  - name: validate_taxonomy
    description: Verifies that a category string matches exactly one allowed value in the taxonomy.
    input: |
      String: category value to validate (e.g., "Pothole", "pothole", "Potholes")
    output: |
      Boolean: True if category matches exactly, False otherwise.
      If True, also return the canonical (correct) category string.
    error_handling: |
      - If input is not a string: return False
      - If input is empty: return False
      - Case sensitivity: return False for "pothole" (lowercase is not allowed)

  - name: detect_file_format
    description: Detects input file format (CSV or Excel) by file extension and validates file integrity.
    input: |
      String: file path (e.g., ../data/city-test-files/test_pune.csv or test_pune.xlsx)
    output: |
      String: detected format ("csv" or "xlsx")
      Also returns metadata: row_count, column_names, file_size_bytes
    error_handling: |
      - If file does not exist: raise FileNotFoundError
      - If file extension not .csv or .xlsx: raise ValueError "Unsupported file format"
      - If Excel file is corrupted: raise IOError "Invalid Excel file format"
      - If CSV file cannot be parsed: raise ValueError "Invalid CSV format"

  - name: convert_file_format
    description: Converts output between CSV and Excel formats while preserving data integrity.
    input: |
      - data: list of dictionaries or DataFrame with classification results
      - output_format: string ("csv" or "xlsx")
      - output_path: file path where output should be written
    output: |
      None (writes file to disk)
      Returns path to written file and format confirmation
    error_handling: |
      - If output_format not "csv" or "xlsx": raise ValueError
      - If data is empty: write empty file with headers only
      - If output_path is invalid: raise IOError "Cannot write to path"
      - For xlsx: apply header formatting, auto-width columns, freeze first row
