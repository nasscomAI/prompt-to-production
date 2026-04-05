# Session Prerequisites

To participate in this session and successfully build the four use cases (UC-0A through UC-X), ensure the following hardware and software requirements are met.

---

## 💻 Hardware Prerequisites

**Laptop Specifications**
- **RAM**: **16GB minimum** (Highly Recommended). Modern AI-powered IDEs and WSL2 are memory-intensive.
- **Processor (CPU)**: 
    - Intel Core i5 / AMD Ryzen 5 (11th Gen or newer) or better.
    - Apple Silicon (M1/M2/M3) for macOS users.
- **Storage**: At least **10GB of free space** for the workshop repository and WSL overhead.
- **BIOS Settings**: **Virtualization (VT-x or AMD-V)** must be **Enabled**. This is critical for running WSL2 on Windows.

---

## 🛠 Software Prerequisites

**Core Environment**
- **Python**: Version **3.9 or higher**. Use the `python3` command.
    - Verify: `python3 --version`
- **Git**: Must be installed.
    - Verify: `git --version`
- **Python Libraries**: Ensure `csv` and `json` are functional.
    - Verify: `python3 -c "import csv, json; print('Ready')"`

**Operating System & Tools**
- **Windows Users**: Must have **WSL2 (Windows Subsystem for Linux)** installed (Ubuntu is recommended).
- **IDEs**: Antigravity, Trae , Cursor, or VS Code (with WSL extension).
- **CLIs**: 
    - **Windows**: Use PowerShell or Command Prompt.
    - **macOS/Linux**: Use Terminal.
- **AI Tools**: Open Interpreter, Aider, or Mentat are also compatible.

---

## 📁 Project Data Verification

Confirm the following files are present in your local environment:

- **City Test Files**: `data/city-test-files/`
- **Policy Documents**: `data/policy-documents/`
- **Budget Data**: `data/budget/ward_budget.csv`

---

## 🚀 Quick Start Commands

```bash
# Verify Python
python3 --version

# Verify Git
git --version

# Check Data
ls data/city-test-files/
```

For more details, see the [README.md](./README.md) and [FAQ.md](./FAQ.md).

