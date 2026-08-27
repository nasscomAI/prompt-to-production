import argparse
import csv

def classify_complaint(row):
    complaint = row.get("complaint", "").lower()

    if any(k in complaint for k in ["injury","accident","fire","hospital","school"]):
        return "Emergency","Urgent","Safety keyword detected",""
    elif "pothole" in complaint:
        return "Pothole","Normal","Detected pothole keyword",""
    elif "garbage" in complaint:
        return "Garbage","Normal","Detected garbage keyword",""
    elif "water" in complaint:
        return "Water Supply","Normal","Detected water issue",""
    elif "drain" in complaint or "flood" in complaint:
        return "Flooding","Normal","Detected drainage keyword",""
    else:
        return "Other","Normal","No clear keyword","NEEDS_REVIEW"


def batch_classify(input_path,output_path):

    results=[]

    with open(input_path,newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)

        for row in reader:
            cat,priority,reason,flag = classify_complaint(row)

            results.append({
                "complaint_id":row.get("complaint_id",""),
                "category":cat,
                "priority":priority,
                "reason":reason,
                "flag":flag
            })

    with open(output_path,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["complaint_id","category","priority","reason","flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    batch_classify(args.input,args.output)

    print("Done. Results written to",args.output)