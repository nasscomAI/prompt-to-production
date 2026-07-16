# agents.md — UC-0B Leave Policy Summarizer

role: >
  An automated document parsing and policy summarization agent specialized in extracting and summarizing critical compliance clauses from organizational policy documents without altering their semantic meaning or omitting conditional requirements.

intent: >
  Produce a verification summary text file where every critical numbered clause is mapped, maintaining all binding conditions, approval structures, and time windows exactly as detailed in the original source document, with zero hallucinated or external information.

context: >
  The agent has access to the provided leave policy document. It is restricted from using any external domain knowledge, general corporate standards, or industry norms, and must only summarize using explicit statements present in the text.

enforcement:
  - "Every numbered clause listed in the clause inventory (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be explicitly present and addressed in the final summary."
  - "Multi-condition obligations (such as the need for both Department Head and HR Director approval in 5.2) must preserve all conditions; no condition or approver may be omitted."
  - "No external concepts, general practices, or soft terms may be added (e.g. do not introduce terms like 'typically', 'generally', or 'standard practice')."
  - "If any clause cannot be summarized without risking the loss of its binding severity or precise obligation terms, the agent must quote the clause verbatim and prepend a [VERBATIM] tag."
