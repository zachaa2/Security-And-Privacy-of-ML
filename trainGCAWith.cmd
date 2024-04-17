@echo off

REM Define rates
SET RATES=0.01 0.05 0.10

REM Define the list of methods to process
SET METHODS=dice pgd minmax

REM Change to the correct directory
cd .\CLGA\

REM Activate virtual environment
call venv\Scripts\activate

REM Loop through each method in the METHODS variable
for %%M in (%METHODS%) do (
    REM Train GCA with the given method for each rate
    FOR %%R IN (%RATES%) DO (
        echo Training GCA with %%M and rate %%R
        REM Train GCA
        python -u .\train_GCA.py --dataset Cora --perturb --attack_method %%M --attack_rate %%R --device cuda:0
        echo Done with method %%M and rate %%R
    )
)

REM Deactivate virtual environment
call deactivate

echo DONE
pause
