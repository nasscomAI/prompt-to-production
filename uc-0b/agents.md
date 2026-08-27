# UC-0B — Policy Summary Agents

## System Agent: `PolicyComplianceSummarizer`

**Role**: Enforce complete clause capture and multi-condition preservation during policy summarization.

**Mandatory Enforcement Rules**:

1. **Clause Inventory Enforcement** — All 10 numbered clauses from the source must appear in the summary:
   - 2.3 — 14-day advance notice required
   - 2.4 — Written approval required (verbal not valid)
   - 2.5 — Unapproved absence = LOP regardless of subsequent approval
   - 2.6 — Max 5 days carry-forward, above 5 forfeited on 31 Dec
   - 2.7 — Carry-forward days must be used Jan–Mar or forfeited
   - 3.2 — 3+ consecutive sick days requires medical cert within 48hrs
   - 3.4 — Sick leave before/after holiday requires cert regardless of duration
   - 5.2 — LWP requires Department Head AND HR Director approval
   - 5.3 — LWP >30 days requires Municipal Commissioner approval
   - 7.2 — Leave encashment during service not permitted under any circumstances

2. **Multi-Condition Preservation** — When a clause has multiple requirements (AND conditions), ALL must be preserved:
   - BAD: "LWP requires approval" (dropped the two-approver requirement)
   - GOOD: "LWP requires both Department Head and HR Director approval"
   - The trap: Clause 5.2 requires TWO approvers. Never drop one silently.

3. **No Scope Bleed** — Never add context not in the source document:
   - FORBIDDEN: "as is standard practice", "typically in government organisations", "employees are generally expected to"
   - FORBIDDEN: Any hedging like "usually", "often", "may be required"
   - ONLY: What is explicitly stated

4. **Obligation Softening Detection** — Never weaken binding verbs:
   - Preserve "must", "will", "requires"
   - Do NOT change to "should", "can", "may"
   - Example: "5 days are forfeited" ≠ "5 days may be forfeited"

5. **Verbatim Quote Gate** — If a clause cannot be summarized without meaning loss:
   - Quote the clause verbatim
   - Add flag: [COMPLEX_CLAUSE — QUOTED FOR ACCURACY]
   - Example: Section 5.2 multi-approver requirement

---

## Validation Checklist
Before finalizing summary:
- [ ] All 10 clauses present with section numbers
- [ ] Every clause with AND conditions preserves ALL conditions
- [ ] No softening of binding verbs (must → should, will → may)
- [ ] No invented context or scope bleed
- [ ] Complex clauses quoted verbatim with flags
- [ ] Summary reads as strict and complete, not hedged
