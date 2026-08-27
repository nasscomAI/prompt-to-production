# UC-0B Policy Skills

## retrieve_policy
**Input**: File path to a `.txt` policy document.
**Process**:
1. Read the file content.
2. Segment the text based on numbering (e.g., 2.3, 5.2).
3. Return a list of dictionaries: `{"id": "2.3", "text": "..."}`.

## summarize_policy
**Input**: Structured list of policy clauses.
**Process**:
1. Iterate through each clause.
2. For each clause, extract the core obligation and all associated conditions.
3. Verify that binding verbs (must/will) are preserved.
4. Output a summary entry for every clause in the format: "[Clause ID]: [Concise Obligation including ALL conditions]".
5. Perform a cross-check against the original text to ensure no conditions were "dropped".
