"""
UC-X classifier.py / runner alias for app.py
Ensures compatibility if invoked as classifier.py or app.py.
"""
from app import main

if __name__ == "__main__":
    main()
