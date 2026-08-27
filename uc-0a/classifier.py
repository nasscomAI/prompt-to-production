import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(text: str) -> dict:
    """Classifies a complaint text into category, priority, reason, and flag."""
    if not text or not isinstance(text, str):
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint text was empty or invalid.",
            "flag": "NEEDS_REVIEW"
        }
        
    text_lower = text.lower()
    
    # Priority classification
    if any(kw in text_lower for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # Category matching
    detected_cats = []
    if "pothole" in text_lower: detected_cats.append("Pothole")
    if "flood" in text_lower or "water logging" in text_lower: detected_cats.append("Flooding")
    if "light" in text_lower or "lamp" in text_lower: detected_cats.append("Streetlight")
    if "waste" in text_lower or "garbage" in text_lower or "trash" in text_lower: detected_cats.append("Waste")
    if "noise" in text_lower or "loud" in text_lower: detected_cats.append("Noise")
    if "road" in text_lower and "pothole" not in text_lower: detected_cats.append("Road Damage")
    if "heritage" in text_lower or "monument" in text_lower: detected_cats.append("Heritage Damage")
    if "heat" in text_lower or "temperature" in text_lower: detected_cats.append("Heat Hazard")
    if "drain" in text_lower or "block" in text_lower: detected_cats.append("Drain Blockage")

    # Flag assignment
    if not detected_cats:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(detected_cats) > 1:
        category = detected_cats[0]
        flag = "NEEDS_REVIEW"
    else:
        category = detected_cats[0]
        flag = ""

    # Generate a single-sentence reason using words from the text
    words = [w for w in text.split() if len(w) > 3]
    if words:
        sample_words = ", ".join(words[:2])
        reason = f"Classified based on words from complaint like '{sample_words}'."
    else:
        reason = "Classified based on general text context."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """Reads input CSV, applies classification, and writes to output CSV."""
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
         
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        try:
            headers = next(reader)
        except StopIteration:
            return  # Empty file
            
        desc_idx = 0
        if "description" in headers:
            desc_idx = headers.index("description")
        elif "text" in headers:
            desc_idx = headers.index("text")
        elif "complaint" in headers:
            desc_idx = headers.index("complaint")
            
        # Write output columns exactly as requested
        writer.writerow(["category", "priority", "reason", "flag"])
        
        for row in reader:
            if not row:
                continue
                
            text = row[desc_idx] if len(row) > desc_idx else " ".join(row)
            result = classify_complaint(text)
            
            writer.writerow([
                result["category"],
                result["priority"],
                result["reason"],
                result["flag"]
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done processing. Results written to {args.output}")
