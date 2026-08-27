skills:
  - name: classify_complaint
    description: Classify one complaint description into UC-0A fields (`category`, `priority`, `reason`, `flag`) using only the allowed label sets and keyword rules.
    input: A single CSV row as a mapping/dict; must contain the complaint text in a `description` field (string). Other fields may be present but are not used for classification.
    output: A dict with `category` (one of the allowed exact strings), `priority` (`Urgent` | `Standard` | `Low`), `reason` (exactly one sentence citing specific words from the complaint description), and `flag` (`NEEDS_REVIEW` or blank string).
    error_handling: If `description` is missing/empty, output `category: Other`, `priority: Standard`, `reason: "Description missing"`, `flag: NEEDS_REVIEW`. If no allowed category can be determined with confidence from the description alone, output `category: Other` and `flag: NEEDS_REVIEW` (with a `reason` explaining the ambiguity).

  - name: batch_classify
    description: Read the input CSV, apply `classify_complaint` to each row, and write the UC-0A output CSV.
    input: `input_csv_path` (string path to `../data/city-test-files/test_[your-city].csv`) and `output_csv_path` (string path for `uc-0a/results_[your-city].csv`).
    output: Writes `output_csv_path` as a CSV containing at least the columns `category`, `priority`, `reason`, and `flag`, with one output row per input row.
    error_handling: For any row that causes classification failure (invalid/missing fields, unexpected row format), fall back to `category: Other`, `priority: Standard`, `reason: "Row invalid or ambiguous"`, and `flag: NEEDS_REVIEW` so the batch run continues without crashing.
