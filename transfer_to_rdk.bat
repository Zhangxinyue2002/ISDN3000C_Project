@echo off
REM Windows batch script to help transfer files to RDK X5
REM Usage: transfer_to_rdk.bat 192.168.127.10

echo ================================
echo File Transfer Helper - RDK X5
echo ================================
echo.

if "%1"=="" (
    echo ERROR: Please provide RDK IP address
    echo Usage: transfer_to_rdk.bat 192.168.x.x
    echo.
    pause
    exit /b 1
)

set RDK_IP=%1
set RDK_USER=root
set PROJECT_DIR=ISDN3000C_Project

echo Target: %RDK_USER%@%RDK_IP%
echo.

echo This script will help you transfer files to your RDK X5.
echo.
echo Prerequisites:
echo   1. RDK X5 is powered on and connected to network
echo   2. You have SSH access to RDK X5
echo   3. SCP/SSH client is available (Windows 10+ has built-in)
echo.

echo Files to transfer:
echo   - config/config.yaml
echo   - requirements.txt
echo   - src/ directory (all Python files)
echo   - test_components.py
echo   - RDK_SETUP.md
echo   - QUICK_START.md
echo.

pause

echo.
echo Starting file transfer...
echo.

REM Create project directory on RDK
echo Creating project directory on RDK...
ssh %RDK_USER%@%RDK_IP% "mkdir -p ~/%PROJECT_DIR%/config ~/%PROJECT_DIR%/src ~/%PROJECT_DIR%/data/images ~/%PROJECT_DIR%/data/logs ~/%PROJECT_DIR%/models"

REM Transfer config
echo Transferring config...
scp config\config.yaml %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/config/

REM Transfer requirements
echo Transferring requirements.txt...
scp requirements.txt %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/

REM Transfer src directory
echo Transferring src/ directory...
scp src\__init__.py %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/src/
scp src\database.py %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/src/
scp src\gpio_handler.py %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/src/
scp src\camera_service.py %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/src/

REM Transfer test script
echo Transferring test_components.py...
scp test_components.py %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/

REM Transfer documentation
echo Transferring documentation...
scp RDK_SETUP.md %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/
scp QUICK_START.md %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/
scp CHECKLIST.md %RDK_USER%@%RDK_IP%:~/%PROJECT_DIR%/

echo.
echo ================================
echo Transfer Complete!
echo ================================
echo.
echo Next steps:
echo   1. SSH into RDK: ssh %RDK_USER%@%RDK_IP%
echo   2. Navigate: cd ~/%PROJECT_DIR%
echo   3. Follow: cat QUICK_START.md
echo   4. Run: python3 test_components.py
echo.

pause
