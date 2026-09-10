# UC-0C Budget Growth Skills

## Skill 1: Load Dataset
Read the CSV and validate that the required columns are present.
Report the total row count and identify every row where actual spend is null.

## Skill 2: Null Handling
Before calculating growth, flag every null actual-spend row.
Use the notes column to report the reason for each null.
Never invent or estimate a missing value.

## Skill 3: Growth Calculation
Calculate growth only when the growth type is explicitly specified.
Support MoM (Month-over-Month) and YoY (Year-over-Year).
If growth type is missing, refuse to calculate and ask for clarification.

## Skill 4: Correct Aggregation
Keep results at the per-ward, per-category, per-period level.
Never combine different wards or categories unless explicitly instructed.

## Skill 5: Formula Transparency
Show the formula used in every output row alongside the calculated result.

## Skill 6: Validation
Before final output, verify that:
- All null rows are flagged.
- Null reasons come from the notes column.
- No missing values were invented.
- The requested growth type was used.
- Ward and category aggregation levels are preserved.
- Every result includes its formula.
