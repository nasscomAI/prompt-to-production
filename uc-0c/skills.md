skills:
  - name: load_dataset
    description: "reads CSV, validates columns, reports null count and which rows before returning"
    input: "file path to the budget dataset (.csv)"
    output: "structured array of budget data and a pre-validation report containing a list of null rows and their notes"
    error_handling: "If the requested dataset is empty or corrupted, halt execution immediately with an error."

  - name: compute_growth
    description: "takes ward + category + growth_type, returns per-period table with formula shown"
    input: "filtered budget dataset, target ward, target category, and strict growth computation type"
    output: "A calculated data table string detailing the spend, computed growth, and the formula used for each period."
    error_handling: "If the requested growth type is not provided, output a refusal and do not guess. If an aggregation metric for multiple wards or categories is passed without explicit approval, throw a refusal. If an actual_spend value is missing, flag the row accurately using the notes from load_dataset instead of dropping it silently."
