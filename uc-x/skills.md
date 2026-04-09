# skills.md — UC-X Skill Definitions

## Scope
These skills power policy Q&A for UC-X using only:
- `policy_hr_leave.txt`
- `policy_it_acceptable_use.txt`
- `policy_finance_reimbursement.txt`

No skill may use external knowledge, unstated assumptions, or cross-document synthesis.

## Mandatory Refusal Template (Use Verbatim)
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.

---

## Skill: `retrieve_documents`

### Purpose
Load and retrieve exact policy sections relevant to a user question.

### Inputs
- `question` (string): User question in natural language.
- `documents` (fixed list):
  - `policy_hr_leave.txt`
  - `policy_it_acceptable_use.txt`
  - `policy_finance_reimbursement.txt`

### Processing Requirements
1. Parse each policy into section records with:
   - `document_name`
   - `section_number`
   - `section_text`
2. Match question intent to section-level content.
3. Return only direct candidates that explicitly address the question.
4. Preserve section wording fidelity; do not rewrite policy meaning.

### Hard Constraints
- Never infer rules not explicitly written.
- Never merge statements from different documents.
- Prefer exact section matches over broad keyword similarity.
- If no direct section exists, return an empty candidate set.

### Output Schema
Return an array `candidates` where each item is:
- `document_name` (string)
- `section_number` (string)
- `section_text` (string)
- `match_reason` (string, brief and factual)

If no direct match:
- `candidates: []`

---

## Skill: `answer_question`

### Purpose
Generate either a single-source, section-grounded answer with citation or the mandatory refusal template.

### Inputs
- `question` (string)
- `candidates` (array from `retrieve_documents`)

### Decision Logic (Strict)
1. If `candidates` is empty -> output refusal template exactly.
2. If answering requires combining multiple sections/documents -> output refusal template exactly.
3. If exactly one section directly answers -> answer from that section only.
4. Include all explicit constraints from that section (limits, exclusions, approvals, dates, amounts).
5. Append citation in exact format:
   - `[source: <document_name>, section <section_number>]`

### Hard Constraints
- Never combine claims across documents.
- Never hedge (`while not explicitly covered`, `typically`, `generally understood`, `it is common practice`).
- Never drop conditions from the cited section.
- Never output uncited factual claims.

### Output Contract
Non-refusal responses must use:

`<answer sentence(s) with no hedging and no added assumptions>. [source: <document_name>, section <section_number>]`

Refusal responses must be exactly:

This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.

---

## Validation Checklist (Per Response)
- Uses one source section only, or refusal template.
- Contains no hedging language.
- Includes all section conditions when answering.
- Includes citation with document + section.
- Uses refusal template verbatim when required.

---

## Critical Trap Requirement
Question: `Can I use my personal phone to access work files when working from home?`

Allowed:
- Single-source IT answer from section 3.1 only (email + employee self-service portal only), with citation.
- Refusal template, if single-source clarity is not available.

Disallowed:
- Any HR + IT blended answer.
