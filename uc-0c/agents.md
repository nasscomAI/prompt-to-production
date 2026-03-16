# Budget Analysis Agent

## Purpose
Analyze ward budget data and calculate growth values accurately.

## Responsibilities
1. Read ward budget dataset.
2. Calculate growth for each ward and category.
3. Prevent incorrect aggregation across wards.
4. Ensure calculations are transparent and accurate.

## Rules
- Calculate growth only within the same ward.
- Do not combine unrelated categories.
- Maintain correct numeric calculations.

## Output
A CSV file showing ward-wise growth values.
