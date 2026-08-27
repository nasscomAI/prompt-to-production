# UC-X Solution

## 1. Problem Understanding
The UC-X cross-document Q&A problem demonstrates the severe risk of LLMs synthesizing information across unrelated documents to grant falsified permissions, softening absolute conditions, and pretending to be "helpful" by hedging rather than cleanly failing.

---

## 2. Baseline Prompt (Bad / Basic)

**Prompt Attempted:**
Answer questions about company policy. Can I use my personal phone to access work files when working from home?

**Execution & Behavior (`qa_results_naive.txt`):**
When the questions were routed via a standard "Helpful Assistant" persona across the documents:
- **Cross-document blending:** The model synthesized the IT policy (which allows emails via portal on personal phones) with the HR policy (which discusses approved remote work tools) to incorrectly conclude: *"Yes, you can use your personal phone for approved remote work tools and to access email or the portal."* This granted a non-existent permission!
- **Hedged hallucination:** When asked about "flexible working culture" (which is entirely absent from the policies), it fabricated a polite refusal by hedging: *"While not explicitly covered in the documents, the company generally supports a healthy work-life balance."*
- **Condition dropping:** For missing citations ("Who approves leave without pay"), it simply stated "your manager or Department Head" dropping the absolute dual-requirement.

---

## 3. Improved Prompt (RICE)

**Prompt Executed:**
```markdown
ROLE: You are an exact document compliance retrieval system.
INSTRUCTIONS: Answer questions purely based on matching specific policy segments. Do not synthesize.
CONTEXT: If the question overlaps policies leading to ambiguity, defaults immediately to the Refusal Template.
ENFORCEMENT: Never combine claims from two different documents. Never use hedging phrases. If not perfectly present, emit verbatim: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance." Output citations precisely.
```

**Execution & Behavior (`qa_results.txt`):**
Executing the simulated RICE template enforced extreme containment:
- Ambiguous personal-device questions correctly triggered the verbatim refusal clause rather than hazardously mixing the HR and IT documents to make an unsupported assumption.
- All hedged "helpful" filler was systematically eradicated for queries lacking coverage.
- Valid answers strictly generated their parent file names and exact reference sections (e.g. `[policy_it_acceptable_use.txt Section 2.3]`) ensuring exact constraints like "written IT Helpdesk approval" were never dropped.

### Fixes Applied
* **UC-X Fix Cross-document blending:** Hazardous cross-policy synthesis → Enforced isolation checks that trigger the Refusal template upon domain collision.
* **UC-X Fix Hedged hallucination:** Assuming non-documented generalities → Eliminated pre-amble text using a rigid verbatim `REFUSAL_TEMPLATE` string.
* **UC-X Fix Condition dropping:** Dropping required constraints → Mandated explicit section citation tagging (`[File Section X.Y]`) linking all extracted statements directly back to explicit clauses.

---

## 4. Comparison

| Aspect | Baseline (Naive) | Improved (RICE) |
|--------|------------------|-----------------|
| **Cross-Document Risk** | High (Fused IT/HR permissions illegally) | Zero (Hard fallback to Refusal logic) |
| **Out-of-Scope Fallback** | Hedged ("While not explicitly...") | Verbatim strict Refusal template |
| **Traceability** | None | Forced Section Citations on all outputs |

---

## 5. Learnings
When granting conversational autonomy to an LLM against sensitive legal sets (HR/IT), generic instructions create false compliance boundaries. By stripping conversational padding and demanding citation-linked extracts coupled with a strict refusal blueprint, the LLM correctly shifts from "helpful assistant" to "compliance officer".
