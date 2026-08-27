import pandas as pd
import os
import re

# folder path
DATA_FOLDER = "data/city-test-files"

# get all csv files
files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

print("Files found:", files)

# keyword rules
def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", str(text).lower())

def classify(text):
    text = clean_text(text)

    # category
    if "water" in text:
        category = "water"
    elif "road" in text:
        category = "road"
    elif "garbage" in text:
        category = "garbage"
    else:
        category = "other"

    # severity
    if any(word in text for word in ["urgent", "hospital", "accident", "injury"]):
        severity = "high"
    elif "delay" in text:
        severity = "medium"
    else:
        severity = "low"

    return pd.Series([category, severity])


# process each file
for file in files:
    input_path = os.path.join(DATA_FOLDER, file)
    df = pd.read_csv(input_path)

    print(f"\n🔍 Processing: {file}")
    print("Columns:", df.columns)

    # auto detect column
    text_column = None
    for col in df.columns:
        if "complaint" in col.lower() or "text" in col.lower():
            text_column = col
            break

    if text_column is None:
        print(f"Skipping {file} (no complaint column found)")
        continue

    # apply classification
    df[["category", "severity"]] = df[text_column].apply(classify)

    # output file name
    city_name = file.replace("test_", "").replace(".csv", "")
    output_file = f"results_{city_name}.csv"

    df.to_csv(output_file, index=False)

    print(f"Generated: {output_file}")

print("\nAll files processed successfully!")
