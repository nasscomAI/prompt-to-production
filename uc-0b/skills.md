# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A file path to a .txt policy document (e.g. policy_hr_leave.txt).
    output: A list of sections, each with section_number, title, and full text content preserving all original wording, binding verbs, and conditions.
    error_handling: If file does not exist or is empty, returns an error message and halts — never produces a summary from missing input. If file is not a .txt format, refuses and reports the unsupported format.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary with clause references, preserving every obligation and condition.
    input: A list of structured sections (output of retrieve_policy) containing section numbers and full text.
    output: A summary text file where each clause is summarised with its section reference (e.g. "Section 2.3"), all binding verbs preserved exactly, all conditions and approvers listed, and any clause that risks meaning loss is quoted verbatim with a [VERBATIM] flag.
    error_handling: If a clause contains multi-condition obligations (e.g. two required approvers), flags it for extra scrutiny and preserves all conditions. If a binding verb cannot be preserved without altering meaning, quotes the clause verbatim rather than paraphrasing. Never silently drops a clause — logs a warning if any section from input is absent in output.
