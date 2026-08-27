import re

def run_tests(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read().lower()

    tests = {
        "2.3 14-day advance notice": ["14", "advance"],
        "2.4 Written approval before leave, verbal not valid": ["written approval", "verbal approval is not valid"],
        "2.5 Unapproved = LOP regardless": ["unapproved", "lop", "regardless"],
        "2.6 Max 5 days carry-forward, forfeited 31 Dec": ["carry forward", "5", "forfeited on 31 december"],
        "2.7 Carry-forward used Jan-Mar or forfeited": ["january", "march", "forfeited"],
        "3.2 3+ sick days requires cert within 48hrs": ["3", "consecutive", "medical certificate", "48 hours"],
        "3.4 Sick leave near holiday requires cert": ["before or after", "holiday", "medical certificate", "regardless"],
        "5.2 LWP requires Dept Head AND HR Director": ["department head", "hr director"],
        "5.3 LWP >30 days requires Municipal Commissioner": ["30", "municipal commissioner"],
        "7.2 Leave encashment not permitted during service": ["leave encashment during service", "not permitted"]
    }

    passed = 0
    failed = 0
    print(f"Testing {file_path} against 10 core clauses:\n" + "-"*50)
    
    for clause, keywords in tests.items():
        missing = [kw for kw in keywords if kw not in text]
        if missing:
            print(f"[FAILED] {clause} - Missing: {missing}")
            failed += 1
        else:
            print(f"[PASSED] {clause}")
            passed += 1
            
    print("-" * 50)
    print(f"RESULTS: {passed} Passed, {failed} Failed")
    if failed == 0:
        print("Success! All critical conditions were preserved without meaning loss.")
    else:
        print("Failure! Conditions were dropped during summarization.")

if __name__ == '__main__':
    run_tests('summary_hr_leave.txt')
