skills:
  - name: load_dataset
    description: Reads the input CSV budget dataset, checks columns, and identifies rows with null actual spend values.
    input: input_path (str) to the source budget CSV.
    output: list of dictionaries representing the rows of the CSV, with parsed floats and notes.
    error_handling: Logs details of null spend rows. Raises FileNotFoundError if path is incorrect.

  - name: compute_growth
    description: Filters data by ward and category, calculates growth rates (MoM), and lists formulas used.
    input:
      data: list of row dicts.
      ward: str naming the target ward.
      category: str naming the target category.
      growth_type: str naming growth method (e.g. "MoM").
    output: list of dictionaries representing the per-period growth table.
    error_handling: Refuses computation and raises ValueError if ward or category is "Any", unspecified, or growth_type is missing. Handles null current/previous periods by flagging them.
