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

REM train gca with given method for each rate
FOR %%R IN (%RATES%) DO (
    echo Training GCA with %METHOD% and rate %%R
    REM tain gca
    python -u .\train_GCA.py --dataset Cora --perturb --attack_method %METHOD% --attack_rate %%R --device cpu
    echo Done with method %METHOD% and rate %%R
)

REM Deactivate virtual environment
call deactivate

echo DONE
PAUSE