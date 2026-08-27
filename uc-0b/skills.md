# Policy Summary Skills

- `retrieve_policy(file_path: str) -> dict`: Reads the provided policy .txt file and returns a section-mapped dictionary for easier processing.
- `summarize_policy(policy_data: dict) -> str`: Produces a summary that precisely includes all 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with their core obligations and binding verbs. It ensures no multi-condition requirements are dropped and avoids any "scope bleed" or "standard practice" assumptions.
