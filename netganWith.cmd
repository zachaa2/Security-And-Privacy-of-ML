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
cd .\NetGAN-torch\

REM Activate virtual environment
call venv\Scripts\activate

REM run netgan for each rate and the given method
FOR %%R IN (%RATES%) DO (
    echo Running attack with method %METHOD% and rate %%R
    REM run netgan
    python .\main.py --method %METHOD% --rate %%R
    echo Done with method %METHOD% and rate %%R
)