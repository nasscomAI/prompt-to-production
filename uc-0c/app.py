"""
UC-0C app.py — Budget Growth Calculator with Null Handling & Granular Output
Calculates per-ward, per-category growth rates with formula preservation and null flagging.
Core failure modes: Wrong aggregation level · Silent null handling · Formula assumption
"""
import argparse
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class BudgetDataLoader:
    """Loads and validates budget CSV data."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: Optional[pd.DataFrame] = None
        self.null_rows: List[Dict] = []

    def load(self) -> Tuple[pd.DataFrame, List[Dict]]:
        """Load CSV, validate columns, flag nulls."""
        try:
            self.data = pd.read_csv(self.filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset not found: {self.filepath}")

        # Validate required columns
        required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        missing = set(required_cols) - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Identify null rows in actual_spend
        null_mask = self.data['actual_spend'].isna()
        self.null_rows = self.data[null_mask].to_dict('records')

        return self.data, self.null_rows


class GrowthCalculator:
    """Computes growth rates with formula preservation."""

    def __init__(self, data: pd.DataFrame, null_rows: List[Dict]):
        self.data = data
        self.null_rows = null_rows
        self.data['period'] = pd.to_datetime(self.data['period'])

    def validate_parameters(self, ward: str, category: str, growth_type: str) -> None:
        """Validate input parameters."""
        if growth_type not in ['MoM', 'YoY']:
            raise ValueError(f"Invalid growth_type: {growth_type}. Must be 'MoM' or 'YoY'")

        valid_wards = self.data['ward'].unique()
        if ward not in valid_wards:
            raise ValueError(f"Ward '{ward}' not found. Valid wards: {list(valid_wards)}")

        valid_categories = self.data['category'].unique()
        if category not in valid_categories:
            raise ValueError(f"Category '{category}' not found. Valid categories: {list(valid_categories)}")

    def compute_growth(self, ward: str, category: str, growth_type: str) -> pd.DataFrame:
        """
        Compute growth for specific ward & category (NO cross-ward/category aggregation).
        Returns table with period, actual_spend, growth %, and formula.
        """
        self.validate_parameters(ward, category, growth_type)

        # Filter to specific ward and category
        filtered = self.data[
            (self.data['ward'] == ward) &
            (self.data['category'] == category)
        ].copy().sort_values('period')

        if filtered.empty:
            raise ValueError(f"No data for {ward} / {category}")

        results = []

        for idx, row in filtered.iterrows():
            period = row['period'].strftime('%Y-%m')
            actual_spend = row['actual_spend']
            is_null = pd.isna(actual_spend)

            # Check if this row is in the null list
            null_reason = ""
            for nr in self.null_rows:
                if (nr['period'] == period and
                    nr['ward'] == ward and
                    nr['category'] == category):
                    null_reason = nr.get('notes', 'Unspecified')
                    break

            if is_null:
                results.append({
                    'period': period,
                    'actual_spend': None,
                    'growth_percent': None,
                    'formula': 'N/A - NULL VALUE',
                    'null_reason': null_reason,
                    'is_null': True
                })
            else:
                # Compute growth based on type
                if growth_type == 'MoM':
                    # Month-over-Month: current month vs previous month
                    prev_row = filtered[filtered['period'] < row['period']].tail(1)
                    if prev_row.empty:
                        # First month - no previous data
                        growth_percent = None
                        formula = 'N/A - First Month (no prior month)'
                    else:
                        prev_spend = prev_row.iloc[0]['actual_spend']
                        if pd.isna(prev_spend):
                            growth_percent = None
                            formula = 'N/A - Previous month NULL'
                        else:
                            growth_percent = ((actual_spend - prev_spend) / prev_spend) * 100
                            formula = f'({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} × 100'
                else:  # YoY
                    # Year-over-Year: current period vs 12 months ago
                    prev_year = row['period'].replace(year=row['period'].year - 1)
                    prev_row = filtered[filtered['period'] == prev_year]
                    if prev_row.empty:
                        growth_percent = None
                        formula = 'N/A - No prior year data'
                    else:
                        prev_spend = prev_row.iloc[0]['actual_spend']
                        if pd.isna(prev_spend):
                            growth_percent = None
                            formula = 'N/A - Prior year NULL'
                        else:
                            growth_percent = ((actual_spend - prev_spend) / prev_spend) * 100
                            formula = f'({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} × 100'

                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_percent': growth_percent,
                    'formula': formula,
                    'null_reason': '',
                    'is_null': False
                })

        return pd.DataFrame(results)


def generate_report(data: pd.DataFrame, null_rows: List[Dict], ward: str, category: str,
                   growth_type: str) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 80)
    lines.append("BUDGET GROWTH CALCULATION REPORT")
    lines.append("=" * 80)
    lines.append(f"\nFilter: Ward = '{ward}' | Category = '{category}' | Growth Type = {growth_type}")
    lines.append(f"Generated: Per-ward, Per-category (NO cross-aggregation)")
    lines.append(f"\nTotal null rows in dataset: {len(null_rows)}")

    if null_rows:
        lines.append("\nNULL ROWS FLAGGED (before computation):")
        for nr in null_rows:
            lines.append(f"  • {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr.get('notes', 'Unspecified')}")

    lines.append("\n" + "-" * 80)
    lines.append("GROWTH CALCULATION TABLE")
    lines.append("-" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0C: Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Input CSV filepath")
    parser.add_argument("--ward", required=True, help="Target ward (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Target category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'],
                       help="Growth calculation type (MoM=Month-over-Month, YoY=Year-over-Year)")
    parser.add_argument("--output", required=True, help="Output CSV filepath")

    args = parser.parse_args()

    try:
        # Load data
        loader = BudgetDataLoader(args.input)
        data, null_rows = loader.load()
        print(f"✓ Loaded {len(data)} rows from {args.input}")
        print(f"✓ Identified {len(null_rows)} null rows in actual_spend")

        # Calculate growth
        calculator = GrowthCalculator(data, null_rows)
        growth_df = calculator.compute_growth(args.ward, args.category, args.growth_type)

        # Generate report
        report = generate_report(data, null_rows, args.ward, args.category, args.growth_type)
        print(report)
        print(growth_df.to_string(index=False))

        # Write output CSV
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        growth_df.to_csv(output_path, index=False)
        print(f"\n✓ Output written to {output_path}")

        # Validation
        null_in_output = growth_df[growth_df['is_null']].shape[0]
        if null_in_output > 0:
            print(f"⚠ {null_in_output} null rows flagged in output (not computed)")

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"✗ ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
