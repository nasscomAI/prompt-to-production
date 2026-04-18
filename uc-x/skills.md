# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Ingests all mandatory policy documents (HR, IT, Finance) and creates a searchable index organized by document name and section number.
    input: A list of file paths to the three policy .txt files.
    output: A searchable index mapping document names and section numbers to their respective policy content.
    error_handling: If any of the three required policy files are missing or unreadable, the process must halt with a 'DOCUMENT_ACCESS_ERROR'.

  - name: answer_question
    description: Retrieves information from a single source document to answer a query, ensuring strict adherence to the refusal template if no answer is found.
    input: A natural language user query and the searchable document index.
    output: A precise answer string with a [Document Name, Section Number] citation, or the verbatim refusal template.
    error_handling: If the query leads to conflicting information across documents or is not covered in the text, the skill must trigger the exact refusal template rather than attempting to blend sources or guess.
