import pandas as pd

# Convert all test files to Excel
test_files = ['test_pune', 'test_hyderabad', 'test_kolkata', 'test_ahmedabad']

for filename in test_files:
    csv_path = f'data/city-test-files/{filename}.csv'
    xlsx_path = f'data/city-test-files/{filename}.xlsx'
    
    try:
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False)
        print(f'✓ Created {xlsx_path}')
    except Exception as e:
        print(f'✗ Error converting {filename}: {e}')
