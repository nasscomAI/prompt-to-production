import pandas as pd

# List of your CSV files
files = [
    "data/city-test-files/test_pune.csv",
    "data/city-test-files/test_hyderabad.csv",
    "data/city-test-files/test_kolkata.csv",
    "data/city-test-files/test_ahmedabad.csv"
]

# Loop through each file and display first 5 rows
for file in files:
    try:
        df = pd.read_csv(file)
        print(f"\n--- {file} ---")
        print(df.head())
    except FileNotFoundError:
        print(f"File not found: {file}")
