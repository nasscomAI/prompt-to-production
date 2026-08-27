# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections for processing.
    input: >
      A file path (string) to a .txt policy document.
    output: >
      A dictionary with keys:
      - metadata: dict with title, document_ref, version, effective_date
      - sections: list of dicts, each with 'number' (e.g., "1"), 'title' (e.g., "PURPOSE AND SCOPE"), 
        and 'clauses' (list of dicts with 'number' and 'text')
    error_handling: >
      If file doesn't exist: raise FileNotFoundError with descriptive message.
      If file is empty: return structure with empty sections list.
      If file has no recognizable sections: return all content as a single section "1. GENERAL".

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses and conditions.
    input: >
      A dictionary with 'metadata' and 'sections' as returned by retrieve_policy.
    output: >
      A formatted string containing:
      - Document header (title, reference, version, effective date)
      - Section-by-section summary with clause references
      - Each clause summarized with its number preserved
      - [VERBATIM] flag for complex clauses quoted directly
    error_handling: >
      If sections is empty: return header with note "No policy content found".
      If a clause has ambiguous meaning: include [REVIEW NEEDED] flag.
      Never omit a clause — if summarization fails, quote verbatim.
