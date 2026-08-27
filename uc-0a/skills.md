skills:
  - name: classify_complaint
    description: >
      Takes a citizen's complaint consisting of an unstructured description alongside 
      specific operational metadata (days_open, location, reported_by), and classifies it into a 
      standardized taxonomy with an exact category, a dynamically calculated priority, a citing reason, 
      and an ambiguity flag based on robust regex matching and predefined business rules.
    input:
      type: dictionary
      format: >
        {
          "description": "text",
          "days_open": int,
          "reported_by": "text",
          "location": "text",
          "location_count": int
        }
    output:
      type: dictionary
      format: >
        {
          "category": "exact string",
          "priority": "Urgent | Standard | Low",
          "reason": "one sentence citing specific details",
          "flag": "NEEDS_REVIEW | empty string"
        }
    error_handling: >
      If the input lacks sufficient text or matches no category, it assigns 'Other' and triggers the 
      'NEEDS_REVIEW' flag. If the metadata elements (days_open, location count) trigger an overriding 
      severity priority, it ensures 'Urgent' takes strict precedence over normal descriptions to prevent severity blindness.

  - name: batch_classify
    description: >
      Reads a batch of complaints from a CSV file, computes frequency metadata directly from the dataset 
      (like location repetition), applies the 'classify_complaint' skill row-by-row, and writes the complete 
      structured results back to a new destination CSV file.
    input:
      type: file path
      format: Path pointing to an input CSV file containing descriptive textual columns as well as metadata (days_open, location, reported_by)
    output:
      type: file path
      format: Path pointing to the generated output CSV file holding identical rows but populated with 'category', 'priority', 'reason', and 'flag' columns.
    error_handling: >
      Invalid metadata (e.g. non-integer days open) will be safely defaulted rather than throwing exceptions. 
      Row processing errors log a warning instead of halting the batch pipeline.
