# skills.md — UC-0B Policy Summary Skills
# Aligned with agents.md RICE enforcement

skills:
  - name: retrieve_policy
    description: Load policy text file and structure it into numbered sections with clause references and binding verbs extracted.
    
    input: |
      String: file path to policy_hr_leave.txt (or equivalent policy document).
    
    output: |
      Dict with structure:
      {
        "raw_text": "...",
        "sections": [
          {
            "number": "2.3",
            "title": "Annual Leave Advance Notice",
            "text": "Employees must submit a leave application at least 14 calendar days in advance...",
            "binding_verb": "must",
            "conditions": ["14 calendar days", "advance", "Form HR-L1"]
          },
          ... (all numbered clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 expected)
        ]
      }
    
    enforcement:
      - "E1_extraction: Identify and extract all numbered clauses. Minimum 10 expected (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)."
      - "E2_condition_count: For multi-condition clauses (e.g., 5.2 requires X AND Y), extract all conditions and count them."
      - "E3_binding_verb: Extract the binding verb (must, may, requires, will, not permitted) exactly as stated in source."
      - "E4_raw_preservation: Always preserve raw_text for fallback and verification purposes."
    
    error_handling: |
      If file does not exist: return error with file path and gracefully fail.
      If file is empty: return empty sections array but preserve raw_text="".
      If a clause has ambiguous conditions: include all identified conditions; flag in output if uncertain.

  - name: summarize_policy
    description: Take structured policy sections and produce a summary that preserves all clauses, conditions, and binding verbs without omission, softening, or scope bleed.
    
    input: |
      Dict from retrieve_policy with keys: raw_text, sections (array of clause dicts).
      sections[i] has: number, title, text, binding_verb, conditions
    
    output: |
      String: summary text with:
      - All 10 clauses referenced by number (2.3, 2.4, etc.) and included
      - Each clause summary sentence cites the clause number and binding verb exactly
      - All conditions from multi-condition clauses preserved (all N conditions listed for clause with N conditions)
      - Zero phrases from outside the source document
      - Potential verbatim quotes marked with "SOURCE QUOTE:" if meaning loss would occur
      
      Example format:
      "Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance.
       Clause 2.4: Written approval from the manager must be received before leave commences; verbal approval is not valid.
       Clause 5.2: LWP requires approval from the Department Head and the HR Director (both required)."
    
    enforcement:
      - "E1_clause_presence: Output must include all 10 expected clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2). Verify count."
      - "E2_multi_condition_all: For clauses with multiple conditions, list all. Clause 5.2: Do NOT write 'LWP requires approval' without specifying both approvers."
      - "E3_binding_verb_exact: Preserve exact binding verbs (must→must, may→may, requires→requires, will→will, not permitted→not permitted). No softening."
      - "E4_no_scope_bleed: Every sentence must be traceable to source_text. Reject generalisations and external knowledge phrases."
      - "E5_fallback_quote: If a clause is high-risk (especially binding verb + condition chains), include verbatim quote with 'SOURCE QUOTE:' tag instead of paraphrasing."
    
    error_handling: |
      If input sections array is empty: return summary="" with warning that no clauses were extracted.
      If a clause binding_verb is ambiguous or null: flag it and include verbatim SOURCE QUOTE instead of attempting to paraphrase.
      If conditions array is empty for a multi-condition clause: flag as potential extraction error and include verbatim quote.
      If summary would omit any of the 10 expected clauses: raise error and return incomplete summary with list of missing clauses.
