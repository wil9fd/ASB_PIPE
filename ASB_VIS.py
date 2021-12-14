# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 16:37:42 2021

@author: Samson Williams

@organisation: CSIRO

@detail: Take bathymetry geotiffs and output hillshade and optimised geotiffs

@version: 1.0

@changes: N/A
    
@todo: Improve speed
"""


## Package Setup
import time
import sys
from osgeo import gdal
import os
import glob
import pathlib
 
# Start timer
t0 = time.perf_counter()


# Path setup
#subprocess.check_call('cd', shell=True)
#subprocess.check_call('cd /mnt/datasets', shell=True)
#subprocess.check_call('cd work/ncmi-gsm', shell=True)

def ausseabed_vis(voyage_input):

    """
    Brief: This function finds all '*.tiff' files in a directory, then uses GDAL to produce a hillshade and a COG for each TIFF.
        ***WARNING: THIS FUNCTION ASSUMES ALL TIFF FILES IN THE DIRECTORY ARE DTMs***

    Parameters: Path to TIFF folder

    Return: Paths to GOC and hillshade

    Author: Samson Williams 
    """
    
    ROOT = "D:/reference/Ausseabed/"
    BRANCH = "/FP Geotiff"
    INPATH = ROOT + voyage_input + BRANCH
    
    # If the voyage ID can't be found prompt again
    while not pathlib.Path(INPATH).exists():
        print("\nI can't find the voyage ID: " + voyage_input)
        VOYAGE_ID = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
        ROOT = "/reference/AusSeabed/"
        BRANCH = "/FP Geotiff"
        INPATH = ROOT + VOYAGE_ID + BRANCH
        if VOYAGE_ID == "exit":
            sys.exit("\nBye-bye")
    
    os.chdir(INPATH)
    for file in (set(glob.glob("*.tif*")) - set(glob.glob("*Hillshade.tif*") or glob.glob("*HS.tif*") or glob.glob("*OV.tif*"))):

        time_start = time.perf_counter()
        print('\nReading {:} ...'.format(file))
        
        #Define the input and temp file name 
        in_name = file
        stem_name = str(pathlib.Path(file).stem)
        cog_temp = stem_name + '_OV_temp.tiff'
        hillshade_temp = stem_name + '_HS_temp.tiff'
        cog_name = stem_name + '_OV.tiff'
        hillshade_name = stem_name + '_HS.tiff'

    
        image =  gdal.Open(in_name)
            
        translate_options = gdal.TranslateOptions(stats = True, creationOptions = 
                                                      [
                                                       'COMPRESS=DEFLATE',
                                                       'TILED=YES',
                                                       'BIGTIFF=IF_SAFER',
                                                       'COPY_SRC_OVERVIEWS=YES'
                                                       ])
            
        print('\nTranslating {:} ...'.format(file))
        gdal.Translate(str(cog_temp), str(in_name), options = translate_options)
        
        hillshade_options = gdal.DEMProcessingOptions(
            creationOptions = 
            ['COMPRESS=DEFLATE',
             'TILED=YES',
             'BIGTIFF=IF_SAFER',
             'COPY_SRC_OVERVIEWS=YES'], 
            azimuth = 30, 
            altitude = 45, 
            zFactor = 2, 
            scale = 1)
        
        print('\nCreating hillshade for {:} ...'.format(file))
        gdal.DEMProcessing(str(hillshade_temp), str(in_name), "hillshade", options = hillshade_options)

        for temp_name in cog_temp, hillshade_temp: 
            if os.path.getsize(file) < 10**8:
                image.BuildOverviews("AVERAGE", [2,4,8,16,32])
            else:
                image.BuildOverviews("AVERAGE", [2,4,8,16])
            
            translate_options2 = gdal.TranslateOptions(stats = True, creationOptions = 
                                                      [
                                                       'COMPRESS=DEFLATE',
                                                       'TILED=YES',
                                                       'BIGTIFF=IF_SAFER',
                                                       'COPY_SRC_OVERVIEWS=YES',
                                                       'ZLEVEL=9'
                                                       ])
            if temp_name == cog_temp:
                print('\nFinal COG translation {:} ...'.format(file))
                gdal.Translate(str(cog_name), str(cog_temp), options = translate_options2)
            else:
                print('\nFinal hillshade translation {:} ...'.format(file))
                gdal.Translate(str(hillshade_name), str(hillshade_temp), options = translate_options2)



        for file in glob.glob("*temp*"):
            os.remove(file)
            
        time_end = time.perf_counter()
        
        if time_end-time_start > 60:
            print('\nImage processed in {:.2f} min'.format((time_end-time_start)/60))
        else:
            print('\nImage processed in {:.2f} sec'.format(time_end-time_start))

    
   
    if glob.glob("*.tiff") == []:
        print("\nNo GEOTIFFS were found for the voyage:" + VOYAGE_ID)
                
                
    image = None
    
    t1 = time.perf_counter()

    print('\nTotal completion time: {:.2f} min'.format((t1-t0)/60))
    
    return cog_name, hillshade_name

# Prompt for entering voyage name
voyage = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()

ausseabed_vis(voyage)