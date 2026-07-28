@echo off
title SL-Platform Shutdown

echo ============================================
echo   Shutting down SL-Platform...
echo ============================================
echo.

echo Stopping Frontend...
taskkill /FI "WINDOWTITLE eq SL-Frontend*" /T /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173.*LISTENING" 2^>nul') do taskkill /PID %%a /F 2>nul
echo   [OK] Frontend stopped

echo Stopping Backend...
taskkill /FI "WINDOWTITLE eq SL-Backend*" /T /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do taskkill /PID %%a /F 2>nul
echo   [OK] Backend stopped

echo Stopping MySQL...
taskkill /FI "WINDOWTITLE eq SL-MySQL*" /T /F 2>nul
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqladmin" -u root -p123456 shutdown 2>nul
echo   [OK] MySQL stopped

echo.
echo ============================================
echo   All services stopped.
echo ============================================
echo.
pause
