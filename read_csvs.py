import pandas as pd
import glob

# Find all CSV files in the folder
files = glob.glob("data/city-test-files/*.csv")

# Read and combine them into one DataFrame
all_data = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

# Show summary
print("\n✅ Combined dataset created!")
print(f"Total rows: {len(all_data)}")
print(f"Columns: {list(all_data.columns)}")

# Show first 10 rows
print("\n--- Preview of combined data ---")
print(all_data.head(10))

# Save combined dataset to a new CSV file
all_data.to_csv("all_cities.csv", index=False)
print("\n💾 Saved combined dataset as all_cities.csv")