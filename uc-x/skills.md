skills:
  - name: retrieve_documents
    description: Load and index the supplied policy text files, splitting
      content into numbered sections and subsection clauses for precise
      citation.
    input:
      - `file_paths` (list[string]): paths to the policy text files.
    output:
      - `index` (dict): mapping `filename` -> list of `{section: str, text: str}`
      - `errors` (list[string]): any file read or parse errors.
    error_handling:
      - If a file is missing or unreadable, include a message in `errors` and
        continue indexing other files.

  - name: answer_question
    description: Given an indexed corpus and a question, return a single-source
      answer with exact citation or the refusal template if not covered.
    input:
      - `index` (as returned from `retrieve_documents`).
      - `question` (string): the user's natural-language question.
    output:
      - `answer` (string) OR `refusal` (string): if refusal, this must match the
        exact refusal template verbatim.
      - `citation` (dict): `{filename: str, section: str}` when `answer` is returned.
      - `score` (float): match score used to choose the source (for auditing).
    error_handling:
      - If multiple documents provide equally strong, distinct answers, return
        the refusal template (do not blend sources).
      - Do not use hedging language in returned `answer` strings.
