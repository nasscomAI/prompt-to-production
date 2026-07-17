# UC-X Skills

## retrieve_documents

**Input:** Path to data directory containing 3 policy .txt files

**Output:** List of indexed clauses, each with: file, heading, clause number, text

**Logic:**
1. Load each policy file: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
2. Parse section headings (numbered, uppercase).
3. Parse individual clauses (e.g., 2.3, 5.2) with full text including continuation lines.
4. Return structured index for searching.

---

## answer_question

**Input:** question (str), documents (list of indexed clauses)

**Output:** Single-source answer with citation OR refusal template

**Logic:**
1. Normalize question to lowercase for matching.
2. Match against known question patterns for precise routing.
3. For known patterns, return answer from the SPECIFIC document + section only.
4. For unknown patterns, do keyword search across all clauses.
5. If best match score >= 2 keyword hits, return that single clause with citation.
6. If no adequate match, return refusal template.

**Enforcement:**
- NEVER blend answers from multiple documents.
- NEVER use hedging phrases.
- Always cite document filename + section number.
- Use refusal template exactly when question is not covered.
- For the personal phone trap question: answer ONLY from IT policy section 3.1.
