# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag values according to UC-0A schema.
    input:
      type: object
      properties:
        complaint:
          type: object
          properties:
            description:
              type: string
          required: [description]
      required: [complaint]
    output:
      type: object
      properties:
        category:
          type: string
        priority:
          type: string
        reason:
          type: string
        flag:
          type: string
      required: [category, priority, reason, flag]
    error_handling: "If description is missing or empty, set category: Other, priority: Low, reason: 'Description unavailable', flag: NEEDS_REVIEW."

  - name: batch_classify
    description: Read input CSV rows, apply classify_complaint for each row, and write output CSV with schema columns.
    input:
      type: object
      properties:
        input_path:
          type: string
        output_path:
          type: string
      required: [input_path, output_path]
    output:
      type: object
      properties:
        rows_processed:
          type: integer
        output_path:
          type: string
      required: [rows_processed, output_path]
    error_handling: "On file read/write failures, raise an error with a clear message. If a row cannot be processed, mark it as category Other, priority Low, reason 'Invalid row data', flag NEEDS_REVIEW, and continue."
