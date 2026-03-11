import argparse

def respond(complaint):

    complaint = complaint.lower()

    if "flood" in complaint or "drain" in complaint or "water" in complaint:
        return "Category: Drainage | Action: Municipal drainage team will inspect."

    elif "pothole" in complaint or "road" in complaint:
        return "Category: Roads | Action: Road repair department notified."

    elif "garbage" in complaint or "waste" in complaint:
        return "Category: Sanitation | Action: Waste collection team assigned."

    elif "mosquito" in complaint or "dengue" in complaint:
        return "Category: Health | Action: Public health inspection team notified."

    else:
        return "Category: General | Action: Complaint recorded for review."


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True, help="Complaint description")

    args = parser.parse_args()

    result = respond(args.text)

    print(result)


if __name__ == "__main__":
    main()