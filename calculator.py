#!/usr/bin/env python3
"""
A feature-rich terminal calculator with history and scientific functions.
"""

import math
import os

# ── ANSI color codes ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"

# ── History ───────────────────────────────────────────────────────────────────
history: list[str] = []


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_header() -> None:
    print(f"{CYAN}{BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║       🧮  Python Calculator           ║")
    print("  ╚══════════════════════════════════════╝")
    print(RESET)


def print_help() -> None:
    print(f"\n{BLUE}{BOLD}  ── Basic Operations ───────────────────────{RESET}")
    ops = [
        ("add / +",    "Addition           e.g. add 5 3  or  5 + 3"),
        ("sub / -",    "Subtraction        e.g. sub 9 4  or  9 - 4"),
        ("mul / *",    "Multiplication     e.g. mul 6 7  or  6 * 7"),
        ("div / /",    "Division           e.g. div 10 2 or  10 / 2"),
        ("mod / %",    "Modulus            e.g. mod 10 3 or  10 % 3"),
        ("pow / **",   "Power              e.g. pow 2 8  or  2 ** 8"),
    ]
    for cmd, desc in ops:
        print(f"  {GREEN}{cmd:<14}{RESET}{desc}")

    print(f"\n{BLUE}{BOLD}  ── Scientific Functions ────────────────────{RESET}")
    sci = [
        ("sqrt <n>",   "Square root        e.g. sqrt 16"),
        ("cbrt <n>",   "Cube root          e.g. cbrt 27"),
        ("log <n>",    "log base-10        e.g. log 100"),
        ("ln <n>",     "Natural log        e.g. ln 2.718"),
        ("sin <n>",    "Sine (degrees)     e.g. sin 90"),
        ("cos <n>",    "Cosine (degrees)   e.g. cos 0"),
        ("tan <n>",    "Tangent (degrees)  e.g. tan 45"),
        ("abs <n>",    "Absolute value     e.g. abs -7"),
        ("fact <n>",   "Factorial          e.g. fact 5"),
    ]
    for cmd, desc in sci:
        print(f"  {GREEN}{cmd:<14}{RESET}{desc}")

    print(f"\n{BLUE}{BOLD}  ── Commands ────────────────────────────────{RESET}")
    cmds = [
        ("history",  "Show calculation history"),
        ("clear",    "Clear the screen"),
        ("help",     "Show this help message"),
        ("exit / q", "Quit the calculator"),
    ]
    for cmd, desc in cmds:
        print(f"  {YELLOW}{cmd:<14}{RESET}{desc}")
    print()


def format_result(value: float) -> str:
    """Return an int-looking string if the value is a whole number."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def show_history() -> None:
    if not history:
        print(f"  {GRAY}No history yet.{RESET}\n")
        return
    print(f"\n{BLUE}{BOLD}  ── History ─────────────────────────────────{RESET}")
    for i, entry in enumerate(history, 1):
        print(f"  {GRAY}{i:>3}.{RESET}  {entry}")
    print()


def record(expression: str, result: str) -> None:
    history.append(f"{expression}  =  {GREEN}{result}{RESET}")


def evaluate(tokens: list[str]) -> None:
    """Parse tokens and compute the result."""
    try:
        if len(tokens) == 3:
            # Support both "add a b" (word cmd) and "a + b" (symbol op)
            WORD_OPS = {"add", "sub", "mul", "div", "mod", "pow"}
            if tokens[0].lower() in WORD_OPS:
                cmd, a_str, b_str = tokens[0].lower(), tokens[1], tokens[2]
                op = cmd
            else:
                a_str, op, b_str = tokens

            a, b = float(a_str), float(b_str)

            symbol_map = {
                "+": a + b,
                "-": a - b,
                "*": a * b,
                "%": a % b,
                "**": a ** b,
            }
            word_map = {
                "add": a + b,
                "sub": a - b,
                "mul": a * b,
                "div": None,
                "mod": a % b,
                "pow": a ** b,
            }

            combined = {**symbol_map, **word_map}

            if op not in combined:
                print(f"  {RED}Unknown operator '{op}'. Type 'help' for usage.{RESET}\n")
                return

            result = combined[op]

            if op in ("/", "div"):
                if b == 0:
                    print(f"  {RED}Error: Division by zero!{RESET}\n")
                    return
                result = a / b

            res_str = format_result(result)
            expr = f"{a_str} {op} {b_str}"
            print(f"  {CYAN}  {expr}  =  {GREEN}{BOLD}{res_str}{RESET}\n")
            record(expr, res_str)

        elif len(tokens) == 2:
            cmd, n_str = tokens[0].lower(), tokens[1]
            n = float(n_str)

            sci_map = {
                "sqrt":  lambda x: math.sqrt(x),
                "cbrt":  lambda x: x ** (1 / 3),
                "log":   lambda x: math.log10(x),
                "ln":    lambda x: math.log(x),
                "sin":   lambda x: math.sin(math.radians(x)),
                "cos":   lambda x: math.cos(math.radians(x)),
                "tan":   lambda x: math.tan(math.radians(x)),
                "abs":   lambda x: abs(x),
                "fact":  lambda x: math.factorial(int(x)),
            }

            if cmd not in sci_map:
                print(f"  {RED}Unknown command '{cmd}'. Type 'help' for usage.{RESET}\n")
                return

            if cmd in ("sqrt", "log", "ln") and n < 0:
                print(f"  {RED}Error: Cannot compute {cmd} of a negative number.{RESET}\n")
                return
            if cmd == "fact" and (n < 0 or n != int(n)):
                print(f"  {RED}Error: Factorial requires a non-negative integer.{RESET}\n")
                return

            result = sci_map[cmd](n)
            res_str = format_result(result)
            expr = f"{cmd}({n_str})"
            print(f"  {CYAN}  {expr}  =  {GREEN}{BOLD}{res_str}{RESET}\n")
            record(expr, res_str)

        else:
            print(f"  {RED}Invalid input. Type 'help' for usage.{RESET}\n")

    except ValueError as e:
        print(f"  {RED}ValueError: {e}{RESET}\n")
    except OverflowError:
        print(f"  {RED}Error: Result is too large to compute.{RESET}\n")


def main() -> None:
    clear_screen()
    print_header()
    print(f"  {GRAY}Type 'help' for usage  ·  'exit' or 'q' to quit{RESET}\n")

    while True:
        try:
            raw = input(f"  {CYAN}{BOLD}calc>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {YELLOW}Bye! 👋{RESET}\n")
            break

        if not raw:
            continue

        lower = raw.lower()

        if lower in ("exit", "q", "quit"):
            print(f"\n  {YELLOW}Bye! 👋{RESET}\n")
            break
        elif lower == "help":
            print_help()
        elif lower == "history":
            show_history()
        elif lower == "clear":
            clear_screen()
            print_header()
        else:
            # Normalize: allow "5+3" → ["5", "+", "3"]
            import re
            tokens = re.split(r"\s+", raw.strip())
            if len(tokens) == 1:
                # Try splitting on operator with no spaces: e.g. "5+3"
                m = re.match(r"^(-?[\d.]+)(\*\*|[+\-*/%])(-?[\d.]+)$", raw)
                if m:
                    tokens = [m.group(1), m.group(2), m.group(3)]
            evaluate(tokens)


if __name__ == "__main__":
    main()
