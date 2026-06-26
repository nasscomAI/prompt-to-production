# UC-X Skills Definition

## Skill: `retrieve_documents`
**Purpose:** Load all 3 policy files and index by document name and section number.

**Input:** Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt

**Output:** Dictionary indexed by document name and section

**Rules:**
- Load all 3 files completely — never skip one
- Preserve section numbers exactly as in source
- Never merge content across documents

---

## Skill: `answer_question`
**Purpose:** Search indexed documents and return single-source answer with citation OR refusal.

**Input:** User question + indexed documents

**Output:** Answer with citation (Document name + section) OR refusal template

**Rules:**
- Search all 3 documents independently
- If answer found in ONE document — return answer + citation
- If answer requires combining 2+ documents — use refusal template
- If answer not found in any document — use refusal template exactly
- Never use hedging language
