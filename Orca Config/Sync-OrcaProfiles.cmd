@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Sync-OrcaProfiles.ps1" -IncludeDiagnostics -Commit -Push
set "exit_code=%errorlevel%"
echo.
if not "%exit_code%"=="0" (
    echo OrcaSlicer synchronization failed with exit code %exit_code%.
) else (
    echo OrcaSlicer profiles, G-code, and logs were synchronized and pushed.
)
pause
exit /b %exit_code%
