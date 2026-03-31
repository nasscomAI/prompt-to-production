import argparse
import pandas as pd


# 🔹 Simple classification logic
def classify(text):
    text = str(text).lower()

    if "water" in text:
        return "Water Issue"
    elif "road" in text:
        return "Road Issue"
    elif "garbage" in text or "waste" in text:
        return "Sanitation"
    elif "electric" in text or "power" in text:
        return "Electricity"
    else:
        return "Other"


# 🔹 Main function to process CSV
def batch_classify(input_file, output_file):
    print("📥 Reading file:", input_file)

    # Read input CSV
    df = pd.read_csv(input_file)

    print("✅ File loaded successfully")

    # Take first column as complaint text
    column_name = df.columns[0]
    print("📝 Using column:", column_name)

    # Apply classification
    df["category"] = df[column_name].apply(classify)

    # Save output CSV
    df.to_csv(output_file, index=False)

    print("💾 File saved successfully at:", output_file)


# 🔹 Command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    batch_classify(args.input, args.output)