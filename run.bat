@echo off
rem Launch StandUp Reminder with no console window.
set "DIR=%~dp0"
start "" pythonw "%DIR%standup.py"
