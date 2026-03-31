skills:
  - name: retrieve_documents
    description: >
      Applies the deterministic regex ingestion from UC-0B to iterate across multiple `.txt` policy files.
      Strips non-essential line breaks and unnumbered content formatting to generate a structurally robust payload.
      Returns a highly optimized text corpus pre-fixed by file domains and exact hierarchical clause mappings.
    input:
      type: list of file paths
      format: E.g., `["../data/policy-documents/policy_hr_leave.txt", "..._it_acceptable_use.txt", "..._finance_reimbursement.txt"]`
    output:
      type: string
      format: A pre-processed, concatenated knowledge corpus formatted strictly as Document > Section > Clause.
    error_handling: >
      If a file fails to load, gracefully skips to the next file but logs a loud warning about missing contexts. 

  - name: answer_question
    description: >
      Invokes the LLM generation API with the synthesized document blob appended explicitly to the System Prompt mapping 
      the rigid strictures of `agents.md`. Initiates an interactive CLI loop securely capturing arbitrary human requests
      while preventing cross-document contamination during parsing via refusal matching.
    input:
      type: string
      format: The user's query retrieved actively via `input("> ")` inside an interactive loop.
    output:
      type: string
      format: The validated LLM-generated string strictly containing a single-source explicitly cited answer or refusal.
    error_handling: >
      If the LLM output matches forbidden heuristics like "typically" or "while not explicitly", it immediately blocks output 
      and injects the `This question is not covered in the available policy documents...` refusal template instead. 
