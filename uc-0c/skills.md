skills:
  - name: load_dataset
    description: Parses the incoming CSV file and triggers a mandatory nullity assessment prior to computation.
    input: Filepath string pointing to the dataset.
    output: Row data alongside a console report exposing exactly how many nulls were found, where, and why.
    error_handling: Rather than converting blank cells to zero or skipping them silently, it intercepts blank `actual_spend` cells and logs their nullity.

  - name: compute_growth
    description: Operates strictly scoped calculations derived chronologically for a constrained ward/category subset.
    input: Row data, explicit ward filter, explicit category filter, and a defined growth type.
    output: A per-period CSV table capturing current state, computed metrics, and explicitly documented formulas inline.
    error_handling: Refuses to execute if scope boundaries (ward/category) or formulation methods (growth-type) are absent. Bypasses null computational crashes by marking the output as flagged.
