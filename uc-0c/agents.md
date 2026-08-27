# UC-0C Agents

## Aggregation Agent
- Role: Reads input CSV with numbers, wards, and categories.
- Input: CSV file with columns: ward, category, value
- Output: CSV with total value per ward per category
- Behavior: Each ward is treated separately; each category is aggregated independently.
- Constraints: No silent aggregation; totals must reflect only scoped ward/category combinations.

## Execution Flow
1. Read input CSV (`read_input()`).
2. Aggregate numbers per ward per category (`aggregate_per_ward_category()`).
3. Save results to `growth_output.csv`.
4. Print completion message.

## Notes
- Agent follows CRAFT rules: completeness, correctness, clarity.