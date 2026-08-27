import argparse
import csv

def compute_growth(input_file,ward,category,output):

    rows=[]

    with open(input_file,newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)

        for r in reader:
            if r["ward"]==ward and r["category"]==category:
                rows.append(r)

    rows.sort(key=lambda x:x["period"])

    prev=None
    results=[]

    for r in rows:

        spend=r["actual_spend"]

        if spend=="":
            results.append({
                "period":r["period"],
                "actual_spend":"NULL",
                "growth":"NULL",
                "formula":"NULL spend",
                "flag":"NULL_FLAGGED"
            })
            prev=None
            continue

        spend=float(spend)

        if prev is None:
            growth="N/A"
            formula="No previous value"
        else:
            growth=((spend-prev)/prev)*100
            formula="((current-previous)/previous)*100"

        results.append({
            "period":r["period"],
            "actual_spend":spend,
            "growth":growth,
            "formula":formula,
            "flag":""
        })

        prev=spend

    with open(output,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["period","actual_spend","growth","formula","flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__=="__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument("--input",required=True)
    parser.add_argument("--ward",required=True)
    parser.add_argument("--category",required=True)
    parser.add_argument("--growth-type",required=True)
    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    compute_growth(args.input,args.ward,args.category,args.output)

    print("Growth analysis complete")