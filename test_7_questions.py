import subprocess

questions = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

for q in questions:
    p = subprocess.run(["python3", "app.py"], input=f"{q}\nexit\n", cwd="uc-x", text=True, capture_output=True)
    if p.returncode != 0:
        print(f"Q: {q}\nError: app.py exited with code {p.returncode}\n{p.stderr}")
        continue
    try:
        out = p.stdout.split("Answer:")[1].strip().split("\n")[0]
    except IndexError:
        out = "ERROR: Could not parse answer from output."
    print(f"Q: {q}")
    print(f"A: {out}")
    print("-" * 50)
