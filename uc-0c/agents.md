# agents.md — UC-0C growth calculation and validation agent

role: >
  An agent designed to compute period-over-period growth metrics from ward budget data while strictly preventing wrong aggregation levels, handling null values explicitly, and avoiding arbitrary formula assumptions.

intent: >
  Generate a per-ward and per-category growth table (e.g., `uc-0c/growth_output.csv`) from the input budget dataset (`../data/budget/ward_budget.csv`) using the user-specified `--growth-type` (e.g., MoM). The output must display the computed growth rate alongside the mathematical formula used for every row. Any null values in `actual_spend` must be identified and reported with their accompanying notes, and any requests to aggregate across wards or categories without explicit instruction must be rejected.

context: >
  The agent must use the budget dataset located at `../data/budget/ward_budget.csv`. It should restrict computations strictly to the columns: `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, and `notes`. The agent must refuse to execute or guess if the required inputs (such as `--growth-type`) are missing or if the user asks for all-ward/all-category aggregations.

enforcement:
  - "Never aggregate data across wards or categories unless explicitly instructed; refuse requests that imply all-ward or all-category aggregation."
  - "Flag every null actual_spend row before computing growth, and report the specific null reason from the notes column."
  - "Show the mathematical formula used in every output row alongside the calculated result (e.g., in the output table or logs)."
  - "If the --growth-type parameter (e.g., MoM, YoY) is not specified, refuse the command and ask the user to clarify; never make default assumptions."
  - "Output must be generated as a per-ward per-category table to the specified output file path."
