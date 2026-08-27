# UC-0B Skills

## Skill: retrieve_policy

### Input
- file_path: Path to policy text file

### Output
Dictionary with:
- title: Policy document title
- sections: List of section objects with {number, heading, clauses}
- clause_inventory: List of all clause numbers for verification

### Logic
1. Read the text file
2. Parse document structure:
   - Extract title from header
   - Identify section boundaries (lines with ═══)
   - Extract section numbers and headings
   - Parse numbered clauses within each section
3. Build clause inventory (e.g., ["1.1", "1.2", "2.1", "2.2", ...])
4. Return structured data

### Example Output
```python
{
    "title": "EMPLOYEE LEAVE POLICY",
    "sections": [
        {
            "number": "2",
            "heading": "ANNUAL LEAVE",
            "clauses": [
                {"number": "2.1", "text": "Each permanent employee..."},
                {"number": "2.2", "text": "Annual leave accrues..."}
            ]
        }
    ],
    "clause_inventory": ["1.1", "1.2", "2.1", "2.2", "2.3", ...]
}
```

---

## Skill: summarize_policy

### Input
- policy_data: Structured policy from retrieve_policy
- output_file: Path for summary output

### Output
Text file with compliant summary

### Logic
1. Initialize summary with policy title and reference
2. For each section:
   - Write section heading
   - For each clause:
     - Summarize while preserving ALL conditions
     - Include clause reference (e.g., "Section 2.3:")
     - Check for multi-condition clauses and preserve all parts
     - Preserve binding verbs (must, requires, not permitted)
3. Verify completeness:
   - Check all clauses from inventory are mentioned
   - Scan for forbidden scope bleed phrases
   - Verify no information was added
4. Write summary to file

### Multi-Condition Detection
Special handling for clauses with:
- "and" connecting multiple requirements
- Multiple approvers/conditions
- Compound requirements

Examples:
- "Department Head AND HR Director" → preserve both
- "before or after a holiday" → preserve both conditions
- "within 48 hours of returning" → preserve timeframe

### Forbidden Phrases Check
Scan output for these and remove if found:
- "as is standard practice"
- "typically"
- "generally"
- "it is common practice"
- "while not explicitly"
- "employees are expected to"

### Example Summary Format
```
EMPLOYEE LEAVE POLICY SUMMARY
Document Reference: HR-POL-001

ANNUAL LEAVE
Section 2.1: Permanent employees receive 18 days paid annual leave per year.
Section 2.3: Leave applications must be submitted at least 14 calendar days in advance using Form HR-L1.
Section 2.4: Written approval from direct manager is required before leave commences. Verbal approval is not valid.
Section 2.5: Unapproved absence is recorded as Loss of Pay regardless of subsequent approval.
...
```
