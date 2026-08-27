import argparse

def route_request(request):
    if "complaint" in request.lower():
        return "Complaint Classifier Agent"
    elif "summary" in request.lower():
        return "Document Summarization Agent"
    elif "policy" in request.lower():
        return "Policy QA Agent"
    else:
        return "Unknown request type"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=str, required=True, help="User request")
    args = parser.parse_args()

    agent = route_request(args.request)
    print("Request routed to:", agent)

if __name__ == "__main__":
    main()