skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates that all required columns are
      present, and reports the total null count and the specific rows where
      actual_spend is null before returning the dataset for downstream use.
    input:
      type: file_path
      format: String path to a CSV file expected to contain columns — period
        (YYYY-MM), ward (string), category (string), budgeted_amount (float),
        actual_spend (float or blank), notes (string).
    output:
      type: object
      format: |
        {
          "data": <parsed row array with all six columns>,
          "null_report": [
            {
              "period": "YYYY-MM",
              "ward": "<ward name>",
              "category": "<category name>",
              "notes": "<null reason from notes column>"
            }
          ],
          "null_count": <integer>,
          "malformed_report": [
            {
              "row_number": <integer>,
              "period": "YYYY-MM",
              "actual_spend_value": "<raw string>"
            }
          ]
        }
    error_handling:
      - If the file path does not exist or cannot be read, raise FileNotFoundError
        and halt; do not return partial data.
      - If any of the six required columns are absent, list every missing column
        name and refuse to return the dataset.
      - If actual_spend contains values that are neither a valid float nor blank,
        flag those rows in malformed_report and do not silently coerce or drop them.
      - If the CSV contains zero data rows after the header, raise EmptyDatasetError
        and halt.
      - If any period value does not conform to YYYY-MM format, list every
        offending row and halt; do not attempt to parse or reformat them.

  - name: compute_growth
    description: Accepts a single ward, a single category, and an explicit
      growth_type (MoM or YoY), then returns a per-period table showing the
      growth value and the exact formula used for every non-null row, with null
      rows retained and flagged.
    input:
      type: object
      format: |
        {
          "data": <row array produced by load_dataset>,
          "ward": "<exact ward name string>",
          "category": "<exact category name string>",
          "growth_type": "MoM" | "YoY"
        }
    output:
      type: array
      format: |
        Each element is a row object:
        {
          "period": "YYYY-MM",
          "ward": "<ward name>",
          "category": "<category name>",
          "actual_spend": <float> | null,
          "growth_value": "<±N.N%>" | null,
          "formula_used": "<e.g. (19.7 - 14.8) / 14.8 = +33.1%>" | null,
          "null_flag": true | false,
          "null_reason": "<notes value or derived reason>" | null
        }
    error_handling:
      - If growth_type is missing, null, or any value other than "MoM" or "YoY",
        refuse to compute and return an error requiring the caller to supply an
        explicit growth_type; never default to either option.
      - If ward or category are absent from the input object, refuse and prompt
        the caller to supply both; never compute across multiple wards or
        categories.
      - If ward or category do not exactly match a value present in the dataset,
        return an error listing valid ward and category values; do not fuzzy-match
        or proceed with a partial match.
      - If the caller passes a list for ward or category rather than a single
        string, refuse immediately with an aggregation refusal error.
      - If the filtered dataset for the given ward and category is empty after
        filtering, return an EmptyFilterError and halt.
      - For any row where actual_spend is null, set growth_value and formula_used
        to null and null_flag to true; do not interpolate, skip, or estimate a
        growth figure.
      - If the previous period required for a growth calculation is itself null
        or absent from the filtered dataset, set the current row's growth_value
        to null and null_flag to true; never use a stale or adjacent value as a
        substitute denominator.
      - If the previous period actual_spend is zero, set growth_value to null
        and null_flag to true with null_reason indicating division by zero;
        never emit infinity or a coerced result.