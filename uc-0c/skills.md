# UC-0C Skills
 
## load_dataset
- Reads CSV
- Validates required columns
- Detects null values in actual_spend
- Prints affected rows with notes
 
## compute_growth
- Filters by ward and category
- Computes Month-over-Month growth
- Skips null rows
- Returns table with:
  - period
  - growth
  - formula used