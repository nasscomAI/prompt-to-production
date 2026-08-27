skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files and indexes them by document name
      and section number for search.
    input: >
      A list of file paths (list of strings) pointing to the three policy
      .txt files.
    output: >
      A dict mapping document names (e.g. "policy_hr_leave.txt") to their
      parsed content as {section_heading: [clause_strings]}. Returns
      {"error": "File not found"} if any path does not exist.
    error_handling: >
      If any file does not exist, return {"error": "File not found:
      [filename]"}. If any file is empty or unreadable, return {"error":
      "Invalid file: [filename]"}. All three files must load successfully
      or the entire operation fails.

  - name: answer_question
    description: >
      Searches the indexed policy documents for a question and returns a
      single-source answer with citation, or the refusal template if the
      question is not covered.
    input: >
      A question string, plus the indexed document dict from
      retrieve_documents.
    output: >
      A dict with keys: "answer" (string), "source" (document name or
      None), "section" (section heading or None), "refused" (bool). If
      the question is covered, answer contains the factual response with
      citation. If not covered, answer contains the exact refusal template
      and refused=True.
    error_handling: >
      If indexed documents dict is empty or invalid, return {"error":
      "Documents not loaded. Run retrieve_documents first."}.
