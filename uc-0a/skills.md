# skills.md
skills:
  - name: classify_complaint
    description: Parses a citizen complaint description to output a structured categorization perfectly avoiding taxonomy drift, severity blindness, hallucinated categories, and false confidence.
    input: Dictionary containing a `description` string representing the complaint text.
    output: A dictionary with strictly constrained keys: `category` (from the exact list of 10), `priority` (`Urgent`/`Standard`/`Low`), `reason` (exactly one sentence citing specific words), and `flag`.
    error_handling: If the description is genuinely ambiguous or lacks adequate context, it sets category to "Other" and flag to "NEEDS_REVIEW" instead of hallucinating.

  - name: batch_classify
    description: Reads an input dataset of citizen complaints, leverages the classify_complaint skill row-by-row, and outputs a properly formatted structural dataset.
    input: Two strings representing `input_path` (path to input CSV) and `output_path` (path to save results CSV).
    output: None (writes a structured CSV file to disk).
    error_handling: Handles malformed CSV rows without crashing the process. Any row that fails parsing defaults to category "Other" and flag "NEEDS_REVIEW".
