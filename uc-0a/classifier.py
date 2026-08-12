import argparse
import csv

SEVERITY = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_MAP = {
    "pothole": "Pothole",
    "flood": "Flooding",
    "water": "Flooding",
    "streetlight": "Streetlight",
    "light": "Streetlight",
    "garbage": "Waste",
    "waste": "Waste",
    "trash": "Waste",
    "noise": "Noise",
    "road": "Road Damage",
    "crack": "Road Damage",
    "heritage": "Heritage Damage",
    "monument": "Heritage Damage",
    "heat": "Heat Hazard",
    "drain": "Drain Blockage",
    "sewage": "Drain Blockage",
}

def classify_complaint(row):

    text = row.get("description","").lower()

    category = "Other"

    flag = ""

    for k,v in CATEGORY_MAP.items():
        if k in text:
            category=v
            break

    priority="Standard"

    if any(word in text for word in SEVERITY):
        priority="Urgent"

    if category=="Other":
        flag="NEEDS_REVIEW"

    reason=f'Classified because complaint mentions "{text[:40]}".'

    return {
        "complaint_id":row.get("complaint_id",""),
        "category":category,
        "priority":priority,
        "reason":reason,
        "flag":flag
    }


def batch_classify(input_path,output_path):

    with open(input_path,newline='',encoding="utf-8") as infile:

        reader=csv.DictReader(infile)

        rows=[]

        for row in reader:
            try:
                rows.append(classify_complaint(row))
            except Exception:
                rows.append({
                    "complaint_id":row.get("complaint_id",""),
                    "category":"Other",
                    "priority":"Low",
                    "reason":"Processing failed.",
                    "flag":"NEEDS_REVIEW"
                })

    with open(output_path,"w",newline='',encoding="utf-8") as outfile:

        fields=["complaint_id","category","priority","reason","flag"]

        writer=csv.DictWriter(outfile,fieldnames=fields)

        writer.writeheader()

        writer.writerows(rows)


if __name__=="__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument("--input",required=True)

    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    batch_classify(args.input,args.output)

    print("Done")
