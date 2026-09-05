skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag using the enforcement rules defined in agents.md.
    input:
      type: dict
      fields:
        - description: string — the complaint text submitted by the citizen
        - location: string — the location field from the input row
    output:
      type: dict
      fields:
        - category: string — exactly one value from the allowed enum
        - priority: string — Urgent | Standard | Low
        - reason: string — one sentence citing specific words from the description
        - flag: string — NEEDS_REVIEW or empty string
    error_handling:
      - "if description is empty or None: return {category: Other, priority: Low, reason: 'No description provided', flag: NEEDS_REVIEW} — do not call the LLM"
      - "if description is present but fewer than 5 characters: return {category: Other, priority: Low, reason: 'Description too short to classify', flag: NEEDS_REVIEW} — do not call the LLM"
      - "if the LLM returns a category not in the allowed enum: reject the response, retry once with an explicit correction prompt, and if still invalid return category: Other, flag: NEEDS_REVIEW"
      - "if the LLM returns an empty or missing reason field: reject the response and retry once — if still missing, set reason: 'Description insufficient to determine category' and flag: NEEDS_REVIEW"
      - "if the LLM call raises an exception (timeout, API error, rate limit): return {category: Other, priority: Low, reason: 'Classification unavailable', flag: NEEDS_REVIEW} — do not propagate the exception to the caller"
      - "if a severity keyword is present in the description but the LLM returns priority other than Urgent: override the LLM output and set priority: Urgent before returning — never trust the LLM over the keyword rule"

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the results to an output CSV with category, priority, reason, and flag columns added.
    input:
      type: file
      format: CSV
      required_columns:
        - description
        - location
      notes: category and priority_flag columns are stripped from input — do not expect them
    output:
      type: file
      format: CSV
      columns_added:
        - category
        - priority
        - reason
        - flag
      notes: all original columns preserved, four new columns appended per row
    error_handling:
      - "if input file path does not exist: raise FileNotFoundError with the full attempted path — do not proceed"
      - "if input file exists but cannot be parsed as CSV: raise ValueError stating the file is not valid CSV — do not proceed"
      - "if required column 'description' is absent from the CSV header: raise ValueError naming the missing column — do not proceed"
      - "if column 'location' is absent: proceed with location set to empty string per row — do not raise, do not skip rows"
      - "if output file path directory does not exist or is not writable: raise IOError before processing any rows — do not silently discard results"
      - "if classify_complaint raises or returns an invalid result for a row: write {category: Other, priority: Low, reason: 'Classification error on this row', flag: NEEDS_REVIEW} for that row and continue — never abort the entire batch for a single row failure"
      - "if all rows fail classification: still write the output CSV with NEEDS_REVIEW rows — do not raise an exception"
