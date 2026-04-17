# UC-X — District AI Magistrate Skills

## Skill 1: Semantic Multi-Policy Search
- **Input**: User query.
- **Logic**: Search across IT, HR, and Finance documents simultaneously.
- **Requirement**: Identify the specific section (e.g., "IT-POL-003 Section 4.1").

## Skill 2: Citation Injection
- **Logic**: For every sentence generated, verify it matches a retrieved segment.
- **Format**: Append [Source: DocName Section X.Y] to every factual claim.

## Skill 3: Conflict Arbitration
- **Logic**: If two policies overlap (e.g., HR says "Laptop for work" and IT says "Personal use allowed"), provide both with their specific context.

## Skill 4: The Magistrate's Refusal
- **Logic**: Check if the retrieval score is below a strict threshold (e.g., "I know this but it's not in the files").
- **Output**: Apply the exact refusal template from `agents.md`.
