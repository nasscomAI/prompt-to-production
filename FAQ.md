# Frequently Asked Questions (FAQ) 💡

## 🛠 Git & GitHub Issues

### When should I open an Issue?
- **Bug Reports:** If you find something broken in the starter code.
- **Clarification:** If the instructions for a User Case (UC) are confusing.
- **Stuck:** If you've been debugging for more than 5 minutes and need help from a tutor (mention them with @username).

### How do I open a good Issue?
1. Click the **Issues** tab -> **New Issue**.
2. Give it a clear title (e.g., \`[UC-0A] Confusion about severity keywords\`).
3. Describe what you're seeing and what you expected.
4. Add a screenshot if it helps!

---

## 🚀 Creating a Pull Request (PR)

### Step 1: Fork the Repo
Click the **Fork** button at the top right of this page. This creates a copy of the workshop code in your own GitHub account.

### Step 2: Clone Your Fork
Copy your fork's URL and run:
```bash
git clone https://github.com/[your-username]/prompt-to-production.git
cd prompt-to-production
```

### Step 3: Create a Branch
**Crucial:** Do not work on the \`main\` branch. Create a new one:
```bash
git checkout -b participant/[your-name]-[city]
# Example: git checkout -b participant/arshdeep-pune
```

### Step 4: Commit & Push
Follow the commit message standard mentioned in the README:
```bash
git add .
git commit -m \"[UC-0A] Fix severity: missing keywords → added triggers\"
git push origin participant/[your-name]-[city]
```

### Step 5: Open the PR
1. Go to the **original** repository (nasscomAI/prompt-to-production).
2. You'll see a yellow bar saying \"Compare & pull request\" — click it!
3. Ensure the **base** is \`nasscomAI/main\` and the **head** is your branch.
4. Fill out the PR template completely.

---

## 📥 Clone & Download Issues

### ❌ Error: \"Permission Denied (publickey)\"
This happens if you haven't set up SSH keys on GitHub or your local agent isn't running.
- **Quick Fix:** Use the **HTTPS** URL instead of SSH.
- Copy the URL starting with \`https://github.com/...\` from the green **Code** button.
- **SSH Fix:** Run \`ssh-add ~/.ssh/id_ed25519\` (or your key name) to ensure your key is active.

### ❌ Error: \"Cloned an empty repository\"
If your folder is empty after cloning:
1. **Check your URL:** Ensure you are cloning your **fork** (e.g., \`github.com/YOUR-NAME/...\`) and not a blank repository you just created.
2. **Check the branch:** Sometimes the default branch is different. Run \`git branch -a\` to see all available branches.
3. **Hidden Files:** On Mac/Linux, run \`ls -la\`. On Windows, enable \"Hidden items\" in File Explorer.

### ❌ Authentication Failed (HTTPS)
If GitHub asks for a password and fails:
- **Personal Access Token (PAT):** Since 2021, GitHub requires a PAT instead of your account password for command-line Git.
- [Generate a PAT here](https://github.com/settings/tokens) with \`repo\` scope.

### ❌ Still can't clone? (Download as ZIP)
If Git is giving you too much trouble:
1. Click the green **Code** button on GitHub.
2. Select **Download ZIP**.
3. Extract the files and then run \`git init\` inside that folder to start your Git journey manually.

---

## 🤖 AI-Assisted Coding & IDEs

### Which IDE should I use?
We recommend **VS Code**, **Cursor**, **Antigravity**, or **Trae**.

### Which ones are free for AI coding?
1. **Trae:** A powerful, free-to-use adaptive AI IDE (built by ByteDance) that is designed for "vibe coding" and agentic workflows.
2. **Antigravity:** A modern, AI-native IDE that is gaining popularity for its speed and free accessibility.
3. **VS Code + Codeium:** VS Code is free, and [Codeium](https://codeium.com/) offers a powerful **Free Forever** tier for individuals.
4. **Cursor:** An AI-native IDE (fork of VS Code) built for AI coding. It has a **Free** tier with limited AI requests per month.
5. **GitHub Copilot:** Usually a paid service ($10/mo), but **FREE** for verified students, teachers, and maintainers of popular open-source projects.

### 💻 CLI-based AI Coding
If you prefer working entirely in the terminal, check out:
1. **Gemini CLI:** A powerful AI-native terminal agent (the one you're interacting with!) that can analyze code, run tests, and manage your entire git workflow.
2. **Aider:** A popular CLI tool that lets you edit code in your terminal using AI. (Requires an API key).
3. **Mentat:** An open-source AI coding assistant that lives in your terminal and can understand your entire codebase.
4. **Open Interpreter:** Allows the AI to run code locally in your terminal to perform tasks (highly recommended for advanced users).

---

## 📖 Useful Resources
- [Git Cheat Sheet](https://git-scm.com/cheat-sheet)
- [GitHub Best Practices for Repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)
- [Official GitHub Desktop](https://desktop.github.com/) (Great for those who prefer a GUI over CLI!)

---

---

## 🚧 Common Troubleshooting

### My PR has a red 'X' (Validation Failed)
Check the **Actions** tab. It's likely one of two things:
1. **Commit Message:** Ensure your message follows the exact \`[UC-ID] Fix... → ...\` format.
2. **Python Syntax:** Your script might have a typo. Run it locally first!

### How do I sync my fork with the main repo?
If the workshop leads update the main repo, you can sync yours by clicking **Sync fork** on your GitHub repo page or running:
\`\`\`bash
git fetch upstream
git merge upstream/main
\`\`\`
