# skills.md — UC-X Policy Q&A Skills
# Aligned with agents.md RICE enforcement

skills:
  - name: retrieve_documents
    description: Load all 3 policy documents, parse section structure, index by document name and section number.
    
    input: |\n      Paths to 3 policy files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    
    output: |
      Dict with documents indexed by section number and keyword-searchable structure.
      Example: documents["policy_hr_leave.txt"]["sections"]["2.6"] = {heading, text, key_phrases}
    
    enforcement:
      - "E1_parse: Extract all sections numbered X.Y. Preserve section headings and full text."
      - "E2_index: Build keyword index mapping common phrases to [document, section] pairs."
      - "E3_metadata: Extract document title, version, effective date from header for citation."
    
    error_handling: |
      If file not found: log error, skip document, continue if >= 1 loads.
      If section structure malformed: log warning, include partial text if readable.

  - name: answer_question
    description: Search indexed documents for user question, return single-source answer with citation OR exact refusal template.
    
    input: |
      - user_question (str): Natural language question from user
      - documents (dict): Indexed document structure from retrieve_documents
      - refusal_template (str): Exact template to use if not in documents
    
    output: |
      Dict with answer, source, answer_type (direct/refusal), conditions_preserved flag, hedging_phrases flag.
    
    enforcement:
      - "E1_single_source: Answer from one document section only. If multiple documents relevant, return refusal."
      - "E2_citation: Include [Document Name - Section X.Y] in answer. No citation = no answer."
      - "E3_no_hedging: Scan for hedging phrases; if found, rewrite or return refusal."
      - "E4_refusal_check: If not in documents or requires multi-document synthesis, return refusal_template verbatim."
      - "E5_condition_check: Preserve ALL source conditions (e.g., 'only', 'and', without dropping)."
    
    error_handling: |
      If no section matches: return refusal template.
      If multiple documents contradictory: return refusal (contact departments separately).
      If section ambiguous: return refusal (do not guess).
      If question blank: prompt user to ask a question.
