# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 authorized policy files and systematically indexes their content by document name and section number.
    input: List of file paths to the policy text files.
    output: An indexed knowledge structure mapping explicitly defined section numbers to their text within each specific document.
    error_handling: Abort initialization gracefully if any specified document path is unreachable or if sections cannot be reliably parsed.

  - name: answer_question
    description: Searches indexed documents and returns a clean, single-source answer bundled with a precise citation, OR triggering an exact refusal.
    input: The user's question string and the output from retrieve_documents.
    output: A factual answer strictly citing the document name and section number, OR the verbatim refusal template.
    error_handling: Immediately return the exact refusal template if the question's premise is not unambiguously covered by a single policy source, or if multiple policies conflict/blend to form the answer. No hedging is allowed.
