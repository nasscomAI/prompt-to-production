skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its content as structured numbered sections with clause references.
    input: >
      A single string: path to a plain-text .txt policy file (e.g.
      ../data/policy-documents/policy_hr_leave.txt), encoded in UTF-8.
    output: >
      A list of structured sections, each containing: section number,
      section title, and a list of numbered clauses (numbered sub-items)
      with their full original text preserved word-for-word.
    error_handling: >
      If the file does not exist, is not a .txt file, is empty, or cannot
      be decoded as UTF-8, return an error and do not attempt to summarise;
      never fabricate policy content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a faithful summary with clause references that preserves every binding obligation.
    input: >
      A list of structured sections as produced by retrieve_policy
      (section number, section title, list of numbered clauses with original text).
    output: >
      A plain-text summary. Every numbered clause is represented with its
      clause number, its core obligation, and the original binding verb
      intact (must, will, may, requires, not permitted). Multi-condition
      obligations list every condition and every required approver.
    error_handling: >
      If a clause cannot be summarised without losing its meaning, quote it
      verbatim and flag it. If any numbered clause is absent from the input,
      flag the omission and refuse to produce a partial summary without
      noting the missing clause. Never add information not present in the
      source sections (no scope bleed).