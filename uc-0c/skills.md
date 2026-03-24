# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Opens the CSV budget dataset, verifies the integrity of the required columns, and proactively scans for missing `actual_spend` anomalies.
    input: String path to the target CSV budget dataset.
    output: A structured table/dataframe alongside a pre-computation report detailing the exact count and specifics of any null/blank rows detected in the data.
    error_handling: Halts and raises an error if the schema matches are invalid. Refuses to conceal nulls.

  - name: compute_growth
    description: Calculates specific growth metrics (MoM/YoY) on a strictly filtered subset of data (ward + category) without unauthorized global aggregation.
    input: The filtered dataset structure, the targeted `ward`, the targeted `category`, and the explicitly declared `growth_type`. 
    output: A per-period chronological table showing the computed growth, and explicitly attaching the mathematical formula used to derive the result on every generated row.
    error_handling: Immediately halts and refuses to execute if `growth_type` is omitted or if parameters attempt to enforce cross-ward/cross-category global aggregation.
