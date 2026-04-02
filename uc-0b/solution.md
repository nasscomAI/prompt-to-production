# UC-0B Solution

## 1. Problem Understanding
The goal is to summarize an HR Leave policy strictly maintaining explicit conditions (e.g., dual approvers, hard limits date references) without bleeding in assumed institutional generalities ("as is standard").

---

## 2. Baseline Prompt (Bad / Basic)

**Prompt Attempted:**
Summarize this policy document.

**Execution & Behavior (`summary_hr_leave_naive.txt`):**
When running using the naive mode representation across `app.py`, the output dropped severely important conditions:
- **Scope Bleed:** Added phrases like "typical for government organizations" and "as is standard practice" which aren't in the input text.
- **Obligation Softening:** Changed "must submit at least 14 days" to "You need to apply in advance".
- **Clause Omission:** Completely omitted the "HR Director" requirement for LWP (Clause 5.2), framing it falsely as "requires approval from your manager".

---

## 3. Improved Prompt (RICE)

**Prompt Executed:**
```markdown
ROLE: You are an objective policy summariser.
INSTRUCTIONS: Extract every numbered clause. Preserve ALL conditions exactly.
ENFORCEMENT: Never add information not present. Do not drop multi-condition obligations (e.g. BOTH managers). If un-summarizable, quote verbatim.
```

**Execution & Behavior (`summary_hr_leave.txt`):**
The strictly programmed RICE execution yielded highly compliant enforcement:
- Extracting exact elements verbatim without interpretation.
- Precisely matching multi-level dependencies (Department Head AND HR Director approval for LWP).
- Omitted all externally assumed scope bleed.

### Fixes Applied
* **UC-0B Fix Clause omission:** Skipped constraints inside compound sentences → Enforced strict numerical extraction mappings.
* **UC-0B Fix Scope bleed:** Conversational or associative hallucination → Stripped out unrequested context generation.
* **UC-0B Fix Obligation softening:** Weakened legal bounding ("must" to "needs") → Forced verbatim obligation verbs.

---

## 4. Comparison

| Aspect | Baseline (Naive) | Improved (RICE) |
|--------|------------------|-----------------|
| **Completeness** | Flawed (missed dual approvers) | High (captured all 10 bounds) |
| **Accuracy** | Medium (softened legal obligations) | Exact (strict parsing) |
| **Hallucination** | High (assumed standard government practices) | Zero |

---

## 5. Learnings
Using a structured execution loop eliminates conversational AI scope bleed, demanding rigorous preservation of critical legal parameters.
