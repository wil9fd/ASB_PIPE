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
from osgeo import gdal
import os
import glob
import pathlib
 

def make_vis_layers(root_input, voyage_input):

    """
    Brief:  This function finds all '*.tiff' files for a voyage, 
            then uses GDAL to produce a hillshade and a COG (overlay) for each TIFF.
       
    ***WARNING: THIS FUNCTION ASSUMES ALL TIFF FILES IN THE DIRECTORY ARE DTMs***

    Parameters: Voyage ID 

    Return: COG and hillshade

    Author: wil9fd
    """
   
    # Start timer
    t0 = time.perf_counter()

    # ROOT is setup to be run from HPC
    branch = "/FP Geotiff"
    inpath = root_input + voyage_input + branch
    
    # If the voyage ID can't be found prompt again
    while not pathlib.Path(root_input + voyage_input).exists():
        print("\nI can't find the voyage ID: " + voyage_input)
        voyage_input = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
        inpath = root_input + voyage_input + branch
        
        if voyage_input == "exit":
            sys.exit("\nBye-bye")
    
    # Set the working directory to the inpath
    os.chdir(inpath)
    
    # Loop through all the tiff files in the folder
    # Exclude files with these strings (hillshade, HS, OV) in it's name
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

        # Open the tiff
        image =  gdal.Open(in_name)
            
        # First translate
        translate_options = gdal.TranslateOptions(stats = True, creationOptions = 
                                                      ['COMPRESS=DEFLATE',
                                                       'TILED=YES',
                                                       'BIGTIFF=IF_SAFER',
                                                       'COPY_SRC_OVERVIEWS=YES'])
            
        
        print('\nTranslating {:} ...'.format(file))
        gdal.Translate(str(cog_temp), str(in_name), options = translate_options)
        
        # Create Hillshade
        hillshade_options = gdal.DEMProcessingOptions(creationOptions = 
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

        
        # Create overlay (depending on file size)
        for temp_name in cog_temp, hillshade_temp: 
           
            if os.path.getsize(file) < 10**8:
                image.BuildOverviews("AVERAGE", [2,4,8,16,32])
            else:
                image.BuildOverviews("AVERAGE", [2,4,8,16])
            
            
            # Do the second translate for the hilshade and COG
            translate_options2 = gdal.TranslateOptions(stats = True, creationOptions = 
                                                      ['COMPRESS=DEFLATE',
                                                       'TILED=YES',
                                                       'BIGTIFF=IF_SAFER',
                                                       'COPY_SRC_OVERVIEWS=YES',
                                                       'ZLEVEL=9'])
            
            if temp_name == cog_temp:
                print('\nFinal COG translation {:} ...'.format(file))
                gdal.Translate(str(cog_name), str(cog_temp), options = translate_options2)
            else:
                print('\nFinal hillshade translation {:} ...'.format(file))
                gdal.Translate(str(hillshade_name), str(hillshade_temp), options = translate_options2)


        # Remove temp files
        for file in glob.glob("*temp*"):
            os.remove(file)
            
        
        time_end = time.perf_counter()
        
        
        if time_end-time_start > 60:
            print('\nImage processed in {:.2f} min'.format((time_end-time_start)/60))
        else:
            print('\nImage processed in {:.2f} sec'.format(time_end-time_start))

    
    # Notification of empty folder
    if glob.glob("*.tiff") == []:
        print("\nNo GEOTIFFS were found for the voyage:" + voyage_input)
                
                
    image = None
    
    t1 = time.perf_counter()

    print('\nTotal completion time: {:.2f} min'.format((t1-t0)/60))

# Prompt for entering voyage name
voyage = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()

make_vis_layers("/datasets/work/ncmi-gsm/reference/AusSeabed/",voyage)