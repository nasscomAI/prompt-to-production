# skills.md — UC-0C Budget Growth Skills
# Aligned with agents.md RICE enforcement

skills:
  - name: load_dataset
    description: Load CSV, validate column structure, detect and report all null rows before returning data.
    
    input: |
      String: file path to ward_budget.csv.
    
    output: |
      Dict with structure:
      {
        "raw_data": [array of dicts with keys: period, ward, category, budgeted_amount, actual_spend, notes],
        "null_rows": [
          {
            "period": "2024-03",
            "ward": "Ward 2 – Shivajinagar",
            "category": "Drainage & Flooding",
            "reason": "<notes value from CSV>"
          },
          ... (all 5 null rows listed before any computation)
        ],
        "metadata": {
          "total_rows": 300,
          "null_count": 5,
          "wards": ["Ward 1 – Kasba", ...],
          "categories": ["Roads & Pothole Repair", ...],
          "periods": ["2024-01", ..., "2024-12"]
        }
      }
    
    enforcement:
      - "E1_validation: Check that all columns present (period, ward, category, budgeted_amount, actual_spend, notes). If missing, raise error."
      - "E2_null_detection: Scan actual_spend column; identify all rows where actual_spend is null/empty. Store with period, ward, category, and notes explanation."
      - "E3_null_count: Report null_count in metadata. Expected: 5 nulls (per README.md). If count <= 4 or >= 6, flag discrepancy."
      - "E4_metadata: Extract unique wards, categories, periods. Wards: 5. Categories: 5. Periods: 12 (Jan-Dec 2024)."
    
    error_handling: |
      If file does not exist: return error with file path and refuse to proceed.
      If columns are missing: return error listing missing columns and refuse to proceed.
      If null_count does not match expected (5): raise warning but continue; include discrepancy in metadata.
      If a period is missing: log warning in metadata; mark in periods array as incomplete.

  - name: compute_growth
    description: Calculate MoM or YoY growth for a specific ward + category, showing formula in every output row and flagging nulls.
    
    input: |
      - raw_data: array from load_dataset (all rows with period, ward, category, budgeted_amount, actual_spend, notes)
      - null_rows: array from load_dataset (list of rows where actual_spend is null)
      - ward (str): exact ward name, e.g., "Ward 1 – Kasba"
      - category (str): exact category name, e.g., "Roads & Pothole Repair"
      - growth_type (str): "MoM" (month-over-month) or "YoY" (year-over-year). MUST be specified or refuse (E4).
    
    output: |
      Array of dicts, one per period for the specified ward+category:
      [
        {
          "period": "2024-01",
          "actual_spend": 13.3,
          "prior_value": null (no prior for first period),
          "formula": "N/A (first period)",
          "growth_pct": null
        },
        {
          "period": "2024-02",
          "actual_spend": 12.2,
          "prior_value": 13.3 (from 2024-01 for MoM; from prior year for YoY),
          "formula": "MoM Growth = (12.2 - 13.3) / 13.3 × 100",
          "growth_pct": -8.27
        },
        {
          "period": "2024-03",
          "actual_spend": null,
          "prior_value": null,
          "formula": "NULL — <reason from notes>",
          "growth_pct": null
        },
        ... (all 12 months including any nulls)
      ]
    
    enforcement:
      - "E1_no_aggregation: Before computing, verify --ward and --category are specified (non-null, non-empty). If either is missing/null/empty or if input contains 'all', 'total', 'aggregate', REFUSE (E1)."
      - "E2_null_in_path: If the current period OR prior period is null, mark output row as NULL with reason from null_rows explanation. Do not compute growth from/to null."
      - "E3_formula_shown: Every output row must include formula string. First month/quarter: formula='N/A (first period or no prior data)'. Subsequent with valid priors: show calculation (e.g., 'MoM Growth = (19.7 - 14.8) / 14.8 × 100'). For nulls: formula='NULL — <reason>'."
      - "E4_growth_type_check: If growth_type is not 'MoM' or 'YoY', REFUSE with 'Growth type not specified. Please provide --growth-type MoM or YoY' (E4)."
      - "E5_per_period: Output exactly 12 rows (one per month 2024-01 through 2024-12), even if nulls present. Do not aggregate or skip."
    
    error_handling: |
      If ward not found in raw_data: return error 'Ward not found: <ward>'. List available wards.
      If category not found for the specified ward: return error 'Category not found for <ward>: <category>'. List available categories.
      If growth_type is null/missing: REFUSE with 'Growth type not specified. Please provide --growth-type MoM or YoY' (E4).
      If growth_type is not 'MoM' or 'YoY': return error 'Invalid growth_type: <value>. Must be MoM or YoY'.
      If a period's actual_spend is null: mark row as NULL with reason. Do not attempt division by zero or computation.
