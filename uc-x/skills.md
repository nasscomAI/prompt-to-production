# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes the three CMC policy documents into a clause-level index keyed by document name, section number, and document reference code.
    input: >
      Nothing (no arguments). Reads the fixed files
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt.
    output: >
      Dict mapping document filename -> {"reference": str (e.g. "HR-POL-001"),
      "clauses": list of {"section": "2.6", "text": str verbatim clause text}}.
      A clause starts at a line matching ^\d+\.\d+\s and continues through
      indented continuation lines until the next clause or section break.
    error_handling: >
      If any file is missing or unreadable, raise SystemExit(1) naming the
      missing file — never answer from a partial corpus. If no clauses are
      parsed from a file, treat it as unreadable.

  - name: answer_question
    description: Answers one employee question with either a single-source verbatim cited answer from exactly one policy document, or the exact refusal template.
    input: >
      One question string. The clause index produced by retrieve_documents.
    output: >
      A plain-text answer string that is exactly one of:
      (a) single-source answer — each line is a verbatim clause from ONE
          document followed by its citation "(REFERENCE §section)", prefixed
          by a "[Source: <filename>]" header; never mixes documents;
      (b) the refusal template reproduced character-for-character:
          "This question is not covered in the available policy documents\n
          (policy_hr_leave.txt, policy_it_acceptable_use.txt,\n
          policy_finance_reimbursement.txt).\n
          Please contact [relevant team] for guidance."
    error_handling: >
      Deterministic two-stage retrieval: (1) domain phrase index — curated
      policy phrases mapped to (document, sections); the document with the
      most specific phrase hits wins and ONLY its sections are used;
      (2) fallback keyword scoring with IDF over all clauses; best-scoring
      document wins, top clauses within 75% of the best score are quoted.
      If stage 1 has no hit AND stage 2's best clause scores below threshold
      (fewer than 2 distinct content-token matches), return the refusal
      template EXACTLY. Never blend: if both stages point at different
      documents, the higher-confidence result wins and other documents are
      dropped, never concatenated. Output is scanned for banned hedging
      phrases ("while not explicitly covered", "typically", "generally
      understood", "it is common practice") — presence aborts with an error
      instead of emitting invalid output.
