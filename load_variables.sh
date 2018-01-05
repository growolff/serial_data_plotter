#!/bin/bash

# anaconda
export PATH=/home/matias/anaconda3/bin:$PATH
unset PYTHONPATH

# qt stuff
export QT_DEBUG_PLUGINS=0
export LD_LIBRARY_PATH=/home/matias/anaconda3/lib/libxcb.so.1

# activate environment
source activate knightrobotics
