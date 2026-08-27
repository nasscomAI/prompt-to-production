import pandas as pd
import argparse
import re

URGENT_KEYWORDS = [
    "injury","child","school","hospital",
    "ambulance","fire","hazard","fell","collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole","potholes"
    ],

    "Flooding": [
        "flood","flooding","waterlogging","water logged","water filled"
    ],

    "Streetlight": [
        "streetlight","street light","light not working","lamp post","street lamp"
    ],

    "Waste": [
        "garbage","waste","trash","rubbish","dump","dumping"
    ],

    "Noise": [
        "noise","loud music","construction noise"
    ],

    "Road Damage": [
        "road damage","broken road","cracked road","road broken"
    ],

    "Heritage Damage": [
        "heritage","historic monument","monument damage"
    ],

    "Heat Hazard": [
        "heat","extreme heat","heat wave"
    ],

    "Drain Blockage": [
        "drain","blocked drain","drain blockage","sewer blocked","clogged drain"
    ]
}


def classify_complaint(description):

    text = str(description).lower()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    matches = []

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                matches.append((cat, word))

    # CATEGORY DECISION
    if len(matches) == 1:
        category, keyword = matches[0]

    elif len(matches) > 1:
        category, keyword = matches[0]
        flag = "NEEDS_REVIEW"

    else:
        keyword = None
        category = "Other"
        flag = "NEEDS_REVIEW"

    # PRIORITY RULE
    for urgent_word in URGENT_KEYWORDS:
        if urgent_word in text:
            priority = "Urgent"
            break

    # REASON
    if keyword:
        reason = f'Keyword "{keyword}" found in description.'
    else:
        reason = "No clear keyword found in description."

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    df = pd.read_csv(input_file)

    results = []

    for _, row in df.iterrows():

        description = row.get("description", "")

        category, priority, reason, flag = classify_complaint(description)

        results.append({
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        })

    pd.DataFrame(results).to_csv(output_file, index=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)
