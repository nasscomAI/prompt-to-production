# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections and clauses.
    input: input_path to a policy .txt file (string).
    output: ordered list of sections, each with a section number/title and its ordered list of clauses (clause_id like "2.3" and clause_text), preserving source order.
    error_handling: Raises a clear error if the file is missing or empty; a line that is not a recognised clause or header is retained as continuation text of the current clause so no wording is lost.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliance-preserving summary with clause references, per the enforcement rules in agents.md.
    input: the structured sections returned by retrieve_policy.
    output: text summary where every source clause appears under its clause reference, binding verbs and all conditions preserved, no added content.
    error_handling: If a clause contains a binding obligation that cannot be compressed without meaning loss (multi-condition, "under any circumstances", or "not valid"), it is emitted verbatim and marked [VERBATIM] rather than paraphrased. A coverage check confirms every source clause id is present before writing.
