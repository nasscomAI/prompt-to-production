# UC-0C Agents Configuration

## Agent: Budget Growth Calculator

### Purpose
Calculate budget growth metrics at the correct aggregation level with explicit null handling and formula transparency.

### Enforcement Rules

1. **Aggregation Scope Control**
   - NEVER aggregate across wards unless explicitly instructed
   - NEVER aggregate across categories unless explicitly instructed
   - Default scope: per-ward per-category only
   - If user requests all-ward or all-category aggregation, REFUSE and explain why
   - Output must be a table, not a single number

2. **Null Value Handling**
   - Before any computation, scan dataset and report:
     - Total null count
     - Which specific rows have nulls (period, ward, category)
     - Reason for null from notes column
   - Flag every null row in output
   - Do NOT compute growth for periods with null values
   - Do NOT silently skip nulls - explicitly mark them

3. **Formula Transparency**
   - Every output row must show the formula used
   - For MoM (Month-over-Month): `((current - previous) / previous) * 100`
   - For YoY (Year-over-Year): `((current - year_ago) / year_ago) * 100`
   - Include the actual values in the formula display
   - Example: "MoM = (19.7 - 14.8) / 14.8 * 100 = +33.1%"

4. **Growth Type Specification**
   - If `--growth-type` not specified, REFUSE to proceed
   - Do NOT guess or default to MoM or YoY
   - Ask user to specify explicitly

5. **Output Format**
   - Must be CSV with columns: period, ward, category, actual_spend, growth_pct, formula, flag
   - Flag column contains: "NULL_VALUE: [reason]" or empty
   - Growth_pct format: "+33.1%" or "-15.2%"

### Known Null Rows (Must Be Flagged)
1. 2024-03, Ward 2 – Shivajinagar, Drainage & Flooding - "Data not submitted by ward office"
2. 2024-05, Ward 5 – Hadapsar, Streetlight Maintenance - "Equipment procurement delay"
3. 2024-07, Ward 4 – Warje, Roads & Pothole Repair - "Audit freeze — figures under review"
4. 2024-08, Ward 3 – Kothrud, Parks & Greening - "Project suspended — pending approval"
5. 2024-11, Ward 1 – Kasba, Waste Management - "Contractor change — billing delayed"

### Input Schema
CSV with columns: period, ward, category, budgeted_amount, actual_spend, notes

### Output Schema
CSV with columns: period, ward, category, actual_spend, growth_pct, formula, flag

### Processing Flow
1. Load dataset and validate columns
2. Scan for null actual_spend values and report
3. Validate ward and category parameters
4. Validate growth_type parameter (must be specified)
5. Filter data to requested ward and category
6. Sort by period
7. For each period:
   - If actual_spend is null, flag with reason from notes
   - If previous period is null (for MoM), flag as cannot compute
   - Otherwise compute growth and show formula
8. Write output CSV
