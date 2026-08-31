# Skills

## retrieve_policy

**Purpose**: Load the policy text file and return content as structured numbered sections.

**Input**: Path to policy text file (e.g., `../data/policy-documents/policy_hr_leave.txt`)

**Output**: JSON object with:
- `sections`: Array of objects, each containing:
  - `clause_number`: String (e.g., "2.3", "5.2")
  - `text`: Full text of the clause
- `raw_text`: Complete original document text

**Behavior**:
- Parse the input file line by line
- Identify numbered clauses matching pattern `X.Y` where X and Y are digits
- Preserve exact wording — no normalization, no interpretation
- Return all clauses found, including any beyond the 10 known clauses

---

## summarize_policy

**Purpose**: Take structured policy sections and produce a compliant summary preserving all enforcement rules.

**Input**: JSON object from `retrieve_policy` output (sections array with clause_number and text)

**Output**: Plain text summary file content

**Behavior**:
1. For each clause in input sections, produce a summary entry that:
   - References the exact clause number
   - Preserves the binding verb (must, requires, will, may, not permitted, are forfeited)
   - Retains ALL conditions — no condition dropping
   - Uses only information from the source clause text

2. Special handling:
   - If a clause cannot be summarized without meaning loss → quote verbatim and flag with `[VERBATIM]`
   - Clause 5.2: Must explicitly state "Department Head AND HR Director" — both required
   - No scope bleed: never add "standard practice", "typically", "generally expected", or any external context

3. Output format: One paragraph per clause, prefixed with clause number (e.g., "2.3: ...")

**Enforcement compliance**:
- All 10 known clauses must appear in output
- Multi-condition clauses (especially 5.2) must preserve every condition
- Zero additions beyond source document
- Verbatim quotes flagged when necessary