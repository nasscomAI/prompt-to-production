skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input:
      type: file_path
      format: "Relative or absolute path to a plain-text policy document (e.g. ../data/policy-documents/policy_hr_leave.txt)"
    output:
      type: structured_sections
      format: "A list of section objects, each containing the section number (e.g. '2.3'), the section heading (e.g. 'ANNUAL LEAVE'), and the full verbatim text of that clause"
    error_handling: >
      If the file path is invalid or the file does not exist, return an error
      and do not proceed. If the file is not a plain-text document or contains
      no recognisable numbered clauses, return an error indicating the format
      is unsupported. Never fabricate or infer section content from partial
      data.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, preserving all conditions and binding verbs.
    input:
      type: structured_sections
      format: "The list of section objects returned by retrieve_policy, each containing section number, heading, and verbatim clause text"
    output:
      type: summary_document
      format: "A plain-text summary where each entry is prefixed with its source clause number (e.g. '[2.3]'), preserves all binding verbs, conditions, thresholds, and approvers exactly as stated in the source"
    error_handling: >
      If any numbered clause from the source is missing from the output,
      halt and flag the omission before returning. If a clause contains
      multi-condition obligations (e.g. multiple required approvers), verify
      all conditions are preserved; if any condition would be lost during
      summarisation, quote the clause verbatim and flag it with
      '[verbatim — meaning loss risk]'. If the input contains scope-bleed
      language not present in the original source document (e.g. 'as is
      standard practice', 'typically in government organisations'), reject
      it and return an error. Never add information not present in the
      source sections.
