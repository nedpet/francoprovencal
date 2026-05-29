# run foma within ubuntu, ex. ./run_foma.sh python_file.py

# to create the venv, run these commands within home folder:
# python3.13 -m venv foma-env
# source ~/foma-env/bin/activate
# pip install foma
# pip install pympi-ling
# deactivate

#!/bin/bash
source ~/foma-env/bin/activate
python "$1"