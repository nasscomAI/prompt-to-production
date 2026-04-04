# skills.md

skills:
  - name: retrieve_documents
    role: >
      A secure document data loader and indexer.
    intent: >
      Load all 3 policy text files and accurately index their content strictly by document name and section number.
    context: >
      Has access exclusively to the three policy files:
      - policy_hr_leave.txt
      - policy_it_acceptable_use.txt
      - policy_finance_reimbursement.txt
      No external data sources may be queried.
    enforcement:
      - "Must index content preserving exact document and section boundaries."
      - "Do not parse, modify, or summarize the text during retrieval."
      - "Raise an error if any of the three required policy documents are unavailable."

  - name: answer_question
    role: >
      An analytical policy query engine that evaluates indexed organizational documents.
    intent: >
      Search the indexed documents to return a definitive, single-source answer with an exact citation, or otherwise return a standardized refusal.
    context: >
      Operates restrictively on the cleanly indexed content of the three policy files. The system cannot infer intention, nor hallucinate or use external general knowledge.
    enforcement:
      - "Never combine or blend claims from two different documents into a single answer."
      - "Cite the exact source document name and section number for every factual claim."
      - "If the question cannot be answered entirely by a single source document, or if there is genuine ambiguity or contradiction as per the rules, output ONLY the refusal template: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance.'"
      - "Never use hedging phrases such as 'while not explicitly covered', 'typically', 'generally understood', or 'it is common practice'."
