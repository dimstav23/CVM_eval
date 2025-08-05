#!/bin/bash
set -euxo pipefail

PLOT_DIR="trace/plotting_scripts"

cd $PLOT_DIR
python3 plot_cpu.py
python3 plot_memory.py
python3 plot_network_io.py
python3 plot_storage_io.py