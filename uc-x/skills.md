# skills.md

skills:
  - name: retrieve_documents
    description: Recursively loads all 3 distinct policy files matching the input schema and explicitly indexes them natively by their systemic document name and internal structural section numbers.
    input: File paths pointing directly to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    output: An aggregated structured knowledge array strictly isolating data by source file identity and explicitly annotated section demarcations to block indexing cross-contamination.
    error_handling: Halts execution if a document is unreadable or fails structural section indexing to prevent corrupted grounding context.

  - name: answer_question
    description: Executes a controlled retrieval generation sweep across the indexed documents using the explicit system bounds set exactly in agents.md.
    input: The user's query alongside the strictly segregated multi-document structural reference block built by retrieve_documents.
    output: A rigid string output returning either a single-source explicit citation (File + Section Number) or invoking the mandated refusal template format explicitly.
    error_handling: Identifies conflicting multi-source hits or lack of coverage natively and triggers the exact refusal template block provided in the agents.md framework.
