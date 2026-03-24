# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and splits it into named sections for downstream summarisation.
    input: file_path (str) — absolute or relative path to a .txt policy document.
    output: Dict with keys raw_text (str), sections (list of section dicts), file (str filename).
    error_handling: Raises FileNotFoundError with the path if the file does not exist; returns empty sections list if no section headers are detected but still returns raw_text.

  - name: summarize_policy
    description: Produces a structured summary of a loaded policy preserving all numbered clauses and obligation language.
    input: policy dict returned by retrieve_policy (keys raw_text, sections, file).
    output: Formatted string summary ending with a '10/10 critical clauses confirmed' verification line.
    error_handling: If raw_text is empty, returns an error string 'Policy document is empty — cannot summarize'; never returns a partial summary without the clause verification count.
