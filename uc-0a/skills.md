 skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint into a canonical category and priority,
      provides an evidence-based reason, and flags genuine ambiguity.

    input:
      type: object
      format: >
        A single complaint record containing a complaint description and,
        when available, a complaint_id.

    output:
      type: object
      format: >
        A classification record containing category, priority, reason, and flag.
        Category must use one of the allowed canonical values. Priority must be
        Urgent, Standard, or Low. Reason must be exactly one sentence citing
        specific words from the complaint description. Flag must be
        NEEDS_REVIEW for genuinely ambiguous complaints and blank otherwise.

    error_handling: >
      If the complaint description is missing or insufficient to determine a
      category, do not invent information. Use category Other and flag
      NEEDS_REVIEW when the complaint is genuinely ambiguous. Any complaint
      containing the exact severity keywords injury, child, school, hospital,
      ambulance, fire, hazard, fell, or collapse must receive Urgent priority.

  - name: batch_classify
    description: >
      Reads complaint records from an input CSV, applies classify_complaint
      to each row, and writes the classification results to an output CSV.

    input:
      type: CSV file
      format: >
        A CSV containing complaint records with complaint descriptions and,
        when available, complaint_id values. The category and priority_flag
        fields are stripped and must be classified by the application.

    output:
      type: CSV file
      format: >
        A CSV containing classification results for every input complaint,
        including category, priority, reason, and flag.

    error_handling: >
      Process each input row independently and do not silently skip invalid
      rows. If a complaint is genuinely ambiguous, classify it as Other and
      set flag to NEEDS_REVIEW. Do not invent categories or sub-categories.
      If an input row is missing a usable complaint description, preserve the
      record where possible and mark it for review rather than generating a
      confident unsupported classification.