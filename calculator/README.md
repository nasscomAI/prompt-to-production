# OmniCalc Suite

An elegant suite of calculator applications, including a premium web-based application (Calculator + Scientific Mode + Unit Converter) and a lightweight Python command-line calculator.

## 1. Web-Based Premium Application (`index.html`)

OmniCalc is a modern, responsive, and responsive single-page web app built with Vanilla HTML, CSS, and JavaScript.

### Features
- **Standard & Scientific Modes:** Toggle between basic arithmetic and scientific operations (trigonometry, logarithms, factorials, powers, parentheses, constants $\pi$ and $e$).
- **Tactile UI Experience:** Modern neumorphism-inspired dark/light theme, button animations, transition states, and high readability.
- **Conversion Engine:** Multi-category unit converter supporting **Length**, **Weight/Mass**, **Temperature**, and **Area** with dynamic quick-conversion tables.
- **Calculations History:** Side-panel log storing your recent operations locally so you can click and reload them.
- **Keyboard Friendly:** Full support for keyboard number keys, operators, brackets, Enter/Equals, Backspace, and Escape.

### How to Run
Simply double-click the `index.html` file to open it in any modern browser, or launch a quick local server from the project directory:

```bash
# Using Python
python -m http.server 8000
```
Then, open your browser and navigate to `http://localhost:8000`.

---

## 2. Interactive Python CLI Calculator (`calculator.py`)

A lightweight, prompt-based interactive command-line calculator.

### Features
- Support for key arithmetic functions: addition, subtraction, multiplication, and division.
- Graceful validation handling for invalid characters or zero-division exceptions.

### How to Run
```bash
python calculator.py
```
