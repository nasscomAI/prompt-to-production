# UC-0C — Financial Data Magistrate Skills

## Skill 1: Null Detection & Note Mapping
- **Input**: `actual_spend` and `notes` columns.
- **Logic**: For every row, check if `actual_spend` is an empty string. 
- **Output**: If empty, capture the `note` as the "Exclusion Reason". If non-empty, convert to float.

## Skill 2: Category-Ward Aggregation
- **Input**: Validated dataset.
- **Logic**: Group data by `category`.
- **Constraint**: Maintain a "Valid Count" and "Excluded Count" per category.

## Skill 3: Precise Mathematical Averaging
- **Input**: Categorical groups.
- **Formula**: `sum(actual_spend) / count(valid_rows)`.
- **Failure Mode**: If `valid_rows == 0`, return "DATA_UNAVAILABLE".

## Skill 4: Magistrate Report Generation
- **Input**: Statistical results.
- **Format**: Generate a markdown table with `Category`, `Average Actual Spend`, `Data Coverage %`.
- **Fulfillment**: Include a section for "Audit Log" listing every row that was excluded and why.
