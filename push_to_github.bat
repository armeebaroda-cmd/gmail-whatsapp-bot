@echo off
echo ================================================
echo  Pushing latest changes to GitHub...
echo ================================================

git -C "%~dp0" add -A
git -C "%~dp0" commit -m "Update: %date% %time%"
git -C "%~dp0" -c "credential.helper=" push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Changes pushed to GitHub.
) else (
    echo FAILED! Check your internet connection.
)
echo ================================================
pause
