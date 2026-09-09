# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes content by document name and section number.
    input:
      type: list of strings (filepaths)
      format: [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
      ]
    output:
      type: dictionary (map<string, map<string, string>>)
      format: {
        document_name: {
          section_number: section_text
        }
      }
    error_handling: "Raises FileNotFoundError for missing or unreadable policy files; raises ValueError if section headers cannot be parsed."

  - name: answer_question
    description: Searches indexed policy documents and returns a single-source answer with citation, or the verbatim refusal template.
    input:
      type: object
      format: {
        question: string,
        index: map<document_name: string, map<section_number: string, section_text: string>>
      }
    output:
      type: string
      format: "<Answer text> (<document_name>, section <section_number>) OR \"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.\""
    error_handling: "Prevents cross-document blending by enforcing single-source answers or clean refusals. Prevents hedged hallucination by enforcing the exact refusal template without hedging phrases ('while not explicitly covered', 'typically', etc.) when information is missing. Prevents condition dropping by ensuring mandatory limits, approval chains, and forfeiture dates are retained."