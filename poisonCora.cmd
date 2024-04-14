@echo off

REM Check args
IF "%~2"=="" (
    echo Usage: %0 method rate
    exit /b 1
)

REM Assign arguments to variables
SET METHOD=%1
SET RATE=%2

REM Define methods and rates
SET ALLOWED_METHODS="metattack random dice minmax pgd nodeembeddingattack"
SET ALLOWED_RATES="0.01 0.05 0.10"

REM Check if method is allowed
echo %ALLOWED_METHODS% | findstr /R /C:"\<%METHOD%\>" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Invalid method. Allowed methods are: %ALLOWED_METHODS%
    exit /b 1
)

REM Check if rate is allowed
echo %ALLOWED_RATES% | findstr /R /C:"\<%RATE%\>" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Invalid rate. Allowed rates are: %ALLOWED_RATES%
    exit /b 1
)

REM Change to the project directory
cd .\CLGA\

REM Activate virtual environment
call venv\Scripts\activate

REM Run Python script with parameters
python .\baseline_attacks.py --dataset Cora --method %METHOD% --rate %RATE% --device cpu

REM Deactivate virtual environment
call deactivate

echo DONE
PAUSE