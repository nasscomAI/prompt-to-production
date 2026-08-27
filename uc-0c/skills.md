# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV from the specified path, validates that all
      required columns are present, identifies and reports every null
      actual_spend row with its notes reason, and returns the validated
      dataset only after the null report is complete.
    input:
      type: string
      format: >
        A file path pointing to a CSV file; expected path is
        ../data/budget/ward_budget.csv; the file must contain exactly the
        columns period (YYYY-MM string), ward (string), category (string),
        budgeted_amount (float), actual_spend (float or blank), and notes
        (string); 300 rows expected covering 5 wards, 5 categories, and 12
        monthly periods from 2024-01 through 2024-12.
    output:
      type: object
      format: >
        An object with two fields: null_report and dataset; null_report is
        an ordered list of objects each containing period, ward, category,
        and null_reason (verbatim text from the notes column) for every row
        where actual_spend is blank — must include all five known null rows
        (2024-03 Ward 2 Shivajinagar Drainage and Flooding, 2024-07 Ward 4
        Warje Roads and Pothole Repair, 2024-11 Ward 1 Kasba Waste
        Management, 2024-08 Ward 3 Kothrud Parks and Greening, 2024-05
        Ward 5 Hadapsar Streetlight Maintenance); dataset is the full parsed
        row collection available for downstream filtering and computation,
        with null actual_spend values preserved as null and not imputed.
    error_handling:
      file_not_found: >
        If the file path does not resolve to a readable file, halt and raise
        a descriptive error stating the expected path — do not return a
        partial or empty dataset.
      missing_column: >
        If any of the six required columns (period, ward, category,
        budgeted_amount, actual_spend, notes) are absent from the CSV
        header, halt and raise a schema error naming every missing column —
        do not proceed with a structurally incomplete dataset.
      null_without_notes: >
        If a row has a null actual_spend but an empty notes field, include
        the row in the null_report with null_reason set to "No reason
        provided in notes column" and emit a WARNING — do not silently
        omit the row from the null_report.
      unexpected_row_count: >
        If the parsed row count differs materially from the expected 300,
        emit a WARNING stating the actual count before returning — do not
        suppress the discrepancy, as it may indicate a truncated or
        duplicate file.
      null_count_mismatch: >
        If the number of null actual_spend rows detected is not five, emit
        a WARNING listing the detected null rows and their count — do not
        assume the known five are the only ones present.

  - name: compute_growth
    description: >
      Takes a ward filter, a category filter, and an explicit growth_type
      parameter, filters the loaded dataset to the matching rows, computes
      the requested growth metric for each period, and returns a per-period
      table where every computed row includes the formula used and every
      null row is flagged as non-computed with its null reason.
    input:
      type: object
      format: >
        An object with four fields: dataset (the validated row collection
        returned by load_dataset), ward (a non-empty string matching one of
        the five ward names exactly), category (a non-empty string matching
        one of the five category names exactly), and growth_type (must be
        explicitly provided as either the string MoM for month-on-month or
        YoY for year-on-year — no default value is assumed if absent).
    output:
      type: object
      format: >
        An object with two fields: flagged_rows and growth_table;
        flagged_rows is a list of objects each containing period, ward,
        category, and null_reason for every period where actual_spend is
        null within the filtered subset — these rows are excluded from
        growth computation and must appear in flagged_rows before
        growth_table is populated; growth_table is an ordered list of
        objects each containing period, ward, category, actual_spend,
        growth_value (as a percentage string with sign), and formula (the
        exact arithmetic expression used to produce growth_value for that
        row); growth_table must not contain any row spanning multiple wards
        or multiple categories.
    error_handling:
      growth_type_not_specified: >
        If the growth_type field is absent, null, or any value other than
        MoM or YoY, the skill must refuse to proceed, return no computation,
        and emit an error asking the caller to specify growth_type explicitly
        as MoM or YoY — defaulting to either formula without instruction is
        a violation.
      ward_not_found: >
        If the ward value does not match any ward name in the dataset, halt
        and raise an error listing the valid ward names — do not return an
        empty growth_table without explanation.
      category_not_found: >
        If the category value does not match any category name in the
        dataset, halt and raise an error listing the valid category names —
        do not return an empty growth_table without explanation.
      aggregation_requested: >
        If the ward or category field is a wildcard, all-wards instruction,
        or any value that would cause the skill to compute growth across
        multiple wards or multiple categories in a single aggregated row,
        the skill must refuse and return an error stating that cross-ward
        and cross-category aggregation is not permitted — it must not
        produce a single aggregated number under any circumstances.
      null_row_in_computation_window: >
        If a null actual_spend row falls within the filtered period range,
        it must be added to flagged_rows with its null_reason from the notes
        column and excluded from growth_table — it must never be imputed
        with zero, carried forward, or silently skipped without appearing
        in flagged_rows.
      reference_value_deviation: >
        If growth_type is MoM and the filtered selection is Ward 1 Kasba
        Roads and Pothole Repair, the computed growth values for 2024-07
        and 2024-10 must match the reference values of +33.1% and -34.8%
        respectively within acceptable floating-point rounding — a material
        deviation must be treated as a formula error and reported before
        output is returned.
      insufficient_periods_for_growth: >
        If the filtered dataset contains fewer than two non-null periods,
        growth cannot be computed — halt and raise an error stating that
        insufficient non-null periods are available for the requested
        ward and category combination.