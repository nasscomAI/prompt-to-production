"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys

def main(argv=None):
    """Minimal safe implementation for tests.

    - Parses an optional --version flag and prints a stable version string.
    - Returns 0 on success.
    """
    parser = argparse.ArgumentParser(description="UC-0B starter CLI")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    args = parser.parse_args(argv)

    if args.version:
        print("uc-0b 0.1.0")
    # Add real behaviour here following README.md when ready.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
