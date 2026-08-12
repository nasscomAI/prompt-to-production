#!/usr/bin/env python3
"""
UC-0C: Number That Looks Right — Budget Growth Calculator

Computes monthly or yearly growth metrics for specific ward-category combinations,
rejecting all-ward aggregations and handling null actual_spend values with explicit flags.

Core Enforcement:
- Never aggregate across wards or categories
- Flag and report all 5 null actual_spend rows before computing
- Show formula used in every output row
- Refuse if --growth-type not specified; never guess
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np


# Configuration
REQUIRED_COLUMNS = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
KNOWN_NULL_ROWS = [
    {'period': '2024-03', 'ward': 'Ward 2 – Shivajinagar', 'category': 'Drainage & Flooding'},
    {'period': '2024-07', 'ward': 'Ward 4 – Warje', 'category': 'Roads & Pothole Repair'},
    {'period': '2024-11', 'ward': 'Ward 1 – Kasba', 'category': 'Waste Management'},
    {'period': '2024-08', 'ward': 'Ward 3 – Kothrud', 'category': 'Parks & Greening'},
    {'period': '2024-05', 'ward': 'Ward 5 – Hadapsar', 'category': 'Streetlight Maintenance'},
]
VALID_GROWTH_TYPES = {'MoM', 'YoY'}


class BudgetCalculationError(Exception):
    """Base exception for budget calculation errors."""
    pass


class BudgetGrowthCalculator:
    """
    Calculates budget growth metrics with strict enforcement of validation rules.
    
    Implements two skills:
    - load_dataset: Reads and validates CSV, reports null rows
    - compute_growth: Calculates MoM/YoY growth for ward-category with formulas
    """
    
    def __init__(self):
        """Initialize calculator state."""
        self.df: Optional[pd.DataFrame] = None
        self.null_report: Dict = {}
    
    def load_dataset(self, input_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        SKILL: load_dataset
        Reads CSV, validates columns, reports null rows with reasons.
        
        Args:
            input_path: Path to ward_budget.csv
            
        Returns:
            Tuple of (DataFrame, null_report dict)
            
        Raises:
            BudgetCalculationError: If validation fails
        """
        # ERROR HANDLING: File not found
        if not os.path.exists(input_path):
            raise BudgetCalculationError(f"Input file not found: {input_path}")
        
        try:
            df = pd.read_csv(input_path)
        except Exception as e:
            raise BudgetCalculationError(f"Error reading CSV: {e}")
        
        # ERROR HANDLING: Check required columns
        missing_cols = REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise BudgetCalculationError(
                f"Required columns missing: {', '.join(sorted(missing_cols))}"
            )
        
        # Validate and convert types
        try:
            df['period'] = df['period'].astype(str)
            df['budgeted_amount'] = pd.to_numeric(df['budgeted_amount'], errors='coerce')
            df['actual_spend'] = pd.to_numeric(df['actual_spend'], errors='coerce')
        except Exception as e:
            raise BudgetCalculationError(f"Error converting data types: {e}")
        
        # ERROR HANDLING: Validate period format YYYY-MM
        invalid_periods = []
        for idx, period in enumerate(df['period']):
            if not self._is_valid_period(period):
                invalid_periods.append((idx + 2, period))  # +2 for header + 1-indexing
        
        if invalid_periods:
            error_msg = "Period values do not match YYYY-MM format:\n"
            for row, period in invalid_periods[:5]:
                error_msg += f"  Row {row}: '{period}'\n"
            raise BudgetCalculationError(error_msg)
        
        # Find all null actual_spend rows
        null_mask = df['actual_spend'].isna()
        null_rows = df[null_mask].copy()
        
        # Build null report
        self.null_report = {
            'total_null_count': len(null_rows),
            'null_rows': []
        }
        
        for _, row in null_rows.iterrows():
            self.null_report['null_rows'].append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row['notes'] if pd.notna(row['notes']) else 'Not specified'
            })
        
        # ERROR HANDLING: Report discrepancy if not exactly 5 null rows
        if len(null_rows) != 5:
            print(
                f"WARNING: Expected 5 null rows but found {len(null_rows)}",
                file=sys.stderr
            )
        
        # Report null rows found
        print(f"✓ Dataset loaded: {len(df)} rows", file=sys.stderr)
        print(f"✓ Null actual_spend rows found: {len(null_rows)}", file=sys.stderr)
        for nr in self.null_report['null_rows']:
            print(
                f"  - {nr['period']} | {nr['ward']} | {nr['category']} | "
                f"Reason: {nr['reason']}",
                file=sys.stderr
            )
        
        self.df = df
        return df, self.null_report
    
    def _is_valid_period(self, period: str) -> bool:
        """Check if period matches YYYY-MM format."""
        try:
            datetime.strptime(str(period), '%Y-%m')
            return True
        except (ValueError, TypeError):
            return False
    
    def compute_growth(self, df: pd.DataFrame, ward: str, category: str,
                      growth_type: str) -> pd.DataFrame:
        """
        SKILL: compute_growth
        Calculates MoM or YoY growth for specific ward-category combination.
        
        Args:
            df: Loaded dataset
            ward: Ward name (must match exactly)
            category: Category name (must match exactly)
            growth_type: 'MoM' or 'YoY'
            
        Returns:
            DataFrame with columns: period, actual_spend, growth_rate, formula, null_flag
            
        Raises:
            BudgetCalculationError: If validation fails
        """
        # ERROR HANDLING: growth_type not specified
        if not growth_type or growth_type.strip() == '':
            raise BudgetCalculationError(
                "ERROR: --growth-type not specified. "
                "Please specify 'MoM' (month-over-month) or 'YoY' (year-over-year)"
            )
        
        # ERROR HANDLING: Invalid growth_type
        if growth_type not in VALID_GROWTH_TYPES:
            raise BudgetCalculationError(
                f"Invalid growth_type '{growth_type}'. "
                f"Valid options: {', '.join(VALID_GROWTH_TYPES)}"
            )
        
        # ERROR HANDLING: Ward not found
        if ward not in df['ward'].values:
            raise BudgetCalculationError(
                f"Ward '{ward}' not found in dataset. "
                f"Available wards: {', '.join(sorted(df['ward'].unique()))}"
            )
        
        # ERROR HANDLING: Category not found
        if category not in df['category'].values:
            raise BudgetCalculationError(
                f"Category '{category}' not found in dataset. "
                f"Available categories: {', '.join(sorted(df['category'].unique()))}"
            )
        
        # Filter data for specific ward-category
        subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
        
        # ERROR HANDLING: No data found
        if len(subset) == 0:
            raise BudgetCalculationError(
                f"No data found for {ward} / {category}"
            )
        
        # Sort by period
        subset = subset.sort_values('period').reset_index(drop=True)
        
        # Compute growth
        output_rows = []
        for idx, row in subset.iterrows():
            period = row['period']
            actual_spend = row['actual_spend']
            
            output_row = {
                'period': period,
                'actual_spend': actual_spend if pd.notna(actual_spend) else 'NULL',
                'growth_rate': '',
                'formula': '',
                'null_flag': ''
            }
            
            # Handle null current spend
            if pd.isna(actual_spend):
                output_row['growth_rate'] = 'NULL'
                output_row['formula'] = 'Data not available'
                output_row['null_flag'] = 'FLAGGED'
            # Handle first month (no previous period)
            elif idx == 0:
                output_row['growth_rate'] = 'NULL'
                output_row['formula'] = 'N/A - first month'
            else:
                # Get previous row
                prev_row = subset.iloc[idx - 1]
                prev_spend = prev_row['actual_spend']
                prev_period = prev_row['period']
                
                # ERROR HANDLING: Previous period is null
                if pd.isna(prev_spend):
                    output_row['growth_rate'] = 'NULL'
                    output_row['formula'] = f'Cannot compute - previous period ({prev_period}) is NULL'
                else:
                    if growth_type == 'MoM':
                        growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                        formula = f"({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                    else:  # YoY
                        # For YoY, need to look back 12 months
                        year_ago_idx = None
                        current_year = int(period.split('-')[0])
                        current_month = int(period.split('-')[1])
                        target_period = f"{current_year - 1}-{current_month:02d}"
                        
                        for search_idx, search_row in subset.iterrows():
                            if search_row['period'] == target_period:
                                year_ago_idx = search_idx
                                break
                        
                        if year_ago_idx is None or pd.isna(subset.iloc[year_ago_idx]['actual_spend']):
                            output_row['growth_rate'] = 'NULL'
                            output_row['formula'] = 'No year-over-year comparison available'
                        else:
                            year_ago_spend = subset.iloc[year_ago_idx]['actual_spend']
                            growth_pct = ((actual_spend - year_ago_spend) / year_ago_spend) * 100
                            formula = (
                                f"({actual_spend:.1f} - {year_ago_spend:.1f}) / "
                                f"{year_ago_spend:.1f} * 100"
                            )
                            output_row['growth_rate'] = f"{growth_pct:+.1f}%"
                            output_row['formula'] = formula
                    
                    # Set MoM growth rate and formula if computed
                    if output_row['growth_rate'] == '':
                        output_row['growth_rate'] = f"{growth_pct:+.1f}%"
                        output_row['formula'] = formula
            
            output_rows.append(output_row)
        
        result_df = pd.DataFrame(output_rows)
        return result_df
    
    def write_output(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Write output CSV file.
        
        Args:
            df: DataFrame to write
            output_path: Path to output file
            
        Raises:
            BudgetCalculationError: If write fails
        """
        # ERROR HANDLING: Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise BudgetCalculationError(
                    f"Failed to create output directory: {e}"
                )
        
        try:
            df.to_csv(output_path, index=False)
        except Exception as e:
            raise BudgetCalculationError(f"Error writing output file: {e}")


def main():
    """Main entry point for the budget growth calculator."""
    parser = argparse.ArgumentParser(
        description="UC-0C: Calculate budget growth metrics for specific ward-category"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name (must match exactly in dataset)"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Category name (must match exactly in dataset)"
    )
    parser.add_argument(
        "--growth-type",
        required=False,
        help="Growth calculation type: 'MoM' (month-over-month) or 'YoY' (year-over-year)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file"
    )
    
    args = parser.parse_args()
    
    try:
        calculator = BudgetGrowthCalculator()
        
        # SKILL: load_dataset
        df, null_report = calculator.load_dataset(args.input)
        
        # SKILL: compute_growth
        result_df = calculator.compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Write output
        calculator.write_output(result_df, args.output)
        
        print(f"✓ Growth calculations complete for {args.ward} / {args.category}", file=sys.stderr)
        print(f"✓ Growth type: {args.growth_type}", file=sys.stderr)
        print(f"✓ Output written to: {args.output}", file=sys.stderr)
        return 0
        
    except BudgetCalculationError as e:
        print(f"✗ Calculation Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
