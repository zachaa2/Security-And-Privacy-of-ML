#!/bin/bash

# Check args 
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 method rate"
    exit 1
fi

# Assign arguments to variables
METHOD=$1
RATE=$2

# allowed methods and rates
ALLOWED_METHODS="metattack random dice minmax pgd nodeembeddingattack"
ALLOWED_RATES="0.01 0.05 0.10"

# Check if the method is allowed
if [[ ! " $ALLOWED_METHODS " =~ " $METHOD " ]]; then
    echo "Invalid method. Allowed methods are: $ALLOWED_METHODS"
    exit 1
fi

# Check if the rate is allowed
if [[ ! " $ALLOWED_RATES " =~ " $RATE " ]]; then
    echo "Invalid rate. Allowed rates are: $ALLOWED_RATES"
    exit 1
fi

# Change to the project directory
cd ./CLGA/

# Activate virtual environment
source venv/bin/activate

# Run Python script with parameters
python ./baseline_attacks.py --dataset Cora --method $METHOD --rate $RATE --device cpu

# Deactivate virtual environment
deactivate

echo "DONE"
read -p "Press enter to continue..."
