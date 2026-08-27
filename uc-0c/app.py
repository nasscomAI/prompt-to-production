#!/usr/bin/env python3
"""
UC-0C — Number That Looks Right
Municipal Budget Growth Calculator

This script computes month-over-month or year-over-year growth rates for municipal 
budget data at the ward and category level, following strict data integrity rules.
"""

import pandas as pd
import argparse
import sys
from typing import Tuple, Optional


class BudgetGrowthCalculator:
    """
    Handles municipal budget data loading and growth computation with strict
    adherence to data integrity and granularity requirements.
    """
    
    def __init__(self):
        self.data = None
        self.null_rows = []
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Loads CSV file, validates required columns, and reports null count 
        and specific null rows before returning structured data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            pandas DataFrame with validated structure
            
        Raises:
            SystemExit: If file cannot be read or required columns are missing
        """
        try:
            # Read CSV file
            self.data = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                print(f"ERROR: Missing required columns: {missing_columns}")
                sys.exit(1)
            
            # Find and report null actual_spend values
            null_mask = self.data['actual_spend'].isna() | (self.data['actual_spend'] == '')
            self.null_rows = self.data[null_mask].copy()
            
            print(f"Dataset loaded successfully:")
            print(f"- Total rows: {len(self.data)}")
            print(f"- Null actual_spend values: {len(self.null_rows)}")
            
            if len(self.null_rows) > 0:
                print("\nNull rows identified:")
                for _, row in self.null_rows.iterrows():
                    reason = row['notes'] if pd.notna(row['notes']) and row['notes'].strip() else "No reason provided"
                    print(f"  - {row['period']} · {row['ward']} · {row['category']} · Reason: {reason}")
            
            return self.data
            
        except FileNotFoundError:
            print(f"ERROR: File not found: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to read file: {e}")
            sys.exit(1)
    
    def compute_growth(self, ward: str, category: str, growth_type: str, output_file: str) -> None:
        """
        Computes period-wise growth rates for specified ward and category with 
        explicit formula display.
        
        Args:
            ward: Ward name to filter by
            category: Category name to filter by  
            growth_type: 'MoM' for month-over-month or 'YoY' for year-over-year
            output_file: Path to save the output CSV
        """
        if self.data is None:
            print("ERROR: No data loaded. Call load_dataset first.")
            sys.exit(1)
        
        # Validate growth_type
        if growth_type not in ['MoM', 'YoY']:
            print("ERROR: growth_type must be 'MoM' (month-over-month) or 'YoY' (year-over-year)")
            print("Please specify --growth-type parameter")
            sys.exit(1)
        
        # Filter data for specified ward and category
        filtered_data = self.data[
            (self.data['ward'] == ward) & 
            (self.data['category'] == category)
        ].copy()
        
        if filtered_data.empty:
            available_wards = sorted(self.data['ward'].unique())
            available_categories = sorted(self.data['category'].unique())
            print(f"ERROR: No data found for ward '{ward}' and category '{category}'")
            print(f"Available wards: {available_wards}")
            print(f"Available categories: {available_categories}")
            sys.exit(1)
        
        # Sort by period
        filtered_data = filtered_data.sort_values('period').reset_index(drop=True)
        
        # Prepare output data
        output_rows = []
        
        for i, row in filtered_data.iterrows():
            period = row['period']
            actual_spend = row['actual_spend']
            
            # Handle null values
            if pd.isna(actual_spend) or actual_spend == '':
                reason = row['notes'] if pd.notna(row['notes']) and row['notes'].strip() else "No reason provided"
                output_rows.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': 'NULL',
                    'growth_rate': f'NULL - {reason}',
                    'formula_used': 'Cannot compute - missing data'
                })
                continue
            
            # Convert to float for calculation
            try:
                current_spend = float(actual_spend)
            except (ValueError, TypeError):
                output_rows.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': actual_spend,
                    'growth_rate': 'ERROR - Invalid number format',
                    'formula_used': 'Cannot compute - invalid data'
                })
                continue
            
            # Calculate growth rate
            if growth_type == 'MoM':
                if i == 0:
                    # First period - no previous month
                    output_rows.append({
                        'period': period,
                        'ward': ward,
                        'category': category,
                        'actual_spend': current_spend,
                        'growth_rate': 'N/A (first period)',
                        'formula_used': 'No previous month for comparison'
                    })
                else:
                    # Find previous period data
                    prev_row = filtered_data.iloc[i-1]
                    prev_spend = prev_row['actual_spend']
                    
                    if pd.isna(prev_spend) or prev_spend == '':
                        output_rows.append({
                            'period': period,
                            'ward': ward,
                            'category': category,
                            'actual_spend': current_spend,
                            'growth_rate': 'Cannot compute - previous month NULL',
                            'formula_used': 'Previous period data missing'
                        })
                    else:
                        try:
                            prev_spend_float = float(prev_spend)
                            if prev_spend_float == 0:
                                growth_rate = 'Infinite (previous month was 0)'
                                formula = f'({current_spend} - 0) / 0 * 100'
                            else:
                                growth_rate_pct = ((current_spend - prev_spend_float) / prev_spend_float) * 100
                                growth_rate = f'{growth_rate_pct:+.1f}%'
                                formula = f'({current_spend} - {prev_spend_float}) / {prev_spend_float} * 100'
                            
                            output_rows.append({
                                'period': period,
                                'ward': ward,
                                'category': category,
                                'actual_spend': current_spend,
                                'growth_rate': growth_rate,
                                'formula_used': formula
                            })
                        except (ValueError, TypeError):
                            output_rows.append({
                                'period': period,
                                'ward': ward,
                                'category': category,
                                'actual_spend': current_spend,
                                'growth_rate': 'Cannot compute - invalid previous data',
                                'formula_used': 'Previous period data invalid'
                            })
            
            elif growth_type == 'YoY':
                # For YoY, we need same month from previous year
                current_year, current_month = period.split('-')
                prev_year = str(int(current_year) - 1)
                prev_year_period = f'{prev_year}-{current_month}'
                
                prev_year_data = filtered_data[filtered_data['period'] == prev_year_period]
                
                if prev_year_data.empty:
                    output_rows.append({
                        'period': period,
                        'ward': ward,
                        'category': category,
                        'actual_spend': current_spend,
                        'growth_rate': 'N/A (no previous year data)',
                        'formula_used': f'No data for {prev_year_period}'
                    })
                else:
                    prev_year_spend = prev_year_data.iloc[0]['actual_spend']
                    if pd.isna(prev_year_spend) or prev_year_spend == '':
                        output_rows.append({
                            'period': period,
                            'ward': ward,
                            'category': category,
                            'actual_spend': current_spend,
                            'growth_rate': 'Cannot compute - previous year NULL',
                            'formula_used': f'Data for {prev_year_period} is missing'
                        })
                    else:
                        try:
                            prev_year_spend_float = float(prev_year_spend)
                            if prev_year_spend_float == 0:
                                growth_rate = 'Infinite (previous year was 0)'
                                formula = f'({current_spend} - 0) / 0 * 100'
                            else:
                                growth_rate_pct = ((current_spend - prev_year_spend_float) / prev_year_spend_float) * 100
                                growth_rate = f'{growth_rate_pct:+.1f}%'
                                formula = f'({current_spend} - {prev_year_spend_float}) / {prev_year_spend_float} * 100'
                            
                            output_rows.append({
                                'period': period,
                                'ward': ward,
                                'category': category,
                                'actual_spend': current_spend,
                                'growth_rate': growth_rate,
                                'formula_used': formula
                            })
                        except (ValueError, TypeError):
                            output_rows.append({
                                'period': period,
                                'ward': ward,
                                'category': category,
                                'actual_spend': current_spend,
                                'growth_rate': 'Cannot compute - invalid previous year data',
                                'formula_used': f'Data for {prev_year_period} is invalid'
                            })
        
        # Create output DataFrame and save
        output_df = pd.DataFrame(output_rows)
        output_df.to_csv(output_file, index=False)
        
        print(f"\nGrowth computation completed:")
        print(f"- Ward: {ward}")
        print(f"- Category: {category}")
        print(f"- Growth Type: {growth_type}")
        print(f"- Output saved to: {output_file}")
        print(f"- Periods processed: {len(output_rows)}")


def main():
    """Main entry point for the budget growth calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate municipal budget growth rates at ward and category level'
    )
    parser.add_argument('--input', required=True, help='Path to input CSV file')
    parser.add_argument('--ward', required=True, help='Ward name to analyze')
    parser.add_argument('--category', required=True, help='Category to analyze')
    parser.add_argument('--growth-type', required=True, choices=['MoM', 'YoY'], 
                       help='Growth type: MoM (month-over-month) or YoY (year-over-year)')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Initialize calculator
    calculator = BudgetGrowthCalculator()
    
    # Load dataset
    print("Loading dataset...")
    calculator.load_dataset(args.input)
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for {args.ward} - {args.category}...")
    calculator.compute_growth(args.ward, args.category, args.growth_type, args.output)
    
    print("\nProcess completed successfully!")


if __name__ == '__main__':
    main()