# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Securely loads the specified three corporate policy documents and structurally indexes them, mapping clauses perfectly to their explicitly identified document name and respective section numbers natively.
    input: Implicit triggers or a list of predefined filepaths mapped specifically to the required triad of text documents (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`).
    output: A meticulously indexed data dictionary binding segmented clauses stringently to their exact file metadata (e.g. `policy_hr_leave.txt` - Section 2.6).
    error_handling: System halts execution rigorously if any foundational documents are inaccessible or structurally malformed to prevent blind spots or hallucinated compensation logic.

  - name: answer_question
    description: Executes scoped search strictly mapped against the indexed documents, yielding a terse answer natively citing its single, verified source segment effortlessly without deploying unprompted conceptual mixing.
    input: A string format user query requesting policy context paired tightly with the indexed dataset from `retrieve_documents`.
    output: A factual, non-assumptive string answer explicitly paired with its original literal file name and structural section number.
    error_handling: Any detection of blended-document answers across the three files or detection of unsupported gaps triggers a mandated fallback constraint utilizing the exact verbatim string template: `This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.`
