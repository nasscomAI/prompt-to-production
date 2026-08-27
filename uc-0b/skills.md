# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses it into structured numbered sections, section titles, and individual numbered clauses.
    input: file_path (str: path to policy .txt file).
    output: dict containing document metadata, ordered section titles, and parsed clauses with identifiers and raw text.
    error_handling: Raises FileNotFoundError if the file does not exist, and handles unexpected or malformed section headers gracefully by aggregating non-header text into the current section.

  - name: summarize_policy
    description: Generates a high-fidelity, clause-referenced summary from parsed policy sections, ensuring zero clause omissions, preservation of all multi-condition approvals, and strict adherence to binding modal verbs.
    input: policy_data (dict: parsed policy document with sections and clauses).
    output: str (formatted plain-text policy summary with section headers and bulleted clause obligations).
    error_handling: Flags and verbatim-quotes any unsummarizable or ambiguous clauses to avoid condition dropping or obligation softening.
