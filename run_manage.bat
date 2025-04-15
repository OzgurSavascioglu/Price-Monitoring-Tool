@echo off
REM Change to the project directory
cd C:\Users\SAVASCIO\PycharmProjects\priceParser

REM Activate the virtual environment
call C:\Users\SAVASCIO\PycharmProjects\priceParser\venv\Scripts\activate.bat

REM Run the manage.py script with the desired command
python manage.py

REM Deactivate the virtual environment (optional)
deactivate