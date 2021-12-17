# # -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 16:37:42 2021

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry geotiffs and output hillshade and overlays 

@version: 1.0
"""

## Package Setup
import time
import sys
import gdal
import os
import glob
import pathlib
from make_vis_layers import make_vis_layers 

# Prompt for entering voyage name
voyage = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()

make_vis_layers("/datasets/work/ncmi-gsm/reference/AusSeabed/",voyage)