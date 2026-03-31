import pandas as pd
import argparse

severity_keywords = ["injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"]

categories = {
    "pothole":"Pothole",
    "flood":"Flooding",
    "streetlight":"Streetlight",
    "garbage":"Waste",
    "waste":"Waste",
    "noise":"Noise",
    "road":"Road Damage",
    "heritage":"Heritage Damage",
    "heat":"Heat Hazard",
    "drain":"Drain Blockage"
}

def classify_complaint(description):
    text = description.lower()

    category = "Other"
    for key in categories:
        if key in text:
            category = categories[key]
            break

    priority = "Standard"
    for word in severity_keywords:
        if word in text:
            priority = "Urgent"

    reason = f"Detected keywords from description: {description[:40]}"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    df = pd.read_csv(input_file)

    categories=[]
    priorities=[]
    reasons=[]
    flags=[]

    for desc in df["description"]:
        c,p,r,f = classify_complaint(desc)
        categories.append(c)
        priorities.append(p)
        reasons.append(r)
        flags.append(f)

    df["category"] = categories
    df["priority"] = priorities
    df["reason"] = reasons
    df["flag"] = flags

    df.to_csv(output_file,index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    batch_classify(args.input,args.output)
