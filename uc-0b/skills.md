# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return it as structured, numbered sections and clauses.
    input: path — path to a policy .txt file with numbered sections (e.g. "2. ANNUAL LEAVE") and clauses (e.g. "2.3 ...").
    output: A dict {title, sections:[{number, heading, clauses:[{number, text}]}]}. Wrapped continuation lines are joined into their clause so no text is lost.
    error_handling: Divider and blank lines are skipped. Lines that are not a section header or clause and have no current clause are ignored. A clause's continuation lines are appended verbatim rather than dropped.

  - name: summarize_policy
    description: Produce a fidelity-preserving summary from structured sections — every clause verbatim, binding verb shown, multi-condition clauses flagged.
    input: structured — the dict returned by retrieve_policy.
    output: A string summary listing every clause in order with its number, binding verb, a MULTI-CONDITION flag where applicable, and the verbatim clause text. Ends with preserved/flagged counts.
    error_handling: Adds nothing not in the source. If a binding verb is not detected it is shown as "—" rather than guessed. Clause text is never paraphrased, so conditions cannot be silently dropped.
