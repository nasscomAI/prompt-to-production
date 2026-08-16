skills:

  - name: retrieve_documents
    description: >
      Loads and indexes the 3 CMC policy documents (HR Leave, IT Acceptable Use,
      Finance Reimbursement), organizing content by document name, section number,
      clause ID, and content text for fast and accurate single-source retrieval.
    input: >
      Directory path or list of file paths to the policy document text files.
    output: >
      An indexed repository structure containing document metadata, section headers,
      clauses, and keyword/intent mapping.
    error_handling: >
      Raises FileNotFoundError if any required policy file is missing.
      Validates that all 3 policy documents are successfully indexed before serving queries.

  - name: answer_question
    description: >
      Searches indexed policy documents for relevant sections, enforces single-source
      attribution, prohibits cross-document blending, formats exact citations,
      and applies the standard refusal template when the question is out of scope.
    input: >
      A question string from an employee or test suite.
    output: >
      A formatted answer string citing document filename and section number, or
      the exact standard refusal template.
    error_handling: >
      If query is out of scope, ambiguous, or lacks explicit grounding in the policy text,
      returns the exact refusal template citing the relevant contact team (HR, IT, Finance, or Legal).
