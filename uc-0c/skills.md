skills:

  load_dataset:
    description: >
      Reads the ward budget CSV, validates the required columns,
      identifies null actual_spend values, and reports the affected
      rows and their notes before returning the dataset.

    input:
      - csv_file

    output:
      - validated_dataset
      - null_rows
      - null_count

    rules:
      - Required columns are period, ward, category, budgeted_amount, actual_spend, and notes.
      - actual_spend may be blank and must be treated as null.
      - Report every null row and its notes value.
      - Do not silently replace null actual_spend values with zero or another value.

  compute_growth:
    description: >
      Takes an explicitly selected ward, category, and growth type and
      returns a per-period growth table with the formula shown.

    input:
      - validated_dataset
      - ward
      - category
      - growth_type

    output:
      - per_period_growth_table

    rules:
      - Filter to exactly the requested ward and category.
      - Never aggregate across wards or categories.
      - Growth type must be explicitly provided.
      - For MoM, compare the current period actual spend with the previous period actual spend.
      - If either value required for a growth calculation is null, do not calculate the growth and flag the row.
      - Show the formula used for every calculated row.
      - Preserve the null reason from the notes column.
