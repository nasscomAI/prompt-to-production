# skills.md — UC-0B Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered section objects.
    input: File path to policy document (--input).
    output: Data structure containing parsed policy sections, including section numbers, headings, and raw text.
    error_handling: Raises file unreadable warning if file path is invalid or empty, returning an empty section list gracefully.

  - name: summarize_policy
    description: Generates a clause-complete policy summary from structured sections while preserving binding verbs, multi-condition approvals, and exact clause citations.
    input: Structured policy sections object from retrieve_policy and output file path (--output).
    output: Writes summary_hr_leave.txt containing complete clause summary with section references.
    error_handling: Detects missing clause numbers or condition drops during generation, falling back to verbatim quotation with explicit warning flag.
