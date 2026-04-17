skills:
  - name: classify_complaint
    description: >
      Deterministically classifies one complaint row into UC-0A schema fields
      (category, priority, reason, flag) using only evidence present in that
      row text.
    purpose: >
      Prevent taxonomy drift, urgency misses, and fabricated reasoning by
      enforcing a fixed label set, a mandatory urgency keyword override, and
      evidence-grounded justification.
    input:
      type: dict
      required_keys:
        - complaint_id
        - description
      optional_keys:
        - location
        - timestamp
      constraints:
        - complaint_id must be non-empty and serializable as string.
        - description must be non-empty after trim.
        - Only description text may be used for semantic classification.
      normalization:
        - Trim leading/trailing whitespace.
        - Collapse repeated internal whitespace for matching.
        - Perform case-insensitive keyword checks.
    output:
      type: dict
      keys:
        - complaint_id
        - category
        - priority
        - reason
        - flag
      schema_rules:
        category_allowed:
          - Pothole
          - Flooding
          - Streetlight
          - Waste
          - Noise
          - Road Damage
          - Heritage Damage
          - Heat Hazard
          - Drain Blockage
          - Other
        priority_allowed:
          - Urgent
          - Standard
          - Low
        flag_allowed:
          - NEEDS_REVIEW
          - ""
        reason_requirements:
          - Must be exactly one sentence.
          - Must cite specific words or phrases from description.
          - Must explain both category and priority choice.
    decision_policy:
      decision_order:
        - Extract explicit evidence phrases from description.
        - Choose category only from category_allowed.
        - Apply urgency override if any severity keyword is present.
        - If no urgency keyword, choose Standard or Low from explicit severity cues only.
        - Generate one-sentence evidence-grounded reason.
        - Apply ambiguity rule for flag.
      urgency_keywords:
        - injury
        - child
        - school
        - hospital
        - ambulance
        - fire
        - hazard
        - fell
        - collapse
      ambiguity_rule: >
        If multiple categories are similarly supported or evidence is too vague
        for reliable category mapping, set category to Other and flag to
        NEEDS_REVIEW. If one category is clearly best-supported by explicit
        text, do not use NEEDS_REVIEW.
      hallucination_guards:
        - Never invent categories, synonyms, or sub-categories.
        - Never use external world knowledge or assumptions about local context.
        - Never output confidence scores, probabilities, or extra fields.
        - Never leave reason blank.
    error_handling:
      invalid_input:
        - If description is missing/blank, return:
          category: Other
          priority: Standard
          reason: "Description is missing or blank, so category cannot be determined from row text."
          flag: NEEDS_REVIEW
      malformed_row:
        - Preserve complaint_id if present; otherwise set complaint_id to "UNKNOWN".
        - Do not raise fatal exceptions from this skill.
      ambiguous_case:
        - Prefer safe fallback (Other + NEEDS_REVIEW) over speculative precision.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint row by row,
      and writes a schema-valid output CSV without aborting on bad rows.
    purpose: >
      Provide resilient batch execution that always produces output artifacts,
      isolates row-level failures, and preserves traceability for review.
    input:
      type: object
      required_fields:
        - input_path
        - output_path
      constraints:
        - input_path must point to a readable CSV file.
        - output_path parent directory must be writable.
        - CSV must contain complaint_id and description columns.
    output:
      type: csv_file
      path: output_path
      required_columns:
        - complaint_id
        - category
        - priority
        - reason
        - flag
      output_guarantees:
        - One output row per input row when parsing succeeds.
        - Deterministic column order as listed in required_columns.
        - No category/priority/reason nulls in written rows.
    processing_contract:
      row_processing:
        - Process rows independently in input order.
        - Invoke classify_complaint for each row.
        - Validate each returned field against schema_rules before writing.
      validation_and_repair:
        - If category is invalid, coerce to Other and set flag to NEEDS_REVIEW.
        - If priority is invalid, coerce to Standard.
        - If reason is missing/blank, replace with deterministic fallback reason and set flag to NEEDS_REVIEW.
        - If urgency keyword exists but priority is not Urgent, force priority to Urgent.
      failure_isolation:
        - Catch per-row exceptions and continue batch.
        - For failed rows, write safe fallback output with NEEDS_REVIEW and an error reason.
        - Never terminate whole batch because of a single bad row.
    observability:
      logging:
        - Track total rows read, rows successfully classified, rows repaired, rows failed.
        - Track complaint_id for rows repaired/failed when available.
      completion:
        - Return or print a concise summary of batch outcomes.
    error_handling:
      input_file_errors:
        - If input file missing/unreadable, raise a clear error and do not create misleading partial output.
      output_file_errors:
        - If output path unwritable, raise a clear error with target path context.
      schema_errors:
        - Attempt deterministic repair first, then fallback row output with NEEDS_REVIEW.

  - name: batch_classify_with_quality_gate
    description: >
      Runs batch classification with an additional quality-control gate that
      validates every row decision against schema and policy checks before
      final output is accepted.
    purpose: >
      Provide a stricter batch path for production handoff where policy
      violations are surfaced explicitly and uncertain rows are isolated for
      human review instead of silently passing through.
    input:
      type: object
      required_fields:
        - input_path
        - output_path
      optional_fields:
        - review_output_path
      constraints:
        - input_path must point to a readable CSV file.
        - output_path must be writable.
        - review_output_path, if provided, must be writable.
        - Input CSV must contain complaint_id and description columns.
    output:
      type: object
      artifacts:
        - output_csv
        - review_csv_optional
        - qc_summary
      output_csv_contract:
        - Columns must be exactly: complaint_id, category, priority, reason, flag.
        - Rows must be schema-valid and policy-valid after quality gate repair.
      review_csv_contract:
        - Contains only rows flagged NEEDS_REVIEW or rows requiring repair.
        - Includes complaint_id and a concise review_reason.
      qc_summary_fields:
        - total_rows
        - valid_rows
        - repaired_rows
        - review_rows
        - failed_rows
    processing_contract:
      stage_1_classification:
        - Classify each row using classify_complaint.
      stage_2_quality_gate:
        - Reject non-allowed category labels and coerce to Other.
        - Reject non-allowed priority labels and coerce to Standard.
        - Enforce Urgent when severity keywords are present in description.
        - Enforce one-sentence non-empty reason citing description evidence.
        - Enforce flag semantics: NEEDS_REVIEW only for ambiguity/repair cases.
      stage_3_review_routing:
        - Route repaired rows and ambiguous rows to review output.
        - Keep valid non-ambiguous rows in primary output only.
      stage_4_reporting:
        - Emit deterministic summary counts for operational monitoring.
    hallucination_controls:
      - Never permit out-of-schema labels in final outputs.
      - Never preserve speculative or unsupported reasons after quality gate.
      - Never suppress review flags on rows that required repair.
    error_handling:
      row_level:
        - On per-row failure, write safe fallback row and mark for review.
      file_level:
        - On input/output path failure, raise clear actionable error.
      consistency_level:
        - If summary counts do not reconcile, raise runtime error to prevent silent corruption.
