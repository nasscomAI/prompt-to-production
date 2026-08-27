# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag based on keyword matching against complaint description.
    input: |
      dict with keys:
        - complaint_id (str): unique identifier
        - description (str): citizen complaint narrative text
        - location (str): physical location of complaint
        - days_open (int): number of days complaint has been open
    output: |
      dict with keys:
        - complaint_id (str): echoed from input
        - category (str): one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
        - priority (str): one of [Urgent, Standard, Low]
        - reason (str): one-sentence explanation citing specific words from description
        - flag (str): "NEEDS_REVIEW" if category ambiguous or input malformed, otherwise empty string
    error_handling: |
      If description is null or empty: output category=Other, priority=Standard, reason="Description missing or empty", flag=NEEDS_REVIEW.
      If category cannot be determined: output category=Other, priority=Standard, flag=NEEDS_REVIEW.
      If severity keywords present: priority=Urgent. If keywords absent: priority=Standard (Low only if days_open > 60).
      Never crash on malformed input — always produce output row with flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV file, applies classify_complaint to each row, writes output CSV with classifications and flags.
    input: |
      - input_path (str): absolute or relative path to CSV file with columns [complaint_id, date_raised, city, ward, location, description, reported_by, days_open]
      - output_path (str): absolute or relative path where output CSV will be written
    output: |
      - Writes CSV file with columns [complaint_id, category, priority, reason, flag]
      - File contains one output row per input row (1:1 cardinality)
      - Even if individual rows fail classification, output is produced for all rows
    error_handling: |
      If input file not found: raise FileNotFoundError with path.
      If input row has missing columns: flag=NEEDS_REVIEW, attempt best-effort classification with available fields.
      If input row is malformed (e.g. description is numeric): catch exception, output category=Other, flag=NEEDS_REVIEW.
      If output path is not writable: raise exception and halt.
      Progress: Print row count to stdout after completing batch (e.g., "Classified 15 complaints").

  - name: keyword_matcher
    description: Matches complaint description text against predefined keyword sets to assign category and priority.
    input: |
      description (str): complaint narrative text (case-insensitive search)
    output: |
      - category_match (str): matched category keyword set (e.g., "Heat Hazard", "Pothole", or None)
      - severity_match (bool): True if description contains ANY severity keyword
      - matched_words (list): specific words from description that triggered the match
    error_handling: |
      If no keywords match: return category_match=None, severity_match=False, matched_words=[].
      If multiple categories match equally: return category_match=None (signals need for NEEDS_REVIEW flag).
      If description is empty or whitespace: return all empty results.
