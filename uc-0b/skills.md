# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy `.txt` document and parses it strictly into structured, mapped, numbered clause sections.
    input: Filepath pointing to the raw text policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured dataset (like a list or dictionary) containing each explicit numbered clause alongside its raw text.
    error_handling: Handles missing files by halting execution logically, and if structural parsing fails due to bad formatting, yields the raw text alongside an explicit parsing failure flag.

  - name: summarize_policy
    description: Processes the structured policy clauses to yield a compliant summary mapping 1:1 that flawlessly preserves strict constraints and multi-condition obligations without softening.
    input: The structured dataset of raw numbered clauses mapped by retrieve_policy.
    output: A newly compiled text string containing the terse summary mapping each numbered clause directly to its strict counterpart.
    error_handling: If a given complex clause cannot be compressed safely without dropping a condition or losing its strict meaning, skips summarization for that clause and outputs it fully verbatim paired with an explicit "NEEDS_REVIEW" flag.
