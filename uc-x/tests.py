import subprocess
import sys

def run_test():
    sys.stdout.reconfigure(encoding='utf-8')
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]

    print("Running Tests...\n")
    
    # Run app.py and pass all questions along with 'exit' to cleanly exit
    input_str = "\n".join(questions) + "\nexit\n"
    
    process = subprocess.run(
        ['python', 'app.py'],
        input=input_str,
        text=True,
        capture_output=True,
        encoding='utf-8'
    )
    
    print("--- STDOUT ---")
    print(process.stdout)
    if process.stderr:
        print("--- STDERR ---")
        print(process.stderr)

if __name__ == '__main__':
    run_test()
