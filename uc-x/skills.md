# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes their content by document name and section number, ready for per-section lookup.
    input: List of file paths (list of str) for the three policy documents.
    output: Dict keyed by document filename, where each value is a dict of section_number (str) → section_text (str). Example structure: {"policy_hr_leave.txt": {"2.3": "Employees must submit...", ...}, ...}
    error_handling: If any file is missing or unreadable, raise FileNotFoundError naming that file — do not silently skip it. If a file is empty or contains no parseable sections, raise ValueError naming the file. All three documents must load successfully before the system accepts questions.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to a user question and returns either a cited answer or the exact refusal template.
    input: Question string (str); document index (dict, output of retrieve_documents).
    output: Dict with keys — answer (str), source_document (str or None), source_section (str or None), refused (bool). If answered: refused=False, answer contains the policy text, source_document and source_section cite the exact location. If refused: refused=True, answer contains the exact refusal template verbatim, source_document and source_section are None.
    error_handling: If the question matches sections in more than one document and combining them would be required for a complete answer, set refused=True and return the refusal template — do not blend. If the document index is empty, raise ValueError stating no documents are loaded.
