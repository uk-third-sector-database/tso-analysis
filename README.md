# Getting Started

Use python 3.11

    make setup-pyenv
    make setup-venv
    source .tso/bin/activate
    make install-deps
    
## Installing requirements

To install test and runtime requirements use

    pip install -r test-requirements.txt

To only install runtime requirements use:

    pip install -r requirements.txt

## Testing 

    pytest . 

## Running

    python cli.py analyse-linkages <source csv 1> <source csv 2> <output csv>
    python cli.py sort-linkage-data <source csv> <output csv>

    See linkages_analysis.sh for example usage

## To contain
- [x]  Tool to take FindThatCharity linkage data and convert it to comparible format
- [x]  Tool to take two datasets with linked organsiations and compare the linkages found
- []  Tool to analyse organisation lifespans
- [] Tool to analyse spatial pattern of organisations

 
