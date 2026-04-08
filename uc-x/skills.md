# skills.md — UC-X Policy Assistant

skills:
  - name: retrieve_documents
    description: Ingests the required policy text files and parses them into a searchable index partitioned by filename and section number to prevent data blending.
    input: List of paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index of all available policy mandates.
    error_handling: Reports an initialization failure if any of the three core source files are inaccessible.

  - name: answer_question
    description: Executes a single-source search against the policy index to provide precise, cited answers or an exact refusal when data is absent.
    input: Free-form text question from the employee.
    output: A multi-line response containing the factual claim, the citation [Document, Section], or the verbatim refusal template.
    error_handling: Identifying and refusing ambiguous or multi-source questions to prevent cross-document blending.
