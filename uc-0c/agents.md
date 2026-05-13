# Agent Rules

1. Never aggregate across wards or categories unless explicitly instructed.
   If aggregation is requested without clear instruction, refuse the operation.

2. Flag every NULL actual_spend row before computing growth.
   Include the reason from the notes column.

3. Show the exact formula used for every growth calculation.

4. If --growth-type is not specified, refuse and ask for clarification.
   Never guess the growth type.

5. Growth calculations must be performed only for the selected:
   - ward
   - category

6. Output must be a per-period table, not a single combined number.