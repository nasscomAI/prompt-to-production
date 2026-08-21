# Assignment Guide

**Nasscom AI-Code Sarathi · prompt-to-production**

This guide walks you through completing the workshop assignment from start to finish.
Follow every step in order. Do not skip sections.

---

## Contents

1. [What You Need](#1-what-you-need)
2. [Fork the Repository](#2-fork-the-repository)
3. [Clone to Your Computer](#3-clone-to-your-computer)
4. [Create Your Branch](#4-create-your-branch)
5. [How the Assignment Works](#5-how-the-assignment-works)
6. [UC-0A — The Model (Done With Your Facilitator)](#6-uc-0a--the-model-done-with-your-facilitator)
7. [Choose Your Use Case](#7-choose-your-use-case)
8. [Step 1 — Read the UC README](#8-step-1--read-the-uc-readme)
9. [Step 2 — Generate agents.md Using AI](#9-step-2--generate-agentsmd-using-ai)
10. [Step 3 — Generate skills.md Using AI](#10-step-3--generate-skillsmd-using-ai)
11. [Step 4 — Build and Run Your Code](#11-step-4--build-and-run-your-code)
12. [Step 5 — Commit Your Work](#12-step-5--commit-your-work)
13. [Step 6 — Push to GitHub](#13-step-6--push-to-github)
14. [Step 7 — Open a Pull Request](#14-step-7--open-a-pull-request)
15. [What Happens Next](#15-what-happens-next)

---

## 1. What You Need

Complete this checklist before starting. Every item is required.

### 1.1 Accounts

- [ ] A GitHub account — create one free at [github.com](https://github.com) if you do not have one
- [ ] Access to an AI tool — any of the following will work:
  - Claude (claude.ai)
  - ChatGPT (chatgpt.com)
  - Gemini (gemini.google.com)
  - Copilot (copilot.microsoft.com)
  - Cursor, Windsurf, or any AI coding assistant

### 1.2 Software

- [ ] **GitHub Desktop** — download and install from [desktop.github.com](https://desktop.github.com)
      Sign in with your GitHub account after installing.
- [ ] **Python 3.9 or above** — verify by opening a terminal and running:
  ```
  python3 --version
  ```
  If not installed, download from [python.org](https://python.org).
- [ ] **A code editor** — VS Code is recommended ([code.visualstudio.com](https://code.visualstudio.com)).
      Any text editor that can open `.py`, `.md`, and `.yaml` files will work.

### 1.3 Verify Your Setup

Open a terminal and run each command. All three must succeed before continuing.

```bash
python3 --version        # Must show 3.9 or higher
git --version            # Must show a version number
python3 -c "import csv, json; print('Ready')"   # Must print: Ready
```

> **If any command fails**, do not proceed. Resolve the installation issue first
> or flag your tutor.

---

## 2. Fork the Repository

Forking creates your own copy of the repository on GitHub. You will do all your
work in your fork.

1. Open your web browser and go to:

   ```
   https://github.com/nasscomAI/prompt-to-production
   ```

2. Click the **Fork** button in the top-right corner of the page.

3. On the "Create a new fork" screen:
   - **Owner** — select your own GitHub username
   - **Repository name** — leave it as `prompt-to-production`
   - Leave all other settings as default

4. Click **Create fork**.

5. GitHub will redirect you to your fork. The URL will now show your username:
   ```
   https://github.com/[your-username]/prompt-to-production
   ```

> **You now have your own copy of the repository.** All changes you make
> will go into your fork. You will submit your work by opening a Pull Request
> from your fork back to the original.

---

## 3. Clone to Your Computer

Cloning downloads your fork to your local machine so you can edit files.

1. Open **GitHub Desktop**.

2. Click **File → Clone Repository** from the menu.

3. Click the **GitHub.com** tab. Your fork `prompt-to-production` should appear
   in the list. Click it.

4. Under **Local Path**, choose a folder on your computer where the repo will
   be saved. Note this location — you will need to navigate to it later.

5. Click **Clone**.

6. GitHub Desktop will download the repository. When complete, you will see
   the repository name in the top-left of the GitHub Desktop window.

> **Verify the clone worked.** Open your code editor and use
> File → Open Folder to open the folder you chose in step 4.
> You should see the following structure:
>
> ```
> prompt-to-production/
> ├── resources/
> ├── uc-0a/
> ├── uc-0b/
> ├── uc-0c/
> ├── uc-x/
> ├── data/
> ├── README.md
> └── CONTRIBUTING.md
> ```

---

## 4. Create Your Branch

A branch keeps your work separate from everyone else's. You must create one
branch and use it for the entire assignment. Do not create multiple branches.

1. In **GitHub Desktop**, look at the top bar. You will see a button labelled
   **Current Branch** showing `main`.

2. Click **Current Branch**, then click **New Branch**.

3. Name your branch exactly as follows — replace the placeholders:

   ```
   participant/[your-name]-[city]
   ```

   **Examples:**

   ```
   participant/arshdeep-pune
   participant/priya-hyderabad
   participant/rahul-kolkata
   participant/deepa-ahmedabad
   ```

   Use lowercase only. Use hyphens, not spaces.

4. Click **Create Branch**.

5. GitHub Desktop will switch to your new branch. The **Current Branch** button
   now shows your branch name.

> **Important:** You will do all your work — UC-0A, your chosen UC, all commits —
> on this one branch. Do not switch back to `main`.

---

## 5. How the Assignment Works

### The Two Parts

**Part 1 — UC-0A (done with your facilitator during the session)**
You built a complaint classifier together. The files you created during the
session are already in your `uc-0a/` folder.

**Part 2 — One additional UC (done independently)**
You choose one of: UC-0B, UC-0C, or UC-X. You follow the same process
independently, using the UC README as your guide.

### The Process for Every UC

For every use case, you follow this sequence:

```
1. Read the UC README              → understand the task and failure modes
2. Generate agents.md using AI     → paste the README, get YAML, update it
3. Generate skills.md using AI     → paste the README, get YAML, update it
4. Build the .py file using AI     → prompt AI coder, run the code
5. Commit your work                → one commit per UC with a meaningful message
6. Push to GitHub                  → send your branch to your fork
```

### The RICE Framework — What It Is

The AI agent uses the RICE framework to generate your agents.md and skills.md.
You do not need to write a RICE prompt yourself — the README contains everything
the AI needs. RICE stands for:

| Element             | What it means                            |
| ------------------- | ---------------------------------------- |
| **R — Role**        | Who the AI is acting as                  |
| **I — Intent**      | What a correct output looks like         |
| **C — Context**     | What information the AI may use          |
| **E — Enforcement** | Specific rules that must never be broken |

Understanding this helps you read and check the agents.md the AI generates.

### The CRAFT Loop — What It Is

After running your code, follow this loop:

| Step            | What you do                                          |
| --------------- | ---------------------------------------------------- |
| **C — Control** | agents.md + skills.md defined before generating code |
| **R — Run**     | Execute the script and read the actual output        |
| **A — Analyze** | Note what failed and why                             |
| **F — Fix**     | Ask AI to fix one thing, re-run, compare             |
| **T — Track**   | Commit with a meaningful message                     |

---

## 6. UC-0A — The Model (Done With Your Facilitator)

UC-0A is the reference for everything you do independently.
Review what you built during the session:

1. Open the `uc-0a/` folder in your code editor.
2. Confirm these files exist:
   - `uc-0a/agents.md`
   - `uc-0a/skills.md`
   - `uc-0a/classifier.py`
   - `uc-0a/results_[city].csv`

3. Open `uc-0a/README.md` and review the failure modes for this UC.

> **If any of these files are missing**, complete them now before choosing
> your independent UC. Follow Steps 8–11 of this guide using
> `uc-0a/README.md` as your input.

---

## 7. Choose Your Use Case

Select **one** of the following. Read each description before deciding.

---

### UC-0B — Summary That Changes Meaning

**What it does:** Summarises an HR policy document preserving every binding obligation.

**Failure modes taught:**

- Clause omission — AI drops entire clauses when compressing
- Scope bleed — AI adds information not in the source document
- Condition dropping — multi-condition obligations lose one condition silently

**Input file:** `data/policy-documents/policy_hr_leave.txt`
**Output file:** `uc-0b/summary_hr_leave.txt`
**Run command:**

```bash
cd uc-0b
python3 app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
```

---

### UC-0C — Number That Looks Right

**What it does:** Computes month-over-month infrastructure spend growth
from a ward-level budget CSV.

**Failure modes taught:**

- Wrong aggregation level — AI returns one number for all wards combined
- Silent null handling — AI skips missing rows without flagging them
- Formula assumption — AI picks a formula without being asked

**Input file:** `data/budget/ward_budget.csv`
**Output file:** `uc-0c/growth_output.csv`
**Run command:**

```bash
cd uc-0c
python3 app.py --input ../data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv
```

---

### UC-X — Ask My Documents

**What it does:** Answers staff questions strictly from three policy documents.

**Failure modes taught:**

- Cross-document blending — AI merges two policies into an answer neither supports
- Hedged hallucination — AI says "while not explicitly covered..." instead of refusing
- Condition dropping — multi-condition answers lose one condition

**Input files:**

```
data/policy-documents/policy_hr_leave.txt
data/policy-documents/policy_it_acceptable_use.txt
data/policy-documents/policy_finance_reimbursement.txt
```

**Run command:**

```bash
cd uc-x
python3 app.py
```

---

> **Once you have chosen your UC**, open its folder and read its `README.md`
> fully before proceeding to Step 8.

---

## 8. Step 1 — Read the UC README

The UC README is the single source of truth for your use case. The AI will
use it to generate your agents.md and skills.md. You must read it first so
you can verify what the AI produces.

1. Open your chosen UC folder in your code editor.
2. Open the `README.md` file inside it.
3. Read the entire file. Pay attention to:
   - The named failure modes
   - The enforcement rules listed under "Enforcement Rules Your agents.md Must Include"
   - The two skill names listed under "Skills to Define in skills.md"
   - The input file, output file, and run command

> **Do not proceed until you have read the README.** The AI generates
> agents.md and skills.md from the README content. If you have not read
> it, you will not be able to check whether the output is correct.

---

## 9. Step 2 — Generate agents.md Using AI

You will paste the UC README into your AI tool and ask it to generate
agents.md. You will then update the file based on what the AI produces.

### 9.1 Copy the README Content

1. Open `uc-[your-uc]/README.md` in your code editor.
2. Select all the text and copy it.

### 9.2 Generate agents.md

1. Open your AI tool.
2. Paste the following prompt, replacing `[README CONTENT]` with the
   full text you copied:

```
You are an AI agent configuration assistant.

Read the following UC README carefully. Using the R.I.C.E framework,
generate an agents.md YAML file for this use case.

R.I.C.E stands for:
- Role: who the agent is and its operational boundary
- Intent: what a correct output looks like — make it verifiable
- Context: what information the agent is allowed to use, and what it must not use
- Enforcement: specific testable rules that must never be violated —
  include every enforcement rule mentioned in the README

Output only valid YAML with four fields: role, intent, context, enforcement.
Enforcement must be a list. Do not include any explanation or markdown code fences.

README:
[README CONTENT]
```

3. Copy the YAML output from the AI tool.

### 9.3 Save the File

1. In your code editor, open `uc-[your-uc]/agents.md`.
2. Delete the placeholder content.
3. Paste the AI-generated YAML.
4. Save the file.

### 9.4 Update the File

Read through the generated agents.md and check it against the README:

| Check                                                                 | Where to look in the README                     |
| --------------------------------------------------------------------- | ----------------------------------------------- |
| Does the enforcement section include every rule listed in the README? | "Enforcement Rules Your agents.md Must Include" |
| Does the enforcement include a refusal condition?                     | "Failure modes" section                         |
| Is the context specific — does it state what is excluded?             | "Input file" and "failure modes" sections       |

If anything is missing, edit the agents.md file directly in your code editor
to add it. Save the file when done.

### 9.5 Final agents.md Structure

Your completed agents.md must follow this structure:

```yaml
role: >
  [Description of the agent and its boundary]

intent: >
  [What correct output looks like]

context: >
  [Allowed sources. Exclusions stated explicitly.]

enforcement:
  - "[Rule 1]"
  - "[Rule 2]"
  - "[Rule 3]"
  - "[Refusal condition]"
```

---

## 10. Step 3 — Generate skills.md Using AI

### 10.1 Identify the Two Skills

Each UC README lists two skills under "Skills to Define in skills.md":

| UC    | Skill 1              | Skill 2            |
| ----- | -------------------- | ------------------ |
| UC-0B | `retrieve_policy`    | `summarize_policy` |
| UC-0C | `load_dataset`       | `compute_growth`   |
| UC-X  | `retrieve_documents` | `answer_question`  |

### 10.2 Generate skills.md

1. Open your AI tool.
2. Paste the following prompt, replacing `[README CONTENT]` with the
   full README text:

```
You are an AI agent configuration assistant.

Read the following UC README carefully. Generate a skills.md YAML file
defining the two skills described in the README.

For each skill include:
- name
- description (one sentence)
- input (type and format)
- output (type and format)
- error_handling (what the skill does when input is invalid, ambiguous,
  or matches a failure mode described in the README)

Output only valid YAML. Do not include any explanation or markdown code fences.

README:
[README CONTENT]
```

3. Copy the YAML output.
4. Open `uc-[your-uc]/skills.md`, delete the placeholder content, paste
   and save.

### 10.3 Update the File

Check each skill against the README:

| Check                                                 | What to look for                               |
| ----------------------------------------------------- | ---------------------------------------------- |
| Are both skill names correct?                         | Match names in "Skills to Define in skills.md" |
| Does error_handling address the UC failure mode?      | Match failure modes listed in the README       |
| Is the input field specific — type and format stated? | Not just "data"                                |
| Is the output field specific?                         | Not just "result"                              |

Edit the file directly if anything needs to be added or corrected. Save when done.

---

## 11. Step 4 — Build and Run Your Code

### 11.1 Generate the Code

1. Open your AI coding tool.
2. Open the starter `.py` file for your UC:
   - UC-0B: `uc-0b/app.py`
   - UC-0C: `uc-0c/app.py`
   - UC-X: `uc-x/app.py`

3. Share the following with your AI coding tool and ask it to implement
   the script:

```
Using the agents.md and skills.md provided, implement the app.py file
for this use case.

The code must:
1. Follow the enforcement rules in agents.md
2. Implement the two skills defined in skills.md including error_handling
3. Accept the run command arguments shown in the UC README
4. Produce the output file specified in the UC README

agents.md:
[paste your agents.md content]

skills.md:
[paste your skills.md content]

UC README:
[paste the UC README content]
```

4. Copy the generated code into your `app.py` file and save.

### 11.2 Run the Code

Open a terminal, navigate to your UC folder, and run the command for your UC.

**UC-0B:**

```bash
cd uc-0b
python3 app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
```

**UC-0C:**

```bash
cd uc-0c
python3 app.py --input ../data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv
```

**UC-X:**

```bash
cd uc-x
python3 app.py
```

### 11.3 If the Code Does Not Run

If the script crashes or produces an error:

1. Copy the error message.
2. Go back to your AI coding tool.
3. Paste the error and ask it to fix the specific issue.
4. Replace the code in your `.py` file with the fixed version.
5. Run again.

Repeat until the script runs without errors.

### 11.4 Check the Output

Once the script runs, verify the output file was created:

| UC    | Output file to check                                                            |
| ----- | ------------------------------------------------------------------------------- |
| UC-0B | `uc-0b/summary_hr_leave.txt` — open and read it                                 |
| UC-0C | `uc-0c/growth_output.csv` — open and check it has per-ward rows, not one number |
| UC-X  | Output appears in the terminal — try asking a question                          |

---

## 12. Step 5 — Commit Your Work

A commit saves a snapshot of your work and records what changed.

### 12.1 The Commit Message Formula

Every commit must follow this format:

```
[UC-ID] [what you built or fixed]
```

**Examples:**

```
UC-0B Generated agents.md and skills.md from README, implemented summariser
UC-0C Generated agents.md and skills.md from README, implemented growth calculator
UC-X  Generated agents.md and skills.md from README, implemented document assistant
```

**Avoid:**

```
update
done
fix
working
final
```

### 12.2 How to Commit in GitHub Desktop

1. Open **GitHub Desktop**.
2. In the left panel under **Changes**, verify the files shown are the
   ones you intend to commit:
   - `uc-[your-uc]/agents.md`
   - `uc-[your-uc]/skills.md`
   - `uc-[your-uc]/app.py`
   - The output file (`summary_hr_leave.txt`, `growth_output.csv`, etc.)

3. At the bottom of the left panel:
   - **Summary (required)** — type your commit message here

4. Click **Commit to [your-branch-name]**.

---

## 13. Step 6 — Push to GitHub

Pushing sends your committed work from your local machine to your fork on GitHub.

1. In **GitHub Desktop**, after committing, look at the top bar.
2. Click **Push origin**.
3. GitHub Desktop uploads your branch and commits to your fork.
4. When complete, the button changes to **Fetch origin**.

**Verify the push worked:**

1. Open your browser and go to:
   ```
   https://github.com/[your-username]/prompt-to-production
   ```
2. Click the **branches** dropdown (shows `main` by default).
3. Your branch `participant/[your-name]-[city]` should appear in the list.
4. Click your branch and verify your files are visible.

---

## 14. Step 7 — Open a Pull Request

A Pull Request (PR) is your submission. It sends your work from your fork
back to the original repository.

### 14.1 Open the PR

1. Go to the original repository:

   ```
   https://github.com/nasscomAI/prompt-to-production
   ```

2. GitHub will show a banner at the top:
   _"[your-branch] had recent pushes — Compare & pull request"_
   Click **Compare & pull request**.

   If the banner does not appear:
   - Click the **Pull requests** tab
   - Click **New pull request**
   - Set **base** to `main` and **compare** to your branch name

### 14.2 Fill in the PR Title

Use this exact format:

```
[City] [Name] — Vibe Coding Submission
```

Example:

```
[Pune] Arshdeep Singh — Vibe Coding Submission
```

### 14.3 Fill in the PR Description

The description box will be pre-filled with the submission template.
Fill in every section. The minimum required information is:

- Which UC you completed independently
- Confirmation that agents.md and skills.md are present and updated for both UCs
- Your commit message

### 14.4 Submit the PR

1. Review your title and description.
2. Click **Create pull request**.

Your submission is now complete.

---

## 15. What Happens Next

### What Your PR Must Contain

For your submission to be accepted, your PR must include the following files
committed on your branch:

**UC-0A (done with facilitator):**

- [ ] `uc-0a/agents.md` — present and updated
- [ ] `uc-0a/skills.md` — present and updated
- [ ] `uc-0a/classifier.py`
- [ ] `uc-0a/results_[city].csv`

**Your chosen UC (0B, 0C, or UC-X):**

- [ ] `uc-[your-uc]/agents.md` — present and updated
- [ ] `uc-[your-uc]/skills.md` — present and updated
- [ ] `uc-[your-uc]/app.py`
- [ ] Output file — `summary_hr_leave.txt`, `growth_output.csv`, or terminal output for UC-X

### If Your PR Is Missing Files

If your PR is returned, open the relevant UC folder, add the missing files,
commit with a meaningful message, and push. The PR will update automatically.

---

## Quick Reference

### Commit Message Format

```
[UC-ID] [what you built or fixed]
```

### AI Prompt to Generate agents.md

```
Read the following UC README. Using the R.I.C.E framework, generate an
agents.md YAML with four fields: role, intent, context, enforcement.
Enforcement must be a list of specific testable rules from the README.
Output only valid YAML.

README: [paste README content]
```

### AI Prompt to Generate skills.md

```
Read the following UC README. Generate a skills.md YAML defining the
two skills described. Each skill needs: name, description, input, output,
error_handling. Output only valid YAML.

README: [paste README content]
```

### Files Required Per UC

| File                       | UC-0A | UC-0B | UC-0C | UC-X |
| -------------------------- | ----- | ----- | ----- | ---- |
| `agents.md`                | ✓     | ✓     | ✓     | ✓    |
| `skills.md`                | ✓     | ✓     | ✓     | ✓    |
| `classifier.py` / `app.py` | ✓     | ✓     | ✓     | ✓    |
| `results_[city].csv`       | ✓     | —     | —     | —    |
| `summary_hr_leave.txt`     | —     | ✓     | —     | —    |
| `growth_output.csv`        | —     | —     | ✓     | —    |

### Getting Help

- Blocked for more than 5 minutes → flag your tutor
- Git issues → [docs.github.com/en/desktop](https://docs.github.com/en/desktop)
- AI tool not working → switch to any other available AI tool — the workflow is tool-agnostic
