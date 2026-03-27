skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt,   policy_finance_reimbursement.txt
    output: indexed structure {document_name: string → sections: {section_num: string → text: string}}
    error_handling: If any policy file not found, raise IOError listing missing file. If file cannot be read, raise encoding error. Never skip sections during parsing. If document structure cannot be parsed, raise error indicating line number where structure breaks.

  - name: answer_question
    description: Search indexed documents for answer to employee question, return single-source answer with citation OR exact refusal template.
    input: string (employee question) + indexed document structure
    output: string (answer with citation like "policy_document.txt section X.Y: [answer]") OR exact refusal template
    error_handling: If question matches content from two different documents, check for single-source dominance — if no clear single source, return refusal template. If question text would require hedging phrase to answer, return refusal template instead. Never return cross-document blended answer. Never return answer that starts with "typically", "generally", "while not explicitly covered". If no match found in any document, return exact refusal template with no variations.
