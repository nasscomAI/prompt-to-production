# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy text files, parses each into its numbered section IDs (e.g. "2.6"), and returns an index of document filename -> set of section IDs so every answer citation can be verified against the actual documents.
    input: list of paths (str) — the three files ../data/policy-documents/policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt. Passed as one argument: doc_paths (list[str]).
    output: A dict mapping each filename (str) to a list of parsed section IDs (e.g. {"policy_hr_leave.txt": ["1.1", "1.2", ..., "8.2"]}); also returns the raw clause texts keyed by section for quoting.
    error_handling: Raises FileNotFoundError if any file is missing and a ValueError if a file contains no numbered sections; it never builds an unverifiable index.

  - name: answer_question
    description: Matches a user question against the single-source knowledge index, returns the matched intent's answer with its document + section citation, or returns the verbatim refusal template when the question is not covered or the match is ambiguous.
    input: question (str) — the free-text user question; index (dict from retrieve_documents); intents (list of curated single-source answers with trigger phrases). Required.
    output: Either (a) a single-source answer string citing document + section(s) for every claim, or (b) the exact refusal template constant.
    error_handling: Normalizes and scores the question against intent triggers; a zero-score or a tie between two different intents yields the refusal template (never a guess). Runs fail-loud validation that every cited section exists in the index and that no hedge phrase appears in the emitted answer; violations raise an error instead of being served.