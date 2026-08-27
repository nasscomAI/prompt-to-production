# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint using the fixed UC-0A taxonomy and
      returns its category, priority, evidence-based reason, and review flag.
    input:
      type: object
      required_fields:
        complaint_id: >
          The complaint identifier, preserved exactly in the result.
        description: >
          The citizen complaint text. This is the only source allowed for
          classification and severity decisions.
    output:
      type: object
      fields:
        complaint_id: >
          The unchanged identifier from the input.
        category: >
          Exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
          Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
        priority: >
          Exactly one of: Urgent, Standard, Low.
        reason: >
          Exactly one sentence explaining the category and priority while
          citing specific words or phrases from the input description.
        flag: >
          NEEDS_REVIEW when the category is genuinely ambiguous; otherwise
          blank.
    procedure:
      - Read only the complaint description; do not use external knowledge,
        geographic inference, temporal analysis, or sentiment scoring.
      - Determine whether the description clearly maps to one allowed
        category.
      - If no category can be determined, assign Other and NEEDS_REVIEW.
      - Check the description for the mandatory urgent keywords injury, child,
        school, hospital, ambulance, fire, hazard, fell, and collapse.
      - If any mandatory keyword is present, assign Urgent.
      - Otherwise assign Standard or Low using only the severity explicitly
        described in the complaint.
      - Write a one-sentence reason grounded in quoted or clearly cited words
        from the description.
    enforcement:
      - Never invent, rename, qualify, or create a category or sub-category.
      - Never omit the reason.
      - Never return a flag other than NEEDS_REVIEW or blank.
      - Never present an ambiguous category as certain.
      - Preserve complaint_id exactly.
    error_handling:
      - If the description is empty, missing, or insufficient to determine a
        category, return category Other, flag NEEDS_REVIEW, and a one-sentence
        reason stating that the description lacks specific classification
        terms.
      - If complaint_id is missing, report the row as invalid to the batch
        skill without inventing an identifier.

  - name: batch_classify
    description: >
      Reads a city complaint CSV, applies classify_complaint to all 15 rows,
      validates every result, and writes the complete classified output CSV.
    input:
      type: csv_file
      path_pattern: ../data/city-test-files/test_[your-city].csv
      requirements:
        - The file must contain exactly 15 complaint rows.
        - Every row must contain complaint_id and description.
    output:
      type: csv_file
      path_pattern: results_[your-city].csv
      columns:
        - complaint_id
        - category
        - priority
        - reason
        - flag
    procedure:
      - Read the input CSV without changing its complaint identifiers.
      - Apply classify_complaint exactly once to every row.
      - Retain low-confidence and ambiguous rows rather than skipping them.
      - >
        Write the output columns in this order: complaint_id, category,
        priority, reason, flag.
      - Validate the completed file before reporting success.
    validation:
      - The output contains exactly one row for each of the 15 input rows.
      - Every input complaint_id occurs exactly once in the output.
      - Every category exactly matches the allowed taxonomy.
      - Every priority is Urgent, Standard, or Low.
      - Every description containing a mandatory urgent keyword is Urgent.
      - Every reason is one sentence and cites text from its description.
      - Every flag is either NEEDS_REVIEW or blank.
      - Every genuinely ambiguous complaint is Other with NEEDS_REVIEW.
    error_handling:
      - Do not silently skip malformed or unclear complaint rows.
      - If a row has an unclear description, classify it as Other with
        NEEDS_REVIEW and include a grounded reason.
      - If the CSV cannot be read, required columns are missing, an identifier
        is missing, or the row count is not 15, stop before writing a partial
        output and report the validation error.
