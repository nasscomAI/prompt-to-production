# skills.md — UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Load a .txt policy document and extract structured numbered sections without changing wording.
    input: "Path to policy text file, such as ../data/policy-documents/policy_hr_leave.txt."
    output: "Structured section list with fields: clause_id, source_text, obligation_terms, and explicit conditions found in each clause."
    error_handling: "If file is missing or unreadable, return a clear retrieval error and stop. If clause numbering cannot be parsed, return partial parsed sections plus a review warning; do not fabricate clause IDs."

  - name: summarize_policy
    description: Generate a clause-referenced summary from structured sections while preserving legal and operational meaning.
    input: "Structured sections from retrieve_policy including clause IDs and exact source wording."
    output: "Summary text with one mapped entry per clause, preserving obligation strength and all required conditions, with verbatim quote fallback when lossless summarization is not possible."
    error_handling: "If any clause cannot be summarized without condition loss, include that clause verbatim and append REVIEW_REQUIRED. If a required clause is missing from input structure, emit an explicit completeness error instead of guessing content."
