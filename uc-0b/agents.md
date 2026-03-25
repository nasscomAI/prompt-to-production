# Policy Summary Agents

- `PolicySummaryAgent`: A high-precision extraction agent that summarizes policy documents. It is programmed to identify and preserve all numbered clauses, especially those with multiple binding conditions. It avoids "scope bleed" by strictly adhering to the source text.
- `ComplianceAuditor`: (Internal) Ensures that all 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present in the final output with their original binding verbs.
