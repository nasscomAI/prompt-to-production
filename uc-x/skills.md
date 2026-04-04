skills:
  - name: retrieve_documents
    description: >
      Loads the 3 target policy text files (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`) 
      and indexes them explicitly by document name and numeric section header to prevent crossover retrieval.
    input: >
      A list of valid file paths pointing to the policy files.
    output: >
      A structured dictionary isolating contextual blocks linked by `Document_Name -> Section_ID -> Content`.
    error_handling: >
      If a file fails to load or parse, log a warning describing the parse error, but leave its dictionary partition empty—do 
      not allow hallucinated fallback data to substitute.

  - name: answer_question
    description: >
      Searches the explicitly indexed documents to provide a single-source response that includes the 
      exact document name and section number in the response string.
    input: >
      The string question from the user CLI interface and the indexed structured context space.
    output: >
      A final response string correctly citing exact limits or limits extracted solely from a single matched section.
      If conditions for refusal are triggered, it outputs the REFUSAL TEMPLATE string verbatim.
    error_handling: >
      If search results yield multiple conflicting answers (such as querying cross-department permissions), or if the 
      result requires omitting a multi-condition rule, refuse the query via the REFUSAL TEMPLATE string.
      Do not permit the usage of 'while not explicitly covered' hedging.
