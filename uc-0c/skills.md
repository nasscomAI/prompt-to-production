# Skills

## load_dataset

Purpose:
- Read the CSV dataset
- Validate required columns
- Detect null values before processing

Responsibilities:
- Load CSV using pandas
- Check required columns:
  - period
  - ward
  - category
  - budgeted_amount
  - actual_spend
  - notes
- Report rows where actual_spend is NULL
- Show null reason using notes column
- Return validated dataframe


## compute_growth

Purpose:
- Calculate growth for a specific ward and category

Responsibilities:
- Accept:
  - ward
  - category
  - growth_type
- Refuse if growth_type is missing
- Prevent aggregation across wards/categories
- Compute Month-over-Month (MoM) growth
- Skip NULL actual_spend rows
- Show formula used for every calculation
- Return per-period growth table