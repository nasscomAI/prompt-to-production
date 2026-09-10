# Vibe Coding Workshop — Submission PR

**Name:** Karvy Kapoor

**City / Group:** Ghaziabad

**Date:** 11 September 2026

**AI tool(s) used:** ChatGPT, Groq API with `openai/gpt-oss-20b`

---

## Submission Scope

This submission covers **UC-0B — Summary That Changes Meaning** only.

UC-0A, UC-0C, and UC-X are intentionally not included.

---

## Checklist

- [x] `agents.md` committed for UC-0B
- [x] `skills.md` committed for UC-0B
- [x] `app.py` for UC-0B runs without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] All 29 numbered policy clauses are present in the final summary
- [x] Meaningful UC-0B commit created

The following items are not applicable because this submission covers UC-0B only:

- UC-0A classifier and results CSV
- UC-0C growth output
- UC-X document question answering
- Four-use-case completion

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**

> Clause omission.

**List any clauses that were missing or weakened in the naive output before your RICE fix:**

> The naive output stopped at clause 5.2 and omitted clauses 5.3 through 8.2. The initial output was therefore incomplete. Additional enforcement was also needed to preserve all conditions in multi-condition clauses, especially clause 5.2, which requires approval from both the Department Head and the HR Director.

**After your fix — are all 10 critical clauses present in `summary_hr_leave.txt`?**

> Yes. All 10 critical clauses are present. The final summary also contains all 29 numbered clauses from the source policy.

**Did the naive prompt add any information not in the source document?**

> No unsupported information was retained in the final summary. The enforcement rules restricted the system to the supplied policy document and prohibited invented information, external assumptions, and unsupported practices.

**Your git commit message for UC-0B:**

> `[UC-0B] Fix clause omission: incomplete summaries → enforced all 29 policy clauses`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest, and why?**

> The hardest step was enforcement because the initial prompt produced a summary that stopped before the end of the policy. I made the requirements explicit by listing every expected clause and requiring preservation of conditions, approvals, deadlines, exceptions, and prohibitions.

**What is the single most important thing you added manually to `agents.md`?**

> `"Every numbered clause in the source policy must appear in the summary with its clause number."`

**Name one real task where you will apply RICE + CRAFT within the next two weeks:**

> I will apply RICE + CRAFT to my AI career intelligence platform when generating summaries or recommendations from job descriptions. I will identify failure modes and add explicit enforcement rules before relying on the generated output.

---

## Reviewer Notes

*Reviewer fills this section.*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | | |
| agents.md quality | | |
| skills.md quality | | |
| CRAFT loop evidence | | |
| Test coverage | | |
| **Total** | **/20** | |

**Badge decision:**

- [ ] Standard badge
- [ ] Distinction badge
- [ ] Not yet