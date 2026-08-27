skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of structured sections, each containing the section number, title, and a list of numbered sub-clauses.
    input: file_path (string, absolute or relative path to a .txt policy document)
    output: list of dicts, each with keys section_num (string), title (string), clauses (list of dicts with keys clause_num (string) and text (string))
    error_handling: If the file is not found, raise FileNotFoundError with the file path. If a section block cannot be parsed into numbered sub-clauses, include it as an unparsed entry with clause_num set to "UNPARSED" so it is not silently dropped.

  - name: summarize_policy
    description: Takes a list of structured policy sections and produces a clause-by-clause plain-text summary preserving every numbered obligation and all multi-condition rules exactly as stated in the source.
    input: list of section dicts as returned by retrieve_policy, each containing section_num, title, and clauses
    output: string containing a formatted text summary with each clause listed by number, its binding obligation preserved verbatim or near-verbatim, and multi-condition clauses explicitly listing all conditions; clauses that cannot be summarised without meaning loss are quoted verbatim and marked [VERBATIM]
    error_handling: If the input sections list is empty, return the string "No policy content to summarise." If a clause dict is missing the text key, mark that entry [MISSING CLAUSE TEXT — NEEDS REVIEW] rather than omitting it silently.
