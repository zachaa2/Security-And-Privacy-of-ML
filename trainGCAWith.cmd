@echo off

REM Check args
IF "%~1"=="" (
    echo Usage: %0 method1 method2 ...
    exit /b 1
)

REM Define rates
SET RATES=0.01 0.05 0.10

REM Define allowed methods
SET ALLOWED_METHODS="dice minmax pgd"

REM Change to the correct directory
cd .\CLGA\

REM Activate virtual environment
call venv\Scripts\activate

REM Loop through each argument provided
:nextmethod
SHIFT
IF "%~1"=="" GOTO endmethods
SET METHOD=%1

REM Check if the current arg method is allowed
echo %ALLOWED_METHODS% | findstr /R /C:"\<%METHOD%\>" >nul 2>&1
IF ERRORLEVEL 1 (
    echo Invalid method: %METHOD%. Allowed methods are: %ALLOWED_METHODS%
    goto nextmethod
)

REM Train GCA with the given method for each rate
FOR %%R IN (%RATES%) DO (
    echo Training GCA with %METHOD% and rate %%R
    REM Train GCA
    python -u .\train_GCA.py --dataset Cora --perturb --attack_method %METHOD% --attack_rate %%R --device cuda:0
    echo Done with method %METHOD% and rate %%R
)

GOTO nextmethod

:endmethods
REM Deactivate virtual environment
call deactivate

echo DONE
PAUSE
