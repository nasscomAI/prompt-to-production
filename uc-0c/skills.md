# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the raw budget CSV accurately, strictly validating structural schemas whilst actively locating and mapping deliberately null analytical factors natively.
    input: String path pointing to the standard dataset CSV document (e.g., ../data/budget/ward_budget.csv).
    output: Yields parsed numerical table structures paired directly with a rigorous pre-calculation explicit report of exact null counts mapped to their original row IDs accurately.
    error_handling: Halts cleanly and actively warns users if foundational columns are missing preventing hidden downstream aggregator crashing. 

  - name: compute_growth
    description: Calculates localized scope progression based on exactly matched filters natively embedding tracking mathematics whilst rejecting broader aggregation traps effortlessly.
    input: Filtered CSV list payload alongside specific strict string constraints: `ward`, `category`, and explicitly `growth_type`.
    output: Produces a precise per-period numerical tabular evaluation featuring the newly computed values appended adjacent to the explicit mathematical `formula_string` representation natively.
    error_handling: If targeted periods contain `null` evaluation blocks, rejects evaluating blindly and replaces output with explicit reasons directly extracted from data `notes`; actively triggers a hard STOP refusal if asked to collapse data outside its strict boundaries or without `growth_type` defined.
