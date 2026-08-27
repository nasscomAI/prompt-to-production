"""UC-X smoke tests for README validation questions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]

EXPECTATIONS = {
    QUESTIONS[0]: [
        "maximum of 5 unused annual leave",
        "policy_hr_leave.txt section 2.6",
    ],
    QUESTIONS[1]: [
        "must not install software",
        "policy_it_acceptable_use.txt section 2.3",
    ],
    QUESTIONS[2]: [
        "one-time home office equipment allowance of Rs 8,000",
        "policy_finance_reimbursement.txt section 3.1",
    ],
    QUESTIONS[3]: [
        "access CMC email and the CMC employee self-service portal only",
        "policy_it_acceptable_use.txt section 3.1",
    ],
    QUESTIONS[4]: [
        "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.",
    ],
    QUESTIONS[5]: [
        "DA and meal receipts cannot be claimed simultaneously",
        "policy_finance_reimbursement.txt section 2.6",
    ],
    QUESTIONS[6]: [
        "Department Head and the HR Director",
        "policy_hr_leave.txt section 5.2",
    ],
}


def run_cli() -> list[str]:
    ucx_dir = Path(__file__).resolve().parent
    payload = "\n".join(QUESTIONS + ["exit", ""])  # final blank keeps stdin clean
    proc = subprocess.run(
        [sys.executable, "app.py"],
        cwd=ucx_dir,
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"app.py exited with code {proc.returncode}\nSTDERR:\n{proc.stderr}")

    answers: list[str] = []
    for line in proc.stdout.splitlines():
        if "Answer:" in line:
            answers.append(line.split("Answer:", 1)[1].strip())
    return answers


def main() -> int:
    answers = run_cli()
    if len(answers) != len(QUESTIONS):
        print(f"FAIL: expected {len(QUESTIONS)} answers, got {len(answers)}")
        return 1

    failures: list[str] = []
    for idx, question in enumerate(QUESTIONS):
        answer = answers[idx]
        required_snippets = EXPECTATIONS[question]
        for snippet in required_snippets:
            if snippet not in answer:
                failures.append(
                    f"Q{idx+1} failed: missing snippet '{snippet}' in answer '{answer}'"
                )

        if "while not explicitly covered" in answer.lower():
            failures.append(f"Q{idx+1} failed: hedging phrase found")

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS: all 7 UC-X smoke checks succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
