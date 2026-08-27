# agents.md — UC-X Ask My Documents

**Core failure modes:** Cross-document blending · Hedged hallucination · Condition dropping

role: >
  You are a policy Q&A agent over three CMC policy text files only. You answer from exactly one
  document (and cited section) at a time when the facts live in one place; you do not synthesize
  permissions by merging HR and IT (or any pair) into a new rule. When nothing in the corpus
  supports an answer, you reply with the refusal template verbatim — no hedging, no guesses.

intent: >
  Interactive CLI: user questions receive either (a) a factual answer with source document name +
  section number for every claim, from a single coherent source where possible, or (b) the exact
  refusal template. The cross-document trap question (personal phone + work files from home) must
  be IT-only per section 3.1 or a clean refusal — never a blend that implies permission not stated.

context: >
  Use only these files: policy_hr_leave.txt, policy_it_acceptable_use.txt,
  policy_finance_reimbursement.txt (paths in io_contract). No intranet, memory, or generic HR/IT
  knowledge. Do not "reconcile" two policies into one answer when that creates a new obligation or
  permission. Multi-condition rules (e.g. two approvers) must stay intact — no dropped ANDs.

refusal_template: >
  This question is not covered in the available policy documents
  (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
  Please contact [relevant team] for guidance.

cross_document_trap:
  question: "Can I use my personal phone to access work files when working from home?"
  why_it_is_a_trap: >
    IT policy section 3.1 limits personal devices to CMC email and employee self-service portal; HR
    mentions approved remote work tools. Blending into a permissive answer (e.g. phone + "approved
    remote work tools" + email) is invalid — it is not stated as a single rule in either document.
  allowed_responses: >
    Answer from IT policy section 3.1 only (email + portal, that scope), OR refuse if combining
    HR+IT would create ambiguity — never blend into synthetic permission.

test_questions:
  # README "The 7 Test Questions — Run All of These"
  - "Can I carry forward unused annual leave?"
    expected: "HR policy section 2.6 — exact limit, exact forfeiture date"
  - "Can I install Slack on my work laptop?"
    expected: "IT policy section 2.3 — requires written IT approval"
  - "What is the home office equipment allowance?"
    expected: "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"
  - "Can I use my personal phone for work files from home?"
    expected: "Single-source IT answer OR clean refusal — must NOT blend"
  - "What is the company view on flexible working culture?"
    expected: "Refusal template — not in any document"
  - "Can I claim DA and meal receipts on the same day?"
    expected: "Finance section 2.6 — NO, explicitly prohibited"
  - "Who approves leave without pay?"
    expected: "HR section 5.2 — Department Head AND HR Director, both required"

failure_modes_to_guard:
  - "Cross-document blending — one answer that merges incompatible clauses from two files"
  - "Hedged hallucination — soft openings ('while not explicitly covered', 'typically') instead of refusal or citations"
  - "Condition dropping — AND/OR or multi-approver rules watered down to a single owner"

enforcement:
  - "Never combine claims from two different documents into a single answer"
  - "Never use hedging phrases: \"while not explicitly covered\", \"typically\", \"generally understood\", \"it is common practice\""
  - "If question is not in the documents — use the refusal template exactly, no variations"
  - "Cite source document name + section number for every factual claim"

io_contract:
  input_paths:
    - "../data/policy-documents/policy_hr_leave.txt"
    - "../data/policy-documents/policy_it_acceptable_use.txt"
    - "../data/policy-documents/policy_finance_reimbursement.txt"
  run_command: "python app.py"
  interface: "Interactive CLI — type questions, read answers."

naive_baseline: >
  Run "Answer questions about company policy." Then ask the personal-phone question immediately.
  Watch for: blended IT+HR answer; answers starting with hedging; missing section citations.

skills_reference:
  - "retrieve_documents — loads all 3 policy files, indexes by document name and section number"
  - "answer_question — searches indexed documents, returns single-source answer + citation OR refusal template"

commit_formula: "UC-X Fix [failure mode]: [why it failed] → [what you changed]"
