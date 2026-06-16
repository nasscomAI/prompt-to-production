# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files, parses them into a section-indexed structure keyed by document name and section number, and returns the index ready for search.
    input: >
      A single string: the path to the directory containing the three policy files.
      Example: data_dir="../data/policy-documents"
      The function loads exactly these three files from that directory:
        policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
      No other files may be added to the index.
    output: >
      A nested dict indexed by document name then section number:
        {
          "policy_hr_leave.txt": {
            "2.3": "Employees must submit a leave application at least 14 calendar days...",
            "5.2": "Leave Without Pay requires approval from the Department Head and the HR Director...",
            ...
          },
          "policy_it_acceptable_use.txt": { "3.1": "...", ... },
          "policy_finance_reimbursement.txt": { "2.6": "...", ... }
        }
      Section count and per-document section counts are printed to stdout on load.
      Abbreviations (LWP, DA, LOP, MFA, BYOD) are expanded in-memory before indexing.
    error_handling: >
      If any of the three files is missing, abort with a clear FileNotFoundError
      naming the missing file — do not load a partial index.
      If a document contains no detectable section numbers, load it as a single
      entry under key "body" and emit a warning — never silently skip a document.
      The index must contain all three documents before answer_question may be called.

  - name: answer_question
    description: Searches the document index for a single-source answer to the user's question, returning either a cited factual answer from one document+section or the exact refusal template — never a blended or hedged response.
    input: >
      Two values:
        index    — the nested dict returned by retrieve_documents
        question — the user's question as a plain string
      Example: answer_question(index, "Can I carry forward unused annual leave?")
    output: >
      A dict with exactly three fields:
        answer   — the factual answer text drawn verbatim or closely paraphrased
                   from a single section, OR the exact refusal template string if
                   not covered (see enforcement rule 3 in agents.md)
        source   — document filename + section number, e.g.
                   "policy_hr_leave.txt § 2.6"
                   Set to None when the refusal template is used.
        answered — boolean: True if a source was found, False if refusal template used
      Example (answered):
        {"answer": "Employees may carry forward a maximum of 5 unused annual leave days...",
         "source": "policy_hr_leave.txt § 2.6", "answered": True}
      Example (refused):
        {"answer": "This question is not covered in the available policy documents
         (policy_hr_leave.txt, policy_it_acceptable_use.txt,
         policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.",
         "source": None, "answered": False}
    error_handling: >
      If the index contains fewer than three documents, raise ValueError and refuse
      to answer — a partial index may produce cross-document blending.
      If keyword matching returns candidate sections from more than one document,
      return only the highest-confidence single-source match; never merge across
      documents. If no match exceeds the confidence threshold, use the refusal
      template exactly — no variations, no hedging phrases such as 'while not
      explicitly covered', 'typically', 'generally understood', or 'it is common
      practice'.
