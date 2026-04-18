@echo off
REM Generates results_pune.csv, results_ahmedabad.csv, results_hyderabad.csv, results_kolkata.csv
REM From uc-0a folder. Clear PYTHONHOME first if you see Python 3.4 errors:
REM   set PYTHONHOME=
REM   set PYTHONPATH=

set "HERE=%~dp0"
set "PY=C:\Users\prppd\AppData\Local\Programs\Python\Python312\python.exe"
set "DATA=%HERE%..\data\city-test-files"

"%PY%" "%HERE%classifier.py" --input "%DATA%\test_pune.csv"       --output "%HERE%results_pune.csv"
"%PY%" "%HERE%classifier.py" --input "%DATA%\test_ahmedabad.csv"  --output "%HERE%results_ahmedabad.csv"
"%PY%" "%HERE%classifier.py" --input "%DATA%\test_hyderabad.csv"  --output "%HERE%results_hyderabad.csv"
"%PY%" "%HERE%classifier.py" --input "%DATA%\test_kolkata.csv"   --output "%HERE%results_kolkata.csv"

echo Done all cities.
