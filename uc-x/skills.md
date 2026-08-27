skills:
  - name: retrieve_documents
    description: >
      Load all three CMC policy files and build a searchable index keyed by
      document filename and section number for use by answer_question.
    input: >
      Optional base_path (string, default ../data/policy-documents/). Expects
      policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt to exist at that path.
    output: >
      A document index (dict or in-memory structure) mapping each filename to
      parsed sections with section numbers and body text, retrievable by
      document name and section number.
    error_handling: >
      If any policy file is missing or unreadable, raise a clear file-level
      error naming the missing path before the CLI accepts questions. If a
      section header cannot be parsed, index the raw text under a fallback key
      and log the parse issue without crashing. Do not substitute content from
      other files or external sources when a file is absent.

  - name: answer_question
    description: >
      Search the indexed policy documents for a user question and return a
      single-source cited answer or the exact refusal template per UC-X
      enforcement rules.
    input: >
      question (string): natural-language staff question from the interactive
      CLI. document_index: output of retrieve_documents.
    output: >
      A response string printed to the terminal containing either (a) an answer
      drawn from one policy document only, with document filename and section
      number cited for every factual claim and all conditions preserved, or (b)
      the exact refusal template: This question is not covered in the available
      policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team] for
      guidance.
    error_handling: >
      If question is empty or whitespace, prompt the user to re-enter without
      calling the model or inventing an answer. If no section supports the
      question, or multiple documents would be needed to answer (cross-document
      blending), return the refusal template verbatim — no hedging phrases. If
      HR and IT both appear relevant but a single-source answer would overstate
      permission (e.g. personal phone access to work files from home), answer
      from IT policy section 3.1 only or refuse. If a matched section has
      multiple conditions (e.g. two approvers required), include every condition
      in the answer. Never crash on unrecognized questions; always return either
      a cited single-source answer or the refusal template.
