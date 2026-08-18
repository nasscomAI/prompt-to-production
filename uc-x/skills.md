skills:
  - name: retrieve_documents
    description: Loads all three CMC policy .txt files, parses them into a section-indexed structure keyed by document name and section number, ready for search.
    input: A list of file path strings, one for each policy document (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A dict keyed by document filename, each value being a list of clause dicts with keys section_id (e.g. "3.1"), section_heading (e.g. "PERSONAL DEVICES (BYOD)"), and text (full verbatim clause text from the source).
    error_handling: If any file is not found or unreadable, raise FileNotFoundError for that file and halt — do not proceed with partial document sets, as a missing document would produce incomplete and potentially misleading answers. If a file is empty, raise ValueError.

  - name: answer_question
    description: Searches the indexed documents for clauses relevant to the user's question and returns a single-source answer with citation, separate per-document answers if multiple documents are relevant, or the verbatim refusal template if no document covers the question.
    input: A string containing the user's natural language question, and the document index dict returned by retrieve_documents.
    output: A string — either (a) a direct answer with citation(s) in the format [policy_<name>.txt §<section>] for every factual claim, or (b) if the question spans multiple documents, separate cited answers per document clearly labelled by source, never blended, or (c) the verbatim refusal template if the question is not found in any document.
    error_handling: If the question is empty or unparseable, prompt the user to rephrase. If keyword search returns no matching clauses, output the refusal template. Never guess, infer, or use general knowledge — the refusal template is the required fallback, not a hedged answer.
