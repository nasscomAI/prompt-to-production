skills:
  - name: load_dataset
    description: Reads a local CSV budget dataset, verifies required columns, and comprehensively identifies all missing values.
    input: File path string to a budget CSV file.
    output: A dataset object containing the structured data, with a summary report of total null count, locations of nulls, and notes associated with those nulls.
    error_handling: Raise an invalid format error if essential columns ('ward', 'category', 'actual_spend', 'period', 'notes') are missing.

  - name: compute_growth
    description: Calculates specific growth metrics (like MoM or YoY) for a designated ward and category over time, maintaining formula transparency.
    input: A request object specifying the filtered dataset (output from load_dataset), target ward, target category, and explicit growth_type.
    output: A tabular dataset representing the computation per period, including calculated values, the literal formula formula text used, and any null-row warning flags.
    error_handling: Return a strict refusal object instead of data if the target ward/category combination spans multiple wards/categories or if growth_type is missing.
