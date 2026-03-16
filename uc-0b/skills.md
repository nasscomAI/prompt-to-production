skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as an ordered list of numbered sections with their clause text intact.
    input: A file path string pointing to a .txt policy document (e.g. policy_hr_leave.txt).
    output: A list of dicts, each containing a section heading (e.g. "2. ANNUAL LEAVE") and a list of clauses, where each clause is a dict with keys clause_id (e.g. "2.3") and text (the full verbatim clause text from the source).
    error_handling: If the file is not found or unreadable, raise a FileNotFoundError with the path. If the file is empty, raise a ValueError. Never return partial content silently.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and produces a compliant, clause-faithful summary with every clause number cited, all conditions preserved, binding verbs unchanged, and no externally sourced content added.
    input: A list of structured section/clause dicts as returned by retrieve_policy (clause_id and verbatim text per clause).
    output: A formatted plain-text summary string where each clause is represented as "§<clause_id>: <summary_sentence>", multi-condition clauses preserve all conditions, and any clause that cannot be summarised without meaning loss is reproduced verbatim and appended with the flag [VERBATIM – summarisation would lose meaning].
    error_handling: If a clause text is empty or missing, include the clause_id in the output with the note [CLAUSE TEXT MISSING – verify source document] and continue processing remaining clauses. Never silently skip a clause.
