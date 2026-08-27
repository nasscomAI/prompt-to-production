skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses numbered clauses into structured sections.
    input: "file_path:string to .txt policy document with numbered clauses like 2.3"
    output: "ordered list of objects: {clause_id:string, text:string}"
    error_handling: "If file is missing, unreadable, or has no numbered clauses, raise a clear error and stop without generating summary."

  - name: summarize_policy
    description: Produces a compliant summary from structured clauses while preserving each clause meaning.
    input: "ordered list of {clause_id, text} from retrieve_policy"
    output: "plain text summary lines with clause references and no added information"
    error_handling: "If summarization risks omission or condition drop, quote clause verbatim and mark it as quoted due to meaning-loss risk."
