# skills.md — UC-0B Policy Summarizer Skills

## Skill: retrieve_policy

### Description
Reads a policy document from the filesystem and returns its full text content.

### Trigger
User provides a file path to a policy document (e.g., `--input path/to/policy.txt`).

### Inputs
| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| file_path | string | yes      | Path to the policy text file         |

### Steps
1. Validate that the file exists at the given path.
2. Read the entire file content as UTF-8 text.
3. Return the raw text content for downstream processing.

### Outputs
| Field      | Type   | Description                              |
|------------|--------|------------------------------------------|
| text       | string | Full text content of the policy document |
| file_name  | string | Name of the source file (for reference)  |

### Error Handling
- If file does not exist: raise FileNotFoundError with clear message.
- If file is not readable: raise PermissionError with clear message.

---

## Skill: summarize_policy

### Description
Parses a policy document into numbered clauses and produces a faithful
one-line summary for each clause, preserving all binding obligations,
conditions, and consequences.

### Trigger
Called after `retrieve_policy` returns the document text.

### Inputs
| Parameter     | Type   | Required | Description                                  |
|---------------|--------|----------|----------------------------------------------|
| policy_text   | string | yes      | Full text of the policy document             |
| source_ref    | string | yes      | Document reference for the summary header    |

### Steps
1. Parse the document to identify all section headers (pattern: single digit followed by period and title).
2. Parse numbered clauses within each section (pattern: X.Y where X is section number).
3. For each clause:
   a. Extract the full clause text.
   b. Identify the binding verb (must, shall, requires, entitled, cannot, etc.).
   c. Identify ALL conditions (time limits, approvals, thresholds).
   d. Identify ALL consequences (forfeiture, LOP, non-counting, etc.).
   e. Produce a one-line summary preserving binding verb + all conditions + all consequences.
   f. If the clause has multi-condition obligations (AND/OR joins), ensure ALL conditions appear.
   g. If faithful one-line summary is impossible, quote verbatim and flag [VERBATIM].
4. Assemble output with header and section-by-section summaries.

### Outputs
| Field         | Type   | Description                                         |
|---------------|--------|-----------------------------------------------------|
| summary_text  | string | Complete summary with header and all clause summaries |

### Enforcement Checks
- Count of output clauses must equal count of input clauses.
- Critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must contain their key obligations:
  - 2.3: "14" AND "days" AND "advance"
  - 2.4: "written" AND "approval" AND "verbal not valid"
  - 2.5: "unapproved" AND "LOP" AND "regardless"
  - 2.6: "5 days" AND "carry-forward" AND "forfeited" AND "31 Dec"
  - 2.7: "January–March" AND "forfeited"
  - 3.2: "3" AND "consecutive" AND "medical cert" AND "48 hours"
  - 3.4: "before or after" AND "holiday" AND "certificate" AND "regardless of duration"
  - 5.2: "Department Head" AND "HR Director"
  - 5.3: "30 days" AND "Municipal Commissioner"
  - 7.2: "not permitted" AND "under any circumstances"
