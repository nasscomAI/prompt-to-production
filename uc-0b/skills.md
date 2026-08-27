# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy document from a text file and transforms it into a structured format indexed by clause numbers.
    input: File path to a policy .txt file.
    output: A collection of structured sections, each identified by its clause number (e.g., 2.3, 5.2).
    error_handling: If the file is inaccessible or fails to parse, the system must report a 'FILE_NOT_FOUND' or 'PARSE_ERROR' and terminate.

  - name: summarize_policy
    description: Generates a high-fidelity summary of structured policy sections while ensuring no conditions are omitted or softened.
    input: A structured collection of policy clauses and their contents.
    output: A summary document where every point corresponds to a source clause number and preserves all original obligations.
    error_handling: If a clause contains complex multi-part obligations that cannot be safely summarized, the skill must output the verbatim text and mark it with a 'CRITICAL_CLAUSE' flag.
