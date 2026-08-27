# agents.md — UC-0B Summary That Changes Meaning (Rule-Based)

role: >
  A rule-based policy clause extractor. Its operational boundary is strictly limited to identifying and extracting core obligations from numbered policy sections using deterministic string processing. It does not use LLMs, machine learning models, or any form of "intelligent" summarization to ensure 100% fidelity to the source text.

intent: >
  For each source policy document, produce an extraction of core obligations for every numbered clause. A correct output identifies the clause number and the primary obligation sentence. It must never drop conditions or soften terms, favoring accuracy over brevity.

context: >
  The agent uses regex and string normalization to process the provided policy text. It has no external knowledge and operates regardless of the policy's subject matter. It is designed to be "condition-safe" by refusing to truncate sentences that contain logical connectors (and, both, requires).

enforcement:
  - "Every numbered clause (X.Y) from the source document must be extracted."
  - "Extraction must include the full sentence containing the core obligation to avoid condition-dropping."
  - "No paraphrasing is allowed — only cleaning of boilerplate precursors (e.g., removing 'This policy governs' or 'Employees must')."
  - "If a section contains multiple sentences, the first sentence containing an obligation-verb (must, required, permitted, forfeited) is selected."
