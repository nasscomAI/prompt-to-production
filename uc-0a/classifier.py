import csv

# Function to classify complaints
def classify_complaint(text):
    text = text.lower()

    # Sanitation issues
    if any(word in text for word in ["garbage", "waste", "sewage", "mosquito"]):
        return {"category": "Sanitation", "priority": "Medium"}

    # Water / flooding issues
    elif any(word in text for word in ["flood", "drain", "water", "blocked drain"]):
        return {"category": "Water", "priority": "High"}

    # Road issues
    elif any(word in text for word in ["pothole", "road", "pavement"]):
        return {"category": "Roads", "priority": "High"}

    # Electricity issues
    elif any(word in text for word in ["electric", "power", "wire", "streetlight"]):
        return {"category": "Electricity", "priority": "High"}

    # If nothing matches
    else:
        return {"category": "Other", "priority": "Low"}


# Process CSV file
def process_file(input_file, output_file):
    results = []

    with open(input_file, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            complaint_text = row["description"]

            result = classify_complaint(complaint_text)

            results.append({
                "complaint_id": row["complaint_id"],
                "category": result["category"],
                "priority": result["priority"]
            })

    with open(output_file, "w", newline="") as file:
        fieldnames = ["complaint_id", "category", "priority"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


# Run program
if __name__ == "__main__":
    process_file(
        "data/city-test-files/test_hyderabad.csv",
        "results_hyderabad.csv"
    )