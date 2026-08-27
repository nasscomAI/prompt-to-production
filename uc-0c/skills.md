# UC-0C Skills

## Skill: load_dataset

### Input
- file_path: Path to ward_budget.csv

### Output
Dictionary with:
- data: pandas DataFrame
- null_report: List of null rows with details
- null_count: Total number of null actual_spend values

### Logic
1. Read CSV using pandas
2. Validate required columns exist: period, ward, category, budgeted_amount, actual_spend, notes
3. Scan for null/empty actual_spend values
4. For each null row, extract:
   - period
   - ward
   - category
   - reason from notes column
5. Print null report before returning:
   ```
   Found 5 null actual_spend values:
   - 2024-03, Ward 2 – Shivajinagar, Drainage & Flooding: Data not submitted by ward office
   - 2024-05, Ward 5 – Hadapsar, Streetlight Maintenance: Equipment procurement delay
   ...
   ```
6. Return data and null report

### Example Output
```python
{
    "data": <DataFrame>,
    "null_report": [
        {
            "period": "2024-03",
            "ward": "Ward 2 – Shivajinagar",
            "category": "Drainage & Flooding",
            "reason": "Data not submitted by ward office"
        },
        ...
    ],
    "null_count": 5
}
```

---

## Skill: compute_growth

### Input
- dataset: Output from load_dataset
- ward: Specific ward name
- category: Specific category name
- growth_type: "MoM" or "YoY"
- output_file: Path for output CSV

### Output
CSV file with growth calculations

### Logic
1. **Validate Parameters**
   - Check growth_type is specified (not None)
   - If not specified, print error and exit: "Error: --growth-type must be specified (MoM or YoY)"
   - Check ward exists in dataset
   - Check category exists in dataset

2. **Filter Data**
   - Filter to specified ward and category only
   - Sort by period ascending
   - Result should be 12 rows (one per month)

3. **Compute Growth Per Period**
   - Initialize results list
   - For each period:
     - Get current actual_spend
     - If current is null:
       - Add row with flag: f"NULL_VALUE: {reason from null_report}"
       - growth_pct = "N/A"
       - formula = "Cannot compute - null value"
     - Else if growth_type == "MoM":
       - Get previous month's actual_spend
       - If previous is null or doesn't exist:
         - flag = "Cannot compute - previous period null or missing"
         - growth_pct = "N/A"
       - Else:
         - growth_pct = ((current - previous) / previous) * 100
         - formula = f"({current} - {previous}) / {previous} * 100"
         - Format growth_pct as "+X.X%" or "-X.X%"
     - Else if growth_type == "YoY":
       - Get same month previous year
       - Similar logic as MoM

4. **Write Output**
   - Create DataFrame with columns: period, ward, category, actual_spend, growth_pct, formula, flag
   - Write to CSV
   - Print summary: "Computed growth for {ward}, {category} using {growth_type}"

### Example Output Row
```csv
period,ward,category,actual_spend,growth_pct,formula,flag
2024-07,Ward 1 – Kasba,Roads & Pothole Repair,19.7,+33.1%,(19.7 - 14.8) / 14.8 * 100,
2024-11,Ward 1 – Kasba,Waste Management,,,Cannot compute - null value,NULL_VALUE: Contractor change — billing delayed
```
