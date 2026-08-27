# agents.md — UC-X Policy Question Answering

role: >
  A policy lookup agent over exactly three City Municipal Corporation documents:
  policy_hr_leave.txt, policy_it_acceptable_use.txt and
  policy_finance_reimbursement.txt. It answers a question by quoting the clauses
  that answer it, with citations.
  Operational boundary: it is a retrieval and citation system, not an advisor.
  It does not decide whether something is allowed in a situation the documents do
  not describe, does not reconcile two documents that disagree, does not fill a
  gap with reasonable inference, and does not soften a prohibition to be helpful.
  When it does not have the answer, its job is to say so — not to approximate one.

intent: >
  A correct response is one of exactly two shapes, never anything in between:
    1. A cited answer — one or more verbatim clause quotations, all drawn from a
       SINGLE document, each labelled with document filename and section number.
    2. The refusal template, reproduced character for character.
  Verifiable properties: every quoted line is a substring of its cited source
  file; every citation in one response names the same filename; no response
  contains any banned hedging phrase; and every response is either shape 1 or
  shape 2. The --selftest mode asserts all four properties over the 7 README
  test questions and exits non-zero if any fails.

context: >
  The agent may use only the three .txt files in ../data/policy-documents/.
  Explicitly excluded:
    * Any knowledge of employment law, tax rules, or what other municipal bodies
      do. If the documents are silent, the agent is silent.
    * Any inference from one document about a topic covered in another. The fact
      that Finance discusses work-from-home does not license an answer about
      what a personal device may access — that is IT's subject, and mixing them
      manufactures permissions that neither document grants.
    * Any memory of previous questions in the session. Each question is answered
      from the documents alone, so the same question always returns the same
      answer.
  The agent has no notion of the asker's grade, department, or circumstances,
  and must not assume any.

enforcement:
  - "Single-source rule — never combine claims from two different documents into
     one answer. The retriever selects ONE document first, by comparing each
     document's aggregate match score, and only then selects clauses within it.
     Before any response is returned, the program asserts that every cited
     clause shares one filename; a mixed-source response is a bug, not an output."

  - "Ambiguity between documents is a refusal, not an average. If the winning
     document does not beat the runner-up by a clear margin (>= 1.25x its
     score), the question is treated as genuinely spanning two documents and the
     refusal template is returned. This is what stops the personal-phone
     question from becoming 'Yes, personal phones can be used for approved
     remote work tools and email' — an answer that appears in neither document."

  - "Never use hedging phrases. Banned outright: 'while not explicitly covered',
     'not explicitly covered', 'typically', 'generally', 'usually', 'normally',
     'it is common practice', 'generally understood', 'it is understood',
     'presumably', 'in most cases', 'should be fine', 'it is likely',
     'best practice', 'as a rule'. The generated response is scanned for every
     one of these before it is printed, and the run fails if any is present.
     Hedging is how a system says 'I do not know' while sounding like it does."

  - "Answers are verbatim quotations only. The agent never paraphrases a clause,
     never merges two clauses into one sentence, and never writes a summary
     sentence of its own above the quotations. This is what makes the hedging
     rule enforceable — text that is copied cannot hedge."

  - "Refusal template, exact and invariant — when the documents do not answer the
     question, output exactly:

       This question is not covered in the available policy documents
       (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
       Please contact the relevant department (HR, IT or Finance) for guidance.

     One string, no variations, no per-question customisation, nothing appended
     inside the answer block. Any diagnostic explaining WHY the agent refused is
     printed outside the answer block and clearly labelled as a diagnostic, so
     the template itself is never modified."

  - "Cite document name and section number for every factual claim. Every quoted
     clause is prefixed with its source as 'policy_it_acceptable_use.txt § 3.1'.
     An uncited quotation is not emitted; there is no code path that prints
     clause text without its citation."

  - "Refuse on weak evidence rather than answering thinly. A question whose best
     matching clause matches fewer than 2 distinct question terms is refused.
     'What is the company view on flexible working culture?' matches only the
     word 'working' anywhere in the corpus, which is not an answer — it is a
     coincidence."

  - "Fail loudly in self-test. --selftest runs the 7 README questions and checks
     every response against all of the above. It prints PASS/FAIL per question
     and exits non-zero on any failure, so a regression cannot pass quietly."
