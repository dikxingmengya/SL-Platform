@echo off
title SL-Platform Dev Startup

echo ============================================
echo   SL-Platform Dev Mode
echo ============================================
echo.

set MYSQL_BIN=C:\Program Files\MySQL\MySQL Server 8.4\bin
set DATA_DIR=E:\Projects\PyCharmProjects\SL-Platform\mysql-data

REM ==== MySQL ====
echo [1/3] MySQL...
"%MYSQL_BIN%\mysqladmin" -u root -p123456 ping 2>nul | findstr "alive" >nul
if %errorlevel% neq 0 (
    start "SL-MySQL" /MIN "%MYSQL_BIN%\mysqld" --datadir="%DATA_DIR%" --port=3306 --console
    echo   Starting MySQL, waiting...
    set /a mc=0
    :w
    timeout /t 2 /nobreak >nul
    "%MYSQL_BIN%\mysqladmin" -u root -p123456 ping 2>nul | findstr "alive" >nul
    if %errorlevel% equ 0 goto :mok
    set /a mc+=2
    if %mc% lss 30 goto :w
    :mok
)
echo   [OK] MySQL

REM ==== Backend ====
echo [2/3] Backend...
cd /d "%~dp0backend"
start "SL-Backend" cmd /c "py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo   [OK] http://127.0.0.1:8000

REM ==== Frontend ====
echo [3/3] Frontend...
cd /d "%~dp0frontend"
start "SL-Frontend" cmd /c "npx vite --host 127.0.0.1 --port 5173"
echo   [OK] http://127.0.0.1:5173

echo.
echo Access: http://127.0.0.1:5173
echo Login:  root / root123
echo.
timeout /t 5 >nul
exit
