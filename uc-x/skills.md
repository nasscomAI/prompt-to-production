skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and parses their content into a structured list of section objects.
    input: String path to the folder containing the policy text files.
    output: List of dictionaries, each containing filename, section number, and text.
    error_handling: Skips files that cannot be read or are missing without crashing.

  - name: answer_question
    description: Matches queries against parsed document sections and returns a single-source cited answer or the exact refusal template.
    input: String query and list of parsed section dictionaries.
    output: String answer citing the source document and section, or the exact refusal template.
    error_handling: Returns the exact refusal template if the question is not covered in any section or is highly ambiguous.
