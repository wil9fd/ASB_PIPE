# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 14:02:28 2021

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry geotiffs and output hillshade and optimised geotiffs

@version: 1.0

@changes: N/A
    
@todo: Improve speed
"""

import os


# Prompt for entering voyage name
VOYAGE_NAME = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()
ROOT_DIR = "/datasets/work/ncmi-gsm/reference/AusSeabed/"

os.mkdir(ROOT+VOYAGE_ID)

for folders in ["ASCII","Backscatter","BAG","Caris CSAR data","FP Geotiff","Metadata","Shapefile"]:
    os.mkdir(ROOT_DIR+VOYAGE_NAME+"/"+folders)

"""
DO CARIS STUFF HERE TO GET CSAR AND GEOTIFFS
"""

from ausseabed_vis import make_vis_layers

make_vis_layers(ROOT_DIR,VOYAGE_NAME)