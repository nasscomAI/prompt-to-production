# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint by category, priority, and provides justification
      with confidence flagging. Core atomic operation for complaint processing.
    
    input: >
      Type: string
      Format: Complaint description text (plain text, 1-500 words typical)
      Examples:
        Valid: "Large pothole on MG Road near school causing traffic issues"
        Valid: "Streetlight not working on Park Street corner"
        Invalid: "" (empty string - triggers error handling)
        Invalid: null (triggers error handling)
    
    output: >
      Type: dictionary (JSON-serializable)
      Schema: {
        "category": string (must be one of 10 allowed values),
        "priority": string (Urgent|Standard|Low),
        "reason": string (single sentence, 10-100 words),
        "flag": string (NEEDS_REVIEW|empty string)
      }
      Examples:
        {"category": "Pothole", "priority": "Urgent", "reason": "Contains severity keyword 'school'", "flag": ""}
        {"category": "Other", "priority": "Standard", "reason": "No description provided", "flag": "NEEDS_REVIEW"}
    
    preconditions:
      - Input must be string type (empty string allowed, triggers specific handling)
      - ALLOWED_CATEGORIES constant must be defined with 10 exact category strings
      - SEVERITY_KEYWORDS constant must be defined with keyword list
    
    postconditions:
      - Output dictionary contains all four mandatory keys
      - category value exists in ALLOWED_CATEGORIES
      - priority value is one of: Urgent, Standard, Low
      - reason is non-empty string
      - flag is either empty string or NEEDS_REVIEW
      - If severity keyword in input, priority must be Urgent
    
    validation:
      - Assert output has exactly 4 keys: category, priority, reason, flag
      - Assert category in ALLOWED_CATEGORIES (no variations)
      - Assert priority in ['Urgent', 'Standard', 'Low']
      - Assert len(reason) > 0 and len(reason) <= 500
      - Assert flag in ['', 'NEEDS_REVIEW']
      - If input contains severity keyword, assert priority == 'Urgent'
      - Assert reason cites words actually present in input description
    
    error_handling: >  
      Empty/null input → {category: "Other", priority: "Standard", reason: "No description provided", flag: "NEEDS_REVIEW"}
      Ambiguous category → Use best pattern match, set flag: "NEEDS_REVIEW", explain ambiguity in reason
      Multiple equal matches → Choose most severe category, set flag: "NEEDS_REVIEW"
      No pattern matches → {category: "Other", priority: "Standard", reason: "No clear category indicators", flag: "NEEDS_REVIEW"}
      Exception during processing → Log error, return Other category with NEEDS_REVIEW flag
    
    constraints:
      - Must complete in < 100ms per complaint (performance)
      - Must not access external APIs or databases (isolation)
      - Must not maintain state between calls (stateless)
      - Must not modify input string (immutable)
      - Pattern matching must be case-insensitive

  - name: batch_classify
    description: >
      Reads input CSV, applies classify_complaint to each row, writes results CSV.
      Fault-tolerant bulk processing with partial success support.
    
    input: >
      Type: tuple of two strings
      Format: (input_csv_path, output_csv_path)
      Input CSV schema: Must contain columns 'id' (or 'complaint_id') and 'description'
      Examples:
        Valid: ("../data/city-test-files/test_pune.csv", "results_pune.csv")
        Invalid: ("nonexistent.csv", "out.csv") → raises FileNotFoundError
    
    output: >
      Type: CSV file written to disk + integer count
      Output CSV schema: id, description, category, priority, reason, flag
      Return value: (processed_count: int, error_count: int)
      Side effects: Creates/overwrites output CSV file
      Console output: Prints summary with error details if any
    
    preconditions:
      - Input CSV file must exist and be readable
      - Input CSV must have 'description' column
      - Input CSV must have ID column ('id' or 'complaint_id')
      - Output directory must exist or be creatable
      - classify_complaint function must be available
    
    postconditions:
      - Output CSV file exists at specified path
      - Output CSV has all input rows (even if some failed)
      - Output CSV has 6 columns: id, description, category, priority, reason, flag
      - Processed count equals number of rows successfully classified
      - Error count equals number of rows that failed
      - Console shows summary: "Processed N complaints, M errors"
    
    validation:
      - Assert input file exists before processing
      - Assert input CSV has required columns
      - Assert output CSV has exactly 6 columns
      - Assert output row count equals input row count
      - Assert all category values in output are from ALLOWED_CATEGORIES
      - Assert no null values in output (empty string for flag is OK)
    
    error_handling: >
      File not found → Raise FileNotFoundError with full path
      Missing required columns → Raise ValueError with column list
      Malformed CSV → Raise Exception with row number and error details
      Row processing failure → Log to console, add to error list, continue processing
      Write failure → Raise Exception with output path
      Partial failure → Write all successful rows, print error summary showing failed row IDs
      Empty input file → Create empty output CSV with headers, print warning
    
    constraints:
      - Must process files up to 10,000 rows (scalability)
      - Must not load entire CSV into memory at once (streaming)
      - Must preserve input row order in output (ordering)
      - Must not modify input file (immutable)
      - Must use UTF-8 encoding for CSV files (encoding)
      - Must continue processing after individual row failures (fault tolerance)
    
    performance:
      - Target: Process 1000 rows per second on typical hardware
      - Memory: Maximum 100MB regardless of file size
      - Must show progress for files > 1000 rows
