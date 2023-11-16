#!/bin/bash

# take database with match links (output from work in tso-database-builder) and produce file in form uid,linkage,names 
python3 cli.py sort-linkage-data ../TSO_project/processed_data/all.matched_companyid.matched_normname.permutate.csv -o tso.links.csv

# take findthatcharity linkages and create file in uid,linkage,names format
python3 cli.py wrangle-ftc ../TSO_project/raw_data/FindThatCharity_matches.csv -o ftc.links.csv

# take output of above and create file with line for each uid, and matches in each dataset.
python3 cli.py analyse-linkages tso.links.csv ftc.links.csv -o tso_ftc.linkage_comparison.csv


# basic stats for linkage file
python3 cli.py get-linkage-stats -o tso_ftc.linkage_stats.out ../TSO_project/processed_data/compare_linkage_tso_ftc.out.csv 