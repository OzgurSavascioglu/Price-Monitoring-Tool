@echo off
REM Change to the project directory
cd path_to_project_directory

REM Activate the virtual environment
call Project_Directory\venv\Scripts\activate.bat

REM Run the manage.py script with the desired command
python manage.py

REM Deactivate the virtual environment (optional)
deactivate
