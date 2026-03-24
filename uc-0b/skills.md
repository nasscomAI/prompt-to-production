# skills.md

skills:
  - name: retrieve_policy
    description: Loads HR policy text file and returns content structured by numbered clause sections with binding verbs and conditions preserved.
    input: File path to .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)
    output: Structured object with numbered clauses [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2], each containing clause text, binding verb (must/will/may/requires/not permitted), and identified conditions/approvers.
    error_handling: If file not found, return explicit FileNotFoundError. If clause numbering is inconsistent or missing, flag the line range and refuse to proceed — do not attempt to infer clause structure. If binding verb is ambiguous, preserve the exact source text and flag for manual review.

  - name: summarize_policy
    description: Converts structured policy sections into a compliant, legally binding summary that preserves all 10 numbered clauses with zero condition loss or scope addition.
    input: Structured policy object from retrieve_policy skill containing all 10 clauses with binding verbs and multi-step conditions (approvers, timeframes, exceptions).
    output: Summary document with each of the 10 clauses numbered and quoted. Multi-condition obligations (e.g., "requires Department Head AND HR Director approval") reproduced exactly. Any clause that cannot be condensed without meaning loss quoted verbatim with [MANUAL_REVIEW] flag.
    error_handling: If any of the 10 clauses cannot be represented in the summary without dropping a condition or softening a binding verb, halt and return [CLAUSE_RISK: clause_number] with the problematic text. Do not attempt to rephrase to force fit. If summary contains any phrase not present in source document (e.g., "as is standard practice", "typically"), reject output and flag scope bleed.
