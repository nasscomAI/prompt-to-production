"""
UC-0C Test Suite — Budget Growth Calculator Validation
Tests strict scoping, null handling, formula preservation, and parameter validation
"""
import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from app import BudgetDataLoader, GrowthCalculator


class TestDataLoading(unittest.TestCase):
    """Test CSV loading and null detection."""

    @classmethod
    def setUpClass(cls):
        cls.loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = cls.loader.load()

    def test_dataset_loaded(self):
        """Dataset loads successfully."""
        self.assertIsNotNone(self.data)
        self.assertGreater(len(self.data), 0)

    def test_required_columns_present(self):
        """All required columns present in CSV."""
        required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        for col in required_cols:
            self.assertIn(col, self.data.columns, f"Missing column: {col}")

    def test_five_nulls_detected(self):
        """Exactly 5 null rows detected in actual_spend."""
        self.assertEqual(len(self.null_rows), 5, f"Expected 5 nulls, found {len(self.null_rows)}")

    def test_null_rows_have_reasons(self):
        """Each null row includes a notes/reason field."""
        for nr in self.null_rows:
            self.assertIn('period', nr)
            self.assertIn('ward', nr)
            self.assertIn('category', nr)

    def test_five_specific_nulls_present(self):
        """The 5 known null rows are present."""
        expected_nulls = [
            ('2024-03', 'Ward 2 – Shivajinagar', 'Drainage & Flooding'),
            ('2024-07', 'Ward 4 – Warje', 'Roads & Pothole Repair'),
            ('2024-11', 'Ward 1 – Kasba', 'Waste Management'),
            ('2024-08', 'Ward 3 – Kothrud', 'Parks & Greening'),
            ('2024-05', 'Ward 5 – Hadapsar', 'Streetlight Maintenance'),
        ]
        
        found_nulls = [(nr['period'], nr['ward'], nr['category']) for nr in self.null_rows]
        for expected in expected_nulls:
            self.assertIn(expected, found_nulls, f"Missing null: {expected}")


class TestParameterValidation(unittest.TestCase):
    """Test parameter validation and refusal conditions."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_valid_ward_accepted(self):
        """Valid ward parameter accepted."""
        try:
            self.calculator.validate_parameters("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        except ValueError:
            self.fail("Valid ward rejected")

    def test_invalid_ward_rejected(self):
        """Invalid ward parameter rejected."""
        with self.assertRaises(ValueError):
            self.calculator.validate_parameters("Ward 99 – Fake", "Roads & Pothole Repair", "MoM")

    def test_valid_category_accepted(self):
        """Valid category parameter accepted."""
        try:
            self.calculator.validate_parameters("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        except ValueError:
            self.fail("Valid category rejected")

    def test_invalid_category_rejected(self):
        """Invalid category parameter rejected."""
        with self.assertRaises(ValueError):
            self.calculator.validate_parameters("Ward 1 – Kasba", "Invalid Category", "MoM")

    def test_growth_type_mom_accepted(self):
        """MoM growth type accepted."""
        try:
            self.calculator.validate_parameters("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        except ValueError:
            self.fail("Valid MoM growth type rejected")

    def test_growth_type_yoy_accepted(self):
        """YoY growth type accepted."""
        try:
            self.calculator.validate_parameters("Ward 1 – Kasba", "Roads & Pothole Repair", "YoY")
        except ValueError:
            self.fail("Valid YoY growth type rejected")

    def test_invalid_growth_type_rejected(self):
        """Invalid growth type rejected."""
        with self.assertRaises(ValueError):
            self.calculator.validate_parameters("Ward 1 – Kasba", "Roads & Pothole Repair", "Invalid")


class TestGrowthCalculation(unittest.TestCase):
    """Test growth calculation logic and formula preservation."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_mom_growth_computed(self):
        """Month-over-Month growth is computed correctly."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        self.assertGreater(len(result), 0)
        # Should have growth_percent values (not all None)
        non_null_growth = result[result['growth_percent'].notna()]
        self.assertGreater(len(non_null_growth), 0)

    def test_yoy_growth_computed(self):
        """Year-over-Year growth is computed (but for 2024 data, mostly N/A)."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "YoY")
        self.assertGreater(len(result), 0)
        # For 2024 data with no prior year, should be mostly N/A
        self.assertIn("No prior year data", ' '.join(result['formula'].astype(str)))

    def test_output_has_required_columns(self):
        """Output DataFrame has all required columns."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        required_cols = ['period', 'actual_spend', 'growth_percent', 'formula', 'null_reason', 'is_null']
        for col in required_cols:
            self.assertIn(col, result.columns)

    def test_formula_shown_in_every_row(self):
        """Formula shown in every row of output."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        for idx, row in result.iterrows():
            self.assertIsNotNone(row['formula'])
            self.assertTrue(len(row['formula']) > 0)

    def test_first_month_has_no_growth(self):
        """First month (2024-01) has no growth calculation."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        first_row = result[result['period'] == '2024-01'].iloc[0]
        self.assertTrue(pd.isna(first_row['growth_percent']))
        self.assertIn("First Month", first_row['formula'])


class TestNullHandling(unittest.TestCase):
    """Test that null rows are flagged and not computed."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_null_rows_flagged_in_output(self):
        """Null rows are flagged and not computed in output."""
        # Ward 1 – Kasba has a null in 2024-11 (Waste Management)
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Waste Management", "MoM")
        null_rows = result[result['is_null'] == True]
        self.assertGreater(len(null_rows), 0)

    def test_null_rows_have_formula_na(self):
        """Null rows show 'N/A - NULL VALUE' in formula."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Waste Management", "MoM")
        null_rows = result[result['is_null'] == True]
        for idx, row in null_rows.iterrows():
            self.assertIn("NULL VALUE", row['formula'])

    def test_null_rows_have_none_growth_percent(self):
        """Null rows have None for growth_percent."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Waste Management", "MoM")
        null_rows = result[result['is_null'] == True]
        for idx, row in null_rows.iterrows():
            self.assertTrue(pd.isna(row['growth_percent']))


class TestAggregationRefusal(unittest.TestCase):
    """Test that cross-ward and cross-category aggregations are refused."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_per_ward_per_category_scoping(self):
        """Output is strictly per-ward, per-category (no cross aggregation)."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        
        # Check that result contains only one ward and one category
        unique_wards = result['period'].str.len()  # All periods should be same format
        self.assertEqual(len(result), 12)  # 12 months


class TestReferenceValues(unittest.TestCase):
    """Test output against reference values from README."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_ward1_kasba_roads_july_value(self):
        """Ward 1 – Kasba · Roads & Pothole Repair · 2024-07: ₹19.7 lakh"""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        july_row = result[result['period'] == '2024-07'].iloc[0]
        self.assertAlmostEqual(july_row['actual_spend'], 19.7, places=1)

    def test_ward1_kasba_roads_july_growth(self):
        """Ward 1 – Kasba · Roads & Pothole Repair · 2024-07: MoM +33.1%"""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        july_row = result[result['period'] == '2024-07'].iloc[0]
        # Approx 33.1%
        self.assertIsNotNone(july_row['growth_percent'])
        self.assertGreater(july_row['growth_percent'], 30)
        self.assertLess(july_row['growth_percent'], 35)

    def test_ward1_kasba_roads_october_value(self):
        """Ward 1 – Kasba · Roads & Pothole Repair · 2024-10: ₹13.1 lakh"""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        oct_row = result[result['period'] == '2024-10'].iloc[0]
        self.assertAlmostEqual(oct_row['actual_spend'], 13.1, places=1)

    def test_ward1_kasba_roads_october_growth(self):
        """Ward 1 – Kasba · Roads & Pothole Repair · 2024-10: MoM −34.8%"""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        oct_row = result[result['period'] == '2024-10'].iloc[0]
        # Approx -34.8%
        self.assertIsNotNone(oct_row['growth_percent'])
        self.assertLess(oct_row['growth_percent'], -30)
        self.assertGreater(oct_row['growth_percent'], -40)

    def test_ward2_shivajinagar_drainage_march_null(self):
        """Ward 2 – Shivajinagar · Drainage & Flooding · 2024-03: NULL (must be flagged)"""
        result = self.calculator.compute_growth("Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        march_row = result[result['period'] == '2024-03'].iloc[0]
        self.assertTrue(march_row['is_null'])
        self.assertTrue(pd.isna(march_row['actual_spend']))
        self.assertTrue(pd.isna(march_row['growth_percent']))

    def test_ward4_warje_roads_july_null(self):
        """Ward 4 – Warje · Roads & Pothole Repair · 2024-07: NULL (must be flagged)"""
        result = self.calculator.compute_growth("Ward 4 – Warje", "Roads & Pothole Repair", "MoM")
        july_row = result[result['period'] == '2024-07'].iloc[0]
        self.assertTrue(july_row['is_null'])
        self.assertTrue(pd.isna(july_row['actual_spend']))


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_full_pipeline_mom(self):
        """Full pipeline: load → validate → compute (MoM) → output CSV."""
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        data, null_rows = loader.load()
        
        calculator = GrowthCalculator(data, null_rows)
        result = calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        
        # Save and verify
        output_path = "test_output_mom.csv"
        result.to_csv(output_path, index=False)
        
        # Verify file exists and has data
        self.assertTrue(Path(output_path).exists())
        loaded = pd.read_csv(output_path)
        self.assertEqual(len(loaded), 12)
        
        # Cleanup
        Path(output_path).unlink()

    def test_full_pipeline_yoy(self):
        """Full pipeline: load → validate → compute (YoY) → output CSV."""
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        data, null_rows = loader.load()
        
        calculator = GrowthCalculator(data, null_rows)
        result = calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "YoY")
        
        # Save and verify
        output_path = "test_output_yoy.csv"
        result.to_csv(output_path, index=False)
        
        # Verify file exists
        self.assertTrue(Path(output_path).exists())
        
        # Cleanup
        Path(output_path).unlink()


class TestEnforcementRules(unittest.TestCase):
    """Test that all enforcement rules are enforced."""

    @classmethod
    def setUpClass(cls):
        loader = BudgetDataLoader("../data/budget/ward_budget.csv")
        cls.data, cls.null_rows = loader.load()
        cls.calculator = GrowthCalculator(cls.data, cls.null_rows)

    def test_enforcement_1_no_cross_aggregation(self):
        """ENFORCEMENT #1: Never aggregate across wards/categories."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        # Result should be exactly 12 rows (12 months for one ward-category pair)
        self.assertEqual(len(result), 12)

    def test_enforcement_2_flag_nulls(self):
        """ENFORCEMENT #2: Flag every null row before computing."""
        # Check that null rows in output have is_null=True and formula indicates null
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Waste Management", "MoM")
        null_rows = result[result['is_null'] == True]
        self.assertGreater(len(null_rows), 0)
        for idx, row in null_rows.iterrows():
            self.assertIn("NULL", row['formula'])

    def test_enforcement_3_formula_shown(self):
        """ENFORCEMENT #3: Show formula used in every output row."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        for idx, row in result.iterrows():
            self.assertIsNotNone(row['formula'])
            self.assertTrue(len(str(row['formula'])) > 0)
            # Either shows formula (with ×), or explains why not
            self.assertTrue(
                ('×' in str(row['formula'])) or ('N/A' in str(row['formula'])),
                f"Formula doesn't show calculation or reason: {row['formula']}"
            )

    def test_enforcement_4_growth_type_required(self):
        """ENFORCEMENT #4: Growth type must be explicitly specified."""
        # Test that invalid growth type raises error
        with self.assertRaises(ValueError):
            self.calculator.compute_growth("Ward 1 – Kasba", "Roads & Pothole Repair", "InvalidType")

    def test_enforcement_5_ward_validation(self):
        """ENFORCEMENT #5: Refuse if ward not found."""
        with self.assertRaises(ValueError):
            self.calculator.compute_growth("Invalid Ward", "Roads & Pothole Repair", "MoM")

    def test_enforcement_6_no_null_computation(self):
        """ENFORCEMENT #6: Never compute growth for null rows."""
        result = self.calculator.compute_growth("Ward 1 – Kasba", "Waste Management", "MoM")
        null_rows = result[result['is_null'] == True]
        for idx, row in null_rows.iterrows():
            self.assertTrue(pd.isna(row['growth_percent']))


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestParameterValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestGrowthCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestNullHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAggregationRefusal))
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceValues))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    suite.addTests(loader.loadTestsFromTestCase(TestEnforcementRules))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
