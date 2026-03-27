# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: Paths to the HR, IT, and Finance policy .txt files.
    output: Indexed collection of policy sections categorized by document names.
    error_handling: Raise an error if any of the three required policy documents is missing or unreadable.

  - name: answer_question
    description: Searches indexed documents and returns a strictly single-sourced answer with a citation, or the exact refusal template.
    input: Indexed policy documents and the user's question (string).
    output: A single-source factual answer including document name and section number, or the verbatim refusal template.
    error_handling: If the answer requires blending documents or cannot be deterministically found in a single section, return the exact refusal template without any additional explanation.
