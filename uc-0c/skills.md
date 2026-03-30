skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates necessary columns, and explicitly identifies all null rows before returning the parsed data.
    input:
      type: string
      format: A file path pointing to the primary budget CSV dataset.
    output:
      type: list
      format: A structured list of validated row records alongside an explicitly bundled report detailing the count and location of null entries.
    error_handling: To strictly prevent silent null handling, it preemptively flags every null actual_spend row and exposes its reason from the notes column before any operations begin.

  - name: compute_growth
    description: Filters the pre-validated dataset directly by an isolated ward and category to calculate growth metrics natively paired with mathematical formulas.
    input:
      type: dict
      format: Parameters comprising the structured dataset array, the target ward, the target category, and an explicit 'growth_type'.
    output:
      type: list
      format: A formatted per-period table where each row perfectly aligns the numerical outcome with the explicit formula used.
    error_handling: To prevent the wrong aggregation level, it categorically refuses to execute if tasked with aggregating across multiple wards or categories; to prevent formula assumption, it halts and asks for clarification if 'growth_type' is omitted rather than guessing.
