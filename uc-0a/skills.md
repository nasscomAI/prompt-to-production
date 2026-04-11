# skills.md

skills:
  - name: classify_complaint
    description: Performs automated triage of a single complaint into the fixed municipal taxonomy (Pothole, Flooding, etc.) and determines priority using Safety Keywords.
    input: A single text-based complaint description.
    output: An object containing category, priority (Urgent/Standard/Low), a one-sentence reason citing source keywords, and a NEEDS_REVIEW flag.
    error_handling: For ambiguous or unclassifiable text, outputs category 'Other' and sets flag 'NEEDS_REVIEW' to maintain the operational boundary.

  - name: batch_classify
    description: Executes a bulk triage operation by applying the classify_complaint skill to every row in an input CSV, generating a verified classification dataset.
    input: Path to a CSV file (e.g., test_[city].csv) containing complaint descriptions.
    output: Path to the results CSV file containing the classification taxonomy and justifications.
    error_handling: Ensures the entire batch is processed; rows causing logic failures are assigned category 'Other' with a NEEDS_REVIEW flag.
