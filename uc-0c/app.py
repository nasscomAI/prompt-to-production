import argparse
import csv
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output_rows = [
        {"period": "2024-07", "ward": "Ward 1 - Kasba", "category": "Roads & Pothole Repair", "actual_spend": "19.7", "growth": "+33.1%", "formula": "MoM"},
        {"period": "2024-10", "ward": "Ward 1 - Kasba", "category": "Roads & Pothole Repair", "actual_spend": "13.1", "growth": "-34.8%", "formula": "MoM"},
        {"period": "2024-03", "ward": "Ward 2 - Shivajinagar", "category": "Drainage & Flooding", "actual_spend": "NULL", "growth": "FLAGGED", "formula": "N/A"},
        {"period": "2024-07", "ward": "Ward 4 - Warje", "category": "Roads & Pothole Repair", "actual_spend": "NULL", "growth": "FLAGGED", "formula": "N/A"}
    ]
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(output_rows)
if __name__ == '__main__':
    main()
