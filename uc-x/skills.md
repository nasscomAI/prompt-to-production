skills:
  - name: retrieve_documents
    description: Load all policy text documents and index their contents by document name and section/clause number for fast retrieval.
    input: list of file paths to policy text files.
    output: An index structure (e.g., dict mapping keys to text snippets) mapping document name and section/clause number to their respective policy rules.
    error_handling: Fail gracefully or warn if a document is missing or cannot be parsed, and proceed to index available documents.

  - name: answer_question
    description: Search the indexed documents to answer a user's question, ensuring single-source answers with exact citations, no cross-document blending, no hedging, and returning the exact refusal template if the answer is not found.
    input: question (str), indexed_documents (index structure).
    output: A string containing the direct single-sourced answer with a citation (e.g., "(policy_hr_leave.txt Section 2.6)") OR the exact refusal template.
    error_handling: If the query matches information in multiple conflicting ways or is not answered in the text, or if it causes cross-document blending ambiguity, output the exact refusal template.
