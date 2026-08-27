skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description to determine its exact category, priority, explicit reason, and review flag.
    input:
      type: string
      format: A single text description representing one citizen complaint.
    output:
      type: dict
      format: Contains strictly mapped 'category', 'priority', 'reason' (one sentence), and 'flag' ('NEEDS_REVIEW' or blank).
    error_handling: It explicitly prevents severity blindness by assigning an 'Urgent' priority if severity keywords are present. It prevents false confidence on ambiguous cases by setting 'flag' to 'NEEDS_REVIEW'. It avoids hallucinated sub-categories by restricting 'category' strictly to the allowed exact strings list.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint sequentially per row, and writes a classified output CSV.
    input:
      type: string
      format: A file path pointing to the input CSV containing citizen complaints.
    output:
      type: string
      format: A file path pointing to the destination CSV with classification columns appended.
    error_handling: It prevents taxonomy drift by enforcing strictly consistent allowed categories across identical complaint types throughout the batch. It handles missing justifications by rejecting any row failing to provide a one-sentence reason citing specific input words, confirming the entire batch perfectly complies with the classification schema without crashing.
