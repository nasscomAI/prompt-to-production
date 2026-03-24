"""
UC-0C — Municipal Finance Auditor: Ward-Level Budget Growth Calculator

Implements granular Month-over-Month (MoM) growth calculation with strict 
enforcement of data transparencency and null handling. Acts as Municipal 
Finance Auditor prioritizing accuracy over completion.

Core principles:
- NO all-ward or all-category aggregations
- Explicit flag every null actual_spend value
- Show formula in every output row
- Refuse if growth-type not specified
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# Known null rows as per README.md
KNOWN_NULL_ROWS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}

# Valid growth types
VALID_GROWTH_TYPES = {"MoM", "YoY"}


@dataclass
class BudgetRow:
    """Represents a single budget record"""
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: Optional[float]
    notes: str


def load_dataset(file_path: str) -> Tuple[List[BudgetRow], Dict[str, int]]:
    """
    Ingests the ward budget CSV and performs a pre-computation audit to 
    identify missing values.
    
    Args:
        file_path: Path to ward_budget.csv
    
    Returns:
        Tuple of:
        - List of BudgetRow objects with parsed data
        - Dictionary with null summary including row count and reasons
    
    Error handling:
        If required columns ('ward', 'category', 'actual_spend') are missing,
        abort and log a structural error.
    """
    
    file = Path(file_path)
    
    if not file.exists():
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    rows = []
    null_summary = {}
    null_count = 0
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no header")
            
            actual_columns = set(reader.fieldnames)
            missing = required_columns - actual_columns
            
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    period = row.get('period', '').strip()
                    ward = row.get('ward', '').strip()
                    category = row.get('category', '').strip()
                    budgeted = row.get('budgeted_amount', '').strip()
                    actual_str = row.get('actual_spend', '').strip()
                    notes = row.get('notes', '').strip()
                    
                    # Parse numbers
                    try:
                        budgeted_amount = float(budgeted) if budgeted else 0.0
                    except ValueError:
                        budgeted_amount = 0.0
                    
                    actual_spend = None
                    if actual_str:
                        try:
                            actual_spend = float(actual_str)
                        except ValueError:
                            pass
                    
                    # Track null rows
                    if actual_spend is None:
                        null_count += 1
                        key = f"{period}|{ward}|{category}"
                        null_summary[key] = {
                            'row_num': row_num,
                            'reason': notes,
                            'period': period,
                            'ward': ward,
                            'category': category
                        }
                    
                    budget_row = BudgetRow(
                        period=period,
                        ward=ward,
                        category=category,
                        budgeted_amount=budgeted_amount,
                        actual_spend=actual_spend,
                        notes=notes
                    )
                    rows.append(budget_row)
                
                except Exception as e:
                    print(f"Warning: Error parsing row {row_num}: {str(e)}", 
                          file=sys.stderr)
                    continue
        
        print(f"Loaded {len(rows)} budget records")
        print(f"Identified {null_count} null actual_spend values before any calculations")
        
        for key, info in null_summary.items():
            print(f"  NULL: {info['period']} | {info['ward']} | {info['category']} — "
                  f"Reason: {info['reason']}")
        
        return rows, null_summary
    
    except Exception as e:
        raise FileNotFoundError(f"Failed to load dataset: {str(e)}")


def compute_growth(rows: List[BudgetRow], ward: str, category: str, 
                   growth_type: str, null_summary: Dict) -> List[Dict]:
    """
    Calculates period-by-period growth for a filtered subset of data,
    embedding the formula in the result.
    
    Args:
        rows: List of BudgetRow objects
        ward: Specific ward name to process
        category: Specific category name to process
        growth_type: Either 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)
        null_summary: Dictionary of null rows with reasons
    
    Returns:
        List of dictionaries with [Period, Actual Spend, Growth %, Formula, Flag]
    
    Error handling:
        If 'NULL' encountered in current or previous period's actual_spend,
        set Growth to 'N/A', Formula to 'Incomplete Data', and Flag to reason
    """
    
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Invalid growth_type '{growth_type}'. Must be one of: {', '.join(VALID_GROWTH_TYPES)}"
        )
    
    # Filter rows for specific ward and category
    filtered = [r for r in rows 
                if r.ward == ward and r.category == category]
    
    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'"
        )
    
    # Sort by period
    filtered.sort(key=lambda r: r.period)
    
    results = []
    
    for i, current_row in enumerate(filtered):
        result = {
            'period': current_row.period,
            'actual_spend': current_row.actual_spend,
            'growth_percent': None,
            'formula': None,
            'flag': ''
        }
        
        # Check if current period is null
        null_key = f"{current_row.period}|{current_row.ward}|{current_row.category}"
        if null_key in null_summary:
            result['actual_spend'] = 'NULL'
            result['growth_percent'] = 'N/A'
            result['formula'] = 'Incomplete Data'
            result['flag'] = null_summary[null_key]['reason']
            results.append(result)
            continue
        
        # First period has no previous comparison
        if i == 0:
            result['growth_percent'] = 'N/A'
            result['formula'] = 'First period (no baseline)'
            result['flag'] = ''
            results.append(result)
            continue
        
        # Determine previous period based on growth type
        if growth_type == 'MoM':
            previous_row = filtered[i - 1]
        else:  # YoY
            # Find previous year same month
            previous_row = None
            current_month = current_row.period[-2:]  # Extract MM from YYYY-MM
            for j in range(i - 1, -1, -1):
                if filtered[j].period[-2:] == current_month:
                    previous_row = filtered[j]
                    break
            
            if not previous_row:
                result['growth_percent'] = 'N/A'
                result['formula'] = 'No previous year data'
                result['flag'] = ''
                results.append(result)
                continue
        
        # Check if previous period is null
        prev_null_key = (f"{previous_row.period}|{previous_row.ward}|{previous_row.category}")
        if prev_null_key in null_summary:
            result['growth_percent'] = 'N/A'
            result['formula'] = 'Incomplete Data'
            result['flag'] = f"Previous period null: {null_summary[prev_null_key]['reason']}"
            results.append(result)
            continue
        
        # Both periods have valid data
        if current_row.actual_spend is not None and previous_row.actual_spend is not None:
            previous_spend = previous_row.actual_spend
            current_spend = current_row.actual_spend
            
            if previous_spend == 0:
                result['growth_percent'] = 'Infinity'
                result['formula'] = f'({current_spend} - 0) / 0'
                result['flag'] = 'Division by zero (previous spend was 0)'
            else:
                growth = ((current_spend - previous_spend) / previous_spend) * 100
                result['growth_percent'] = f"{growth:+.1f}%"
                result['formula'] = f'({current_spend} - {previous_spend}) / {previous_spend} × 100'
                result['flag'] = ''
        else:
            result['growth_percent'] = 'N/A'
            result['formula'] = 'Incomplete Data'
            result['flag'] = 'Missing actual_spend in current or previous period'
        
        results.append(result)
    
    return results


def write_output(results: List[Dict], output_path: str, ward: str, 
                 category: str, growth_type: str) -> None:
    """
    Writes growth results to CSV file with metadata.
    
    Args:
        results: List of growth calculation results
        output_path: Path to write output CSV
        ward: Ward name for metadata
        category: Category name for metadata
        growth_type: Growth type used (MoM/YoY)
    """
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            f.write(f"# Ward-Level Budget Growth Analysis\n")
            f.write(f"# Ward: {ward}\n")
            f.write(f"# Category: {category}\n")
            f.write(f"# Growth Type: {growth_type}\n")
            f.write(f"# Note: All null actual_spend values have been identified and flagged\n\n")
            
            fieldnames = ['period', 'actual_spend_lakh', 'growth_percent', 'formula', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'period': result['period'],
                    'actual_spend_lakh': result['actual_spend'],
                    'growth_percent': result['growth_percent'],
                    'formula': result['formula'],
                    'flag': result['flag']
                })
        
        print(f"Output written to: {output_path}")
    
    except Exception as e:
        raise IOError(f"Failed to write output file: {str(e)}")


def main():
    """
    Command-line interface for the budget growth calculator.
    
    Enforces strict parameter checking and granular computation.
    
    Usage:
        python app.py --input ../data/budget/ward_budget.csv \
                      --ward "Ward 1 – Kasba" \
                      --category "Roads & Pothole Repair" \
                      --growth-type MoM \
                      --output growth_output.csv
    """
    
    parser = argparse.ArgumentParser(
        description="UC-0C Municipal Finance Auditor: Ward-Level Budget Growth Calculator"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Specific ward name (required — no all-ward aggregation)"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Specific category name (required — no all-category aggregation)"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=VALID_GROWTH_TYPES,
        help=f"Growth type: must be explicitly specified. Options: {', '.join(VALID_GROWTH_TYPES)}"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output growth_output.csv"
    )
    
    args = parser.parse_args()
    
    try:
        # Validation Rule 1: Reject aggregation requests
        if args.ward.lower() == "all" or args.category.lower() == "all":
            print("ERROR: All-ward and all-category aggregations are REFUSED", 
                  file=sys.stderr)
            print("You must specify an explicit ward and category.", file=sys.stderr)
            sys.exit(1)
        
        # Validation Rule 2: Growth type is mandatory
        if not args.growth_type:
            print("ERROR: --growth-type must be explicitly specified", file=sys.stderr)
            print(f"Valid options: {', '.join(VALID_GROWTH_TYPES)}", file=sys.stderr)
            sys.exit(1)
        
        # Step 1: Load and audit dataset
        print(f"Loading budget data from: {args.input}")
        rows, null_summary = load_dataset(args.input)
        
        # Step 2: Compute growth
        print(f"\nComputing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        results = compute_growth(rows, args.ward, args.category, 
                                args.growth_type, null_summary)
        
        # Step 3: Write output
        print(f"\nGenerating output with formula transparency...")
        write_output(results, args.output, args.ward, args.category, args.growth_type)
        
        print(f"\nSUCCESS: Growth calculation complete with full data transparency")
    
    except ValueError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
