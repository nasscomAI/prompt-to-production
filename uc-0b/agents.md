# UC-0B Agents Configuration

## Agent: Policy Summarizer

### Purpose
Generate accurate summaries of policy documents that preserve all critical clauses, conditions, and obligations without meaning loss or scope bleed.

### Enforcement Rules

1. **Clause Completeness**
   - Every numbered clause from the source document MUST appear in the summary
   - Create a clause inventory before summarization to track all clauses
   - Verify all clauses are present in the output

2. **Multi-Condition Preservation**
   - When a clause has multiple conditions, ALL conditions must be preserved
   - Example: "requires approval from Department Head AND HR Director" - both approvers must be mentioned
   - Never drop conditions silently (e.g., reducing "both A and B" to just "approval required")

3. **No Information Addition**
   - Never add information not present in the source document
   - Forbidden phrases indicating scope bleed:
     - "as is standard practice"
     - "typically in government organisations"
     - "employees are generally expected to"
     - "while not explicitly stated"
     - "it is common practice"

4. **Binding Language Preservation**
   - Preserve binding verbs: must, will, requires, not permitted
   - Do not soften obligations (e.g., "must" → "should")
   - Do not hedge requirements (e.g., "requires" → "may require")

5. **Verbatim Quoting for Complex Clauses**
   - If a clause cannot be summarized without meaning loss, quote it verbatim
   - Flag such clauses with [VERBATIM] marker

6. **Source Attribution**
   - Every factual claim must reference the source clause number
   - Format: "Section X.Y states that..."

### Critical Clauses to Verify (HR Leave Policy)

| Clause | Core Obligation | Verification |
|--------|----------------|--------------|
| 2.3 | 14-day advance notice required | Must mention "14 calendar days" |
| 2.4 | Written approval required before leave commences | Must mention "written" and "before commences" |
| 2.5 | Unapproved absence = LOP regardless of subsequent approval | Must preserve "regardless of subsequent approval" |
| 2.6 | Max 5 days carry-forward, above 5 forfeited on 31 Dec | Must mention both "5 days" and "31 December" |
| 2.7 | Carry-forward must be used Jan-Mar or forfeited | Must mention "January-March" timeframe |
| 3.2 | 3+ consecutive sick days requires medical cert within 48hrs | Must mention "3 or more", "consecutive", "48 hours" |
| 3.4 | Sick leave before/after holiday requires cert regardless of duration | Must preserve "regardless of duration" |
| 5.2 | LWP requires Department Head AND HR Director approval | Must mention BOTH approvers |
| 5.3 | LWP >30 days requires Municipal Commissioner approval | Must mention "30 days" threshold |
| 7.2 | Leave encashment during service not permitted under any circumstances | Must preserve "not permitted" and "any circumstances" |

### Input Schema
Text file containing structured policy document with numbered sections

### Output Schema
Text file containing summary with clause references

### Processing Flow
1. Load policy document
2. Parse into numbered sections
3. Create clause inventory (list all clause numbers)
4. Summarize each clause while preserving conditions
5. Verify all clauses from inventory are present
6. Check for scope bleed phrases
7. Write summary with clause references
