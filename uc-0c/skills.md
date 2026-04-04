# Skills: Growth Calculator

## load_dataset
**Description:** Reads CSV, validates columns, and reports null count and which rows.
**Inputs:** filepath
**Outputs:** Checked rows.

## compute_growth
**Description:** Takes ward, category, and growth_type, returns per-period table with formula shown. 
**Rules:**
- Validates the requested inputs
- Computes period over period growth based on growth type
- Ensures formulas are in output
