#!/bin/bash

# Check args
if [ "$1" == "" ]; then
    echo "Usage: $0 method"
    exit 1
fi

# set method from args
METHOD=$1

# rates
RATES="0.01 0.05 0.10"
# allowed methods
ALLOWED_METHODS="metattack random dice minmax pgd nodeembeddingattack"

# Check if arg method is allowed
if ! echo "$ALLOWED_METHODS" | grep -qw "$METHOD"; then
    echo "Invalid method. Allowed methods are: $ALLOWED_METHODS"
    exit 1
fi

# Change to correct directory
cd ./CLGA/

# Activate virtual environment
source venv/bin/activate

# train gca with given method for each rate
for R in $RATES; do
    echo "Training GCA with $METHOD and rate $R"
    # run gca
    python -u ./train_GCA.py --dataset Cora --perturb --attack_method "$METHOD" --attack_rate "$R" --device cuda:0
    echo "Done with method $METHOD and rate $R"
done

# Deactivate virtual environment
deactivate

echo "DONE"