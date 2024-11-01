@echo off
if exist "venv\Scripts\activate.bat" (call venv\Scripts\activate.bat && python src\main.py && deactivate) else echo Virtual environment not found.
