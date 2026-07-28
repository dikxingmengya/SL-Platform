@echo off
title SL-Platform Startup

echo ============================================
echo   SL-Platform Startup
echo ============================================
echo.

REM ==== 1. MySQL ====
echo [1/3] Starting MySQL...
set MYSQL_BIN=C:\Program Files\MySQL\MySQL Server 8.4\bin
set DATA_DIR=E:\Projects\PyCharmProjects\SL-Platform\mysql-data

REM Check if mysqld is already running
"%MYSQL_BIN%\mysqladmin" -u root -p123456 ping 2>nul | findstr "alive" >nul
if %errorlevel% equ 0 (
    echo       MySQL already running, skipping...
    goto :skip_mysql
)

REM Start MySQL in background window
start "SL-MySQL" /MIN "%MYSQL_BIN%\mysqld" --datadir="%DATA_DIR%" --port=3306 --console

REM Wait for MySQL to be ready
echo       Waiting for MySQL to be ready...
set /a mc=0
:wait_mysql
timeout /t 2 /nobreak >nul
"%MYSQL_BIN%\mysqladmin" -u root -p123456 ping 2>nul | findstr "alive" >nul
if %errorlevel% equ 0 goto :mysql_ok
set /a mc+=2
if %mc% lss 30 goto :wait_mysql
echo       [WARN] MySQL startup timeout, continue anyway...
goto :skip_mysql
:mysql_ok
echo       [OK] MySQL ready on port 3306
:skip_mysql
echo.

REM ==== 2. Backend ====
echo [2/3] Starting Backend API...
cd /d "%~dp0backend"
start "SL-Backend" cmd /c "py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo       [OK] Backend starting... http://127.0.0.1:8000
echo       API Docs: http://127.0.0.1:8000/docs
echo.

REM ==== 3. Frontend ====
echo [3/3] Starting Frontend...
cd /d "%~dp0frontend"
start "SL-Frontend" cmd /c "npx vite --host 127.0.0.1 --port 5173"
echo       [OK] Frontend starting... http://127.0.0.1:5173
echo.

REM ==== Done ====
echo ============================================
echo   All services started!
echo.
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : http://127.0.0.1:8000/docs
echo.
echo   Test Accounts:
echo   root    / root123
echo   teacher1 / teacher123
echo   parent1  / parent123
echo ============================================
echo.
echo Press any key to close...
pause >nul
