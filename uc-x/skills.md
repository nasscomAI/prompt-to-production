skills:
  - name: retrieve_documents
    description: Loads the three mandatory human resources, IT, and finance txt policies and indexes them structurally by section number mapping.
    input: File paths to policy directories.
    output: A dictionary index mapping document name and section numbers to raw text.
    error_handling: Handles missing files by failing fast, missing sections by returning empty structures.

  - name: answer_question
    description: Retrieves precisely localized single-document factual claims in response to user questions, avoiding all cross-document blending.
    input: User string query and the loaded documents dictionary index.
    output: A definitive textual answer complete with a mandatory document name and section number citation, or the exact refusal template.
    error_handling: Triggered when content sits outside explicit sections or crosses boundaries; outputs the verbatim refusal template.
