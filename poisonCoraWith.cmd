@echo off

REM Check args
IF "%~1"=="" (
    echo Usage: %0 method
    exit /b 1
)
REM set method from args
SET METHOD=%1

REM rates
SET RATES=0.01 0.05 0.10
REM allowed methods
SET ALLOWED_METHODS="metattack random dice minmax pgd nodeembeddingattack"

REM Check if arg method is allowed
echo %ALLOWED_METHODS% | findstr /R /C:"\<%METHOD%\>" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Invalid method. Allowed methods are: %ALLOWED_METHODS%
    exit /b 1
)

REM Change to correct directory
cd .\CLGA\

REM Activate virtual environment
call venv\Scripts\activate


REM run given method for each rate
FOR %%R IN (%RATES%) DO (
    echo Running attack with method %METHOD% and rate %%R
    REM run attack
    python .\baseline_attacks.py --dataset Cora --method %METHOD% --rate %%R --device cpu
    echo Done with method %METHOD% and rate %%R
)

REM Deactivate virtual environment
call deactivate

echo DONE
PAUSE