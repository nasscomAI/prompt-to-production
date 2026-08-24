# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy documents and indexes their content by document name
      and section number. Each section is stored in an isolated namespace so that
      retrieval always knows which document a clause came from. No cross-document
      indexing or merging is performed.
    input: >
      doc_dir (str): directory path containing the three policy .txt files.
      Expected files: policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      A Python dict (the "index") with structure:
        { document_filename: { section_number: section_text, ... }, ... }
      Each document is a separate top-level key. Section text includes the heading
      and all clause text for that section.
    error_handling: >
      If any of the three expected files is missing, raise FileNotFoundError listing
      the missing files. Never return a partial index silently.

  - name: answer_question
    description: >
      Searches the document index for the most relevant clause(s) matching the
      question. Returns a single-source answer with citation, OR the exact refusal
      template if the answer requires blending documents or is not in any document.
      Never guesses. Never hedges.
    input: >
      question (str): the user's question in natural language.
      index (dict): the document index returned by retrieve_documents.
    output: >
      A string formatted as:
        Source: [filename], Section [X.X]
        [Answer text citing the clause]
      OR the exact refusal template when not answerable from a single document.
    error_handling: >
      If index is empty, return: "ERROR: No documents loaded. Cannot answer questions."
      If question is empty or only whitespace, return: "Please enter a question."
      Never raise an unhandled exception.

# ── Refusal Template (exact wording — no variations permitted) ────────────────
# This question is not covered in the available policy documents
# (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
# Please contact [relevant team] for guidance.
#
# ── The 7 Test Questions and Expected Behaviour ───────────────────────────────
# Q1: "Can I carry forward unused annual leave?"
#     → HR policy section 2.6 — exact limit (5 days), exact forfeiture date (31 Dec)
# Q2: "Can I install Slack on my work laptop?"
#     → IT policy section 2.3 — requires written IT approval
# Q3: "What is the home office equipment allowance?"
#     → Finance section 3.1 — Rs 8,000 one-time, permanent WFH only
# Q4: "Can I use my personal phone for work files from home?"
#     → IT policy section 3.1 ONLY — email and self-service portal only. No blending.
# Q5: "What is the company view on flexible working culture?"
#     → Refusal template — not in any document
# Q6: "Can I claim DA and meal receipts on the same day?"
#     → Finance section 2.6 — NO, explicitly prohibited
# Q7: "Who approves leave without pay?"
#     → HR section 5.2 — Department Head AND HR Director (BOTH required)
#
# ── Document Namespace Map ────────────────────────────────────────────────────
# policy_hr_leave.txt       : leave entitlements, sick leave, LWP, encashment
# policy_it_acceptable_use.txt : corporate devices, BYOD, passwords, data handling
# policy_finance_reimbursement.txt : travel, WFH equipment, training, mobile/internet
