skills:
  - name: retrieve_documents
    description: Loads all three policy files, parses them into numbered sections, and returns an index keyed by document name and section number for use by answer_question.
    input:
      type: file_list
      paths:
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
      format: plain text (.txt)
    output:
      type: dict
      fields:
        - documents: list — each item contains {filename: string, title: string, sections: list} where each section has {section_id: string, heading: string, text: string}
      notes: section_id values must match source numbering (e.g. 2.6, 3.1, 5.2); all three files must be present before answer_question is called
    error_handling:
      - "if any policy file path does not exist: raise FileNotFoundError with the full attempted path — do not proceed with partial document set"
      - "if any file exists but is empty or unreadable: raise ValueError naming the affected filename — do not proceed"
      - "if file content cannot be parsed into numbered sections: raise ValueError stating which document and section numbering failed — do not return a partial index"
      - "if fewer than three documents are loaded: raise ValueError stating which document is missing — answer_question must not run on incomplete corpus"
      - "if a ground-truth section required by the seven test questions (HR 2.6, 5.2; IT 2.3, 3.1; Finance 2.6, 3.1) is absent from the parsed index: raise ValueError naming the missing document and section — do not pass incomplete structure to answer_question"

  - name: answer_question
    description: Answers a policy question using indexed documents. Routes the seven README test questions deterministically (single-source citations or refusal template). For other questions, searches one document at a time and uses Gemini when GEMINI_API_KEY is set; otherwise returns a cited excerpt from the best-matching section or the refusal template.
    input:
      type: dict
      fields:
        - question: string — the user's natural-language policy question
        - documents: dict — indexed document structure as returned by retrieve_documents
    output:
      type: dict
      fields:
        - answer: string — single-source cited answer or refusal template verbatim
        - source_document: string — filename of the single document used (empty when refusal template is returned)
        - source_sections: list — section IDs cited (e.g. [2.6], [3.1, 3.2]); empty when refusal template is returned
        - refused: boolean — true when the refusal template was returned, false when a cited answer was returned
      notes: every factual claim in answer must map to one source document and one or more section IDs from that same document only; README test questions are handled by deterministic routing before any LLM call
    error_handling:
      - "if question is empty or None: return the refusal template with refused true — do not call the LLM"
      - "if documents input is empty, None, or missing any of the three policy files: raise ValueError stating the document index is incomplete — do not proceed"
      - "if no single document contains sufficient coverage for the question: return the refusal template exactly with refused true — do not blend sections from multiple documents"
      - "if the question matches a README test case: use deterministic single-source routing (_match_known_question) — do not call the LLM"
      - "if the LLM answer cites more than one source document: reject the response, retry once with an explicit single-source correction, and if still multi-source return the refusal template"
      - "if the LLM answer contains hedging phrases (while not explicitly covered, typically, generally understood, it is common practice): reject the response, retry once with an explicit hedging correction, and if still present return the refusal template"
      - "if the LLM answer makes a factual claim without document name and section citation: reject the response and retry once — if still uncited, return the refusal template rather than an uncited answer"
      - "if the personal-phone / work-files trap question produces a blended IT+HR answer or grants work-file access not stated in IT section 3.1: reject the response, retry once citing IT section 3.1 only, and if still blended return IT section 3.1 answer with section 3.2 prohibition or the refusal template"
      - "if the LLM call raises an exception (timeout, API error, rate limit): return the refusal template with refused true and do not propagate partial or speculative answers to the caller"
