import csv
import argparse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class ComplaintClassifier:

    def __init__(self):

        self.categories = {
            "Pothole": ["pothole", "crater", "hole"],
            "Flooding": ["flood", "waterlogging", "overflow"],
            "Streetlight": ["streetlight", "lamp", "bulb", "dark"],
            "Waste": ["garbage", "trash", "waste", "dump"],
            "Noise": ["noise", "loud", "music", "construction"],
            "Road Damage": ["broken road", "cracked", "pavement"],
            "Heritage Damage": ["heritage", "monument", "statue"],
            "Heat Hazard": ["heat", "sunstroke", "temperature"],
            "Drain Blockage": ["drain", "sewage", "gutter"]
        }

        self.urgent_keywords = [
            "injury",
            "accident",
            "hospital",
            "school",
            "danger",
            "fire"
        ]

    def calculate_confidence(self, keywords):

        if not keywords:
            return 0.0

        score = len(keywords) / 3
        return round(min(score, 1.0), 2)

    def classify(self, text):

        text_lower = text.lower()

        detected_category = "Other"
        matched_keywords = []
        best_match_count = 0

        for category, keywords in self.categories.items():

            matches = [word for word in keywords if word in text_lower]

            if len(matches) > best_match_count:
                best_match_count = len(matches)
                detected_category = category
                matched_keywords = matches

        priority = "Standard"

        severity_matches = [w for w in self.urgent_keywords if w in text_lower]

        if severity_matches:
            priority = "Urgent"

        confidence = self.calculate_confidence(matched_keywords)

        if matched_keywords:
            reason = f"Detected keywords {matched_keywords} suggesting '{detected_category}'."
        else:
            reason = "No clear keywords detected."

        if priority == "Urgent":
            reason += f" Urgency triggered by {severity_matches}."

        flag = ""

        if detected_category == "Other" or confidence < 0.4:
            flag = "NEEDS_REVIEW"

        return {
            "category": detected_category,
            "priority": priority,
            "reason": reason,
            "confidence": confidence,
            "flag": flag
        }


def process_csv(input_file, output_file):

    classifier = ComplaintClassifier()

    results = []

    with open(input_file, "r", encoding="utf-8") as infile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + [
            "category",
            "priority",
            "reason",
            "confidence",
            "flag",
            "processed_time"
        ]

        for row in reader:

            description = row.get("description", "")

            prediction = classifier.classify(description)

            row.update(prediction)

            row["processed_time"] = datetime.now().isoformat()

            results.append(row)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        writer.writerows(results)

    logging.info(f"Processed {len(results)} complaints")
    logging.info(f"Results saved to {output_file}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Complaint classifier")

    parser.add_argument("--input", required=True)

    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_csv(args.input, args.output)
