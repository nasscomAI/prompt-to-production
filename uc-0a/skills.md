skills:
- name: classify_complaint
  description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the enforcement schema.
  input:
    type: object
    format: "{description: string}"
  output:
    type: object
    format: "{category: string, priority: string, reason: string, flag: string}"
  error_handling: |
    If description is empty or missing: return category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW.
    If description contains no keywords matching any category: return category=Other, priority=Standard (or Urgent if severity keywords present), reason citing relevant words, flag=NEEDS_REVIEW.
    If multiple categories could apply: return category=Other, priority=Standard (or Urgent if severity keywords present), reason citing ambiguity, flag=NEEDS_REVIEW.
    Never hallucinate categories outside the allowed 10. Never omit reason field. Never assign priority other than Urgent/Standard/Low.

- name: batch_classify
  description: Reads input CSV, applies classify_complaint to each row, writes output CSV with classification columns.
  input:
    type: file
    format: "CSV with columns: [any columns including 'description']"
  output:
    type: file
    format: "CSV with original columns plus: category, priority, reason, flag"
  error_handling: |
    If input file not found or unreadable: raise FileNotFoundError with path.
    If description column missing: raise ValueError listing available columns.
    If any row fails classify_complaint: log error, write row with category=Other, priority=Low, reason="Classification error", flag=NEEDS_REVIEW, continue processing.
    Ensure output CSV has exactly the four classification columns appended in order.
    Validate all category values against allowed list before writing.
