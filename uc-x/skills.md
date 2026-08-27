skills:
  - name: retrieve_documents 
    description: Loads all three policy files and builds an in-memory index keyed by document filename and section number.
    input:
      type: list of file paths
      format: "Ordered list of three plain-text file paths: ../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, ../data/policy-documents/policy_finance_reimbursement.txt"
    output:
      type: indexed document store
      format: "Dictionary mapping (filename, section_number) -> section_text; each entry preserves the original section heading and body verbatim"
    error_handling: >
      If a file is missing or unreadable, raise a load error naming the specific file and halt — do not answer questions against a partial index.
      If a file contains no parseable section markers, log a warning and store the entire file body under section '0' for that document so retrieval can still attempt a match.

  - name: answer_question
    description: Searches the indexed document store for a single-source answer to the user's question and returns it with a citation, or returns the verbatim refusal template if no sufficient single-source answer exists.
    input:
      type: string
      format: "A natural-language question string from the user, plus the indexed document store produced by retrieve_documents"
    output:
      type: string
      format: "Either (a) a factual answer drawn from one document section followed by an inline citation in the format '(Source: <filename>, Section <number>)', or (b) the exact refusal string: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'"
    error_handling: >
      If the search returns matching sections from more than one document, do not blend them — return the refusal template instead.
      If the answer candidate contains any hedging phrase ('while not explicitly covered', 'typically', 'generally understood', 'it is common practice'), discard it and return the refusal template.
      If the indexed store is empty or was not provided, raise an error and do not attempt to answer.
