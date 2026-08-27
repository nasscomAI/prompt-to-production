# skills.md — UC-0C

skills:
  - name: load_dataset
    description: Reads the CSV dataset from disk, logs null counts transparently, and filters down strictly to the exact requested ward and category before handing off to the LLM to prevent cross-aggregation bleed.
    input: input_path (string), ward (string), category (string)
    output: A filtered dictionary array representing only exactly matched rows, alongside a count of missing values.
    error_handling: Refuses execution programmatically if the input criteria are missing.

  - name: compute_growth
    description: Prompts the LLM with the filtered dataset and strict constraints to compute the requested local growth.
    input: filtered_dataset (array), growth_type (string)
    output: A string explicitly noting nulls and fully transparent calculations.
    error_handling: Emits an immediate fallback refusal if the LLM detects scope bleed.
