# skills.md — UC-0B HR Leave Policy Summarizer

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured
      numbered sections with clause numbers.
    input: >
      path — path to the policy .txt file.
    output: >
      list of (section_title, [(clause_no, clause_text), ...]) in document
      order; clause text is normalised to single lines.
    error_handling: >
      Missing or unreadable file reports an error and exits without
      producing output. Non-clause lines (headers, box-drawing separators)
      are skipped, never treated as content.

  - name: summarize_policy
    description: >
      Produces a compliant clause-by-clause summary with section grouping
      and a coverage check against the 10 critical clauses.
    input: >
      sections — structured sections produced by retrieve_policy.
    output: >
      str — full summary text with every numbered clause, binding verbs
      intact, and a CLAUSE COVERAGE CHECK section.
    error_handling: >
      Any critical clause missing from the parsed document is explicitly
      flagged in the output as [FLAGGED]; the summariser never silently
      omits or invents content.