@echo off
rem ====================================================================
rem  StandUp Reminder - one-click setup
rem  Double-click this file to install the Desktop icon and start the app.
rem ====================================================================
setlocal
cd /d "%~dp0"

echo.
echo   Installing StandUp Reminder...
echo.

rem --- make sure Python is available -------------------------------------
where pythonw >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 (
    echo   Python was not found on this computer.
    echo   Please install Python 3 from https://www.python.org/downloads/
    echo   and tick "Add Python to PATH" during install, then run setup.bat again.
    echo.
    pause
    exit /b 1
  )
)

rem --- create the Desktop shortcut (with custom icon) -------------------
python install.py

rem --- launch the app right away ---------------------------------------
echo.
echo   Starting StandUp Reminder...
start "" pythonw "%~dp0standup.py"

echo.
echo   Done!  A "StandUp Reminder" icon is now on your Desktop.
echo   Double-click it anytime to start the app.
echo.
pause
