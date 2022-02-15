#!/usr/miniconda3/envs/ASB/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 13:53:53 2022

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry shapefiles and collect geometries into  

@version: 1.0
"""

## Package Setup
import pathlib
import sys
import time
from make_vis_layers import make_vis_layers
from make_contours import make_contours
from merge_polys import merge_polys 
from import_metadata import import_metadata

# Prompt for entering voyage name
voyage = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()

t0 = time.perf_counter()
root_path = "/datasets/work/ncmi-gsm/reference/AusSeabed/"
# Set root path to the ASB reference folder 
# '''Note: this path is accessed throught putty on the HPC'''

# If the voyage ID can't be found prompt again
while not pathlib.Path(root_path + voyage).exists():
    print("\nI can't find the voyage ID: " + voyage)
    voyage = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
    
    if voyage == "exit":
        sys.exit("\nBye-bye")

confirmation = input('\nWould you like to create contours? [y/n]: \nWARNING! This may take significant time...\n').lower()

make_vis_layers(root_path, voyage)

if confirmation == 'y':
    make_contours(root_path, voyage)

merge_polys(root_path, voyage)

import_metadata(root_path, voyage)

t1 = time.perf_counter()

if t1-t0 > 60:
    print('\nTotal computation time {:.2f} min\n\n'.format((t1-t0)/60))
else:
    print('\nTotal computation time {:.2f} sec\n\n'.format(t1-t0))
