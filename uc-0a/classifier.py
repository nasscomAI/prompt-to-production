import csv
import os

def classify_complaint(text):
    text = text.lower()
    if "pothole" in text or "road" in text:
        return "Roads"
    elif "water" in text or "leak" in text or "sewage" in text:
        return "Water"
    elif "power" in text or "electricity" in text:
        return "Electricity"
    else:
        return "General"

def main():
    # Sample data to simulate the workshop lab
    complaints = [
        "Huge pothole on MG Road",
        "Water leakage in Indiranagar",
        "Street lights are not working",
        "General inquiry about tax"
    ]
    
    output_file = "results_bengaluru.csv"
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Complaint", "Category"])
        for c in complaints:
            category = classify_complaint(c)
            writer.writerow([c, category])
            
    print(f"Success! {output_file} has been generated.")

if __name__ == "__main__":
    main()