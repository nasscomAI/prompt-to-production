# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 mandatory policy files and systematically indexes their raw text stringently by their exact document names and section headers into a structured lookup base.
    input: An array or configuration indicating the paths to the 3 mandatory policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A comprehensive structured dictionary or index object organizing the extracted text mapped exclusively underneath specific document and section numerical identifiers.
    error_handling: Refuses to construct an incomplete index and raises a critical load fault if any of the three documents are missing, unavailable, or malformed.

  - name: answer_question
    description: Searches the explicitly indexed documents to fulfill user queries strictly utilizing single-source resolutions featuring precise citations or executing an uncompromising refusal format.
    input: The user's textual query string processed alongside the comprehensive document index previously generated.
    output: A rigidly formatted textual response providing the exact factual claim accompanied tightly by the source document name and section number, or alternatively passing the verbatim refusal template text.
    error_handling: Explicitly halts answer formulation and strictly triggers the verbatim refusal template if query responses require mixing rules across multiple documents, lack direct verifiable coverage, or necessitate conversational hedging/guessing.
