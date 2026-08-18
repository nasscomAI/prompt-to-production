skills:
  - name: load_dataset
    description: Reads the input budget CSV, validates columns, counts null actual spend rows, and reports them before returning.
    input: file_path (string) - Path to the budget CSV file.
    output: list of dicts - The rows of the dataset.
    error_handling: Raise FileNotFoundError if the file does not exist. Raise ValueError if required columns ('period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes') are missing.

  - name: compute_growth
    description: Filters data for the specified ward and category, identifies any null spend rows, and computes the growth rates (MoM or YoY) for each period, showing the formula used.
    input:
      dataset (list of dicts) - The full dataset.
      ward (string) - The ward name to filter by.
      category (string) - The category to filter by.
      growth_type (string) - MoM or YoY.
    output: list of dicts - Each dict representing an output row with period, actual spend, growth, and formula.
    error_handling: Refuse and raise ValueError if ward or category is empty, "any", "all", or "Any". Refuse if growth_type is empty or not in ['MoM', 'YoY']. If YoY is chosen but no matching month exists for the previous year, return a flagged/uncomputed growth status.

examples:
  - input:
      ward: "Ward 1 – Kasba"
      category: "Roads & Pothole Repair"
      growth_type: "MoM"
      dataset:
        - { period: "2024-06", ward: "Ward 1 – Kasba", category: "Roads & Pothole Repair", budgeted_amount: 13.0, actual_spend: 14.8, notes: "" }
        - { period: "2024-07", ward: "Ward 1 – Kasba", category: "Roads & Pothole Repair", budgeted_amount: 13.0, actual_spend: 19.7, notes: "" }
    expected_output:
      - { period: "2024-06", actual_spend: 14.8, growth: "N/A", formula: "First period in slice" }
      - { period: "2024-07", actual_spend: 19.7, growth: "+33.1%", formula: "((19.7 - 14.8) / 14.8) * 100" }

test_guidance:
  - Verify that when `growth-type` is MoM, the calculation uses the previous month in chronological order.
  - Verify that if a ward/category row has a blank actual spend, the output flags the row using the reason from the notes column.
  - Verify that running the script with missing `--ward` or `--category` triggers a refusal error.
