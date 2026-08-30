skills:
  - name: retrieve_documents
    description: Loads all three policy documents, indexes them by document name and section number, and returns a searchable structure for use by answer_question.
    input: A list of file paths (list of str). Each file must be a .txt policy document with numbered sections.
    output: A dict mapping document_name (str) to a dict of section_number (str) → section_text (str). Example structure — {'policy_hr_leave.txt': {'2.3': 'Employees must submit...', ...}, ...}.
    error_handling: If any file is not found, raise FileNotFoundError with the path. If a file cannot be parsed into sections, load it as a single entry under section 'FULL'. Log warnings to stderr but continue loading other documents.

  - name: answer_question
    description: Searches indexed documents for an answer to a question. Returns a single-source cited answer or the exact refusal template — never a blended multi-source answer.
    input: question (str), indexed_documents (dict from retrieve_documents).
    output: A str containing either — (a) the answer with explicit citation in format '[document_name, section X.X]', or (b) the exact refusal template if the question cannot be answered from any single document without combining sources.
    error_handling: If indexed_documents is empty, return the refusal template. If the question matches content in two documents and a single-source answer is not possible, return the refusal template rather than blending. Never return an empty string — always return either an answer with citation or the refusal template.
