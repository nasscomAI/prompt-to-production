"""
UC-X — City Assistant
"""

import argparse


def handle_complaint():
    print("Complaint classifier module (UC-0A) would run here")


def handle_policy():
    print("Policy Q&A module (UC-0B) would run here")


def handle_budget():
    print("Ward budget lookup module (UC-0C) would run here")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--task", required=True)

    args = parser.parse_args()

    if args.task == "complaint":
        handle_complaint()

    elif args.task == "policy":
        handle_policy()

    elif args.task == "budget":
        handle_budget()

    else:
        print("Unknown task")


if __name__ == "__main__":
    main()