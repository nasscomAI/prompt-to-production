import os
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

def run_test():
    p = subprocess.Popen(['python', 'app.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    input_str = '\n'.join(questions) + '\nexit\n'
    stdout, stderr = p.communicate(input=input_str)
    
    print("STDOUT:")
    print(stdout)
    if stderr:
        print("STDERR:")
        print(stderr)



if __name__ == "__main__":
    run_test()
