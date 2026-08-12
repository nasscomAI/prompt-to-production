# UC-0B Policy Summarizer — Skills Definition

## Skill 1: `retrieve_policy`

**Purpose**: Loads a policy text file and parses it into structured numbered sections.

**Input**: File path to a `.txt` policy document.

**Output**: An ordered dictionary where:
- Keys are clause IDs (e.g., `"2.3"`, `"5.2"`)
- Values are the full text of each clause, whitespace-normalized

**Behaviour**:
- Uses regex pattern `(\d+\.\d+)\s+` to split on clause numbers.
- Preserves multi-line clauses by joining continuation lines.
- Reports total clause count after parsing.

**Error handling**: Exits with error if file is not found or contains no parseable clauses.

---

## Skill 2: `summarize_policy`

**Purpose**: Takes the structured clause dictionary from `retrieve_policy` and produces a compliant summary with two sections:
1. A clause-by-clause summary preserving all conditions and binding verbs.
2. A Key Binding Obligations checklist highlighting the 10 critical clauses.

**Input**: Ordered dictionary of clause ID → clause text.

**Output**: A formatted text string written to the output file.

**Compliance rules applied**:
- Every clause ID from the input must appear in the output.
- Multi-condition clauses (e.g., 5.2 with dual approvers) must list ALL conditions.
- Binding verbs (`must`, `will`, `requires`, `not permitted`) are preserved or uppercased for emphasis.
- No external phrases are added (zero scope bleed).
- If a clause would lose meaning when shortened, the core obligation is quoted verbatim.

**Error handling**: Logs a warning if any clause from the input dictionary is missing from the output.
