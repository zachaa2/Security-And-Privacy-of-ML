#!/bin/bash

# Check args
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 method"
    exit 1
fi

# Set method from args
METHOD="$1"

# Rates
RATES="0.01 0.05 0.10"
# Allowed methods
ALLOWED_METHODS="metattack random dice minmax pgd nodeembeddingattack"

# Check if arg method is allowed
if [[ ! " $ALLOWED_METHODS " =~ " $METHOD " ]]; then
    echo "Invalid method. Allowed methods are: $ALLOWED_METHODS"
    exit 1
fi

# Change to correct directory
cd NetGAN-torch/

# Activate virtual environment
source venv/Scripts/activate

# Run netgan for each rate and the given method
for R in $RATES; do
    echo "Running netgan with attack method $METHOD and rate $R"
    # Run netgan
    python -u main.py --method "$METHOD" --rate "$R"
    echo "Done with netgan on attack method $METHOD and rate $R"
done
read -p "Press enter to continue..."