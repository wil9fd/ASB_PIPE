#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 16:37:42 2021

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry geotiffs and output hillshade and overlays 

@version: 1.0
"""

## Package Setup
import time
from osgeo import gdal
import os
import glob
import pathlib


def make_vis_layers(root_input, voyage_input):

    """
    Brief:  This function finds all '*.tiff' files for a voyage, 
            then uses GDAL to produce a hillshade and a COG (overlay) for each TIFF.
       
    ***WARNING: THIS FUNCTION ASSUMES ALL TIFF FILES IN THE DIRECTORY ARE DTMs***

    Parameters: Root path, Voyage ID

    Return: COG and hillshade

    Author: wil9fd
    """
   
    # Start timer
    t0 = time.perf_counter()

    # ROOT is setup to be run from HPC
    branch = "/FP Geotiff"
    inpath = root_input + voyage_input + branch
    if 'Outputs' not in os.listdir(inpath):
        os.mkdir(inpath + "/Outputs")
    outpath = inpath + "/Outputs/"
    
    # Set the working directory to the inpath
    os.chdir(inpath)
        
    # Loop through all the tiff files in the folder
    # Exclude files with these strings (hillshade, HS, OV) in it's name
    for file in (set(glob.glob("*.tif*")) - set(glob.glob("*Hillshade.tif*") or glob.glob("*HS.tif*") or glob.glob("*OV.tif*"))):
        
        os.chdir(inpath)
        
        time_start = time.perf_counter()
        print('\nReading {:} ...'.format(file))
        
        #Define the input and temp file name 
        in_name = file
        stem_name = str(pathlib.Path(file).stem)
        cog_temp = outpath + stem_name + '_OV_temp.tiff'
        hillshade_temp = outpath + stem_name + '_HS_temp.tiff'
        cog_name = outpath + stem_name +'_OV.tiff'
        hillshade_name = outpath + stem_name + '_HS.tiff'
        stats_name = outpath + stem_name + '_stats.txt'

        # Open the tiff
        image =  gdal.Open(in_name)
            
        # First translate
        translate_options = gdal.TranslateOptions(creationOptions = 
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

                # Do the second translate for the hilshade and COG
                translate_options2 = gdal.TranslateOptions(creationOptions = 
                                                        ['COMPRESS=DEFLATE',
                                                        'TILED=YES',
                                                        'BIGTIFF=IF_SAFER',
                                                        'COPY_SRC_OVERVIEWS=YES',
                                                        'ZLEVEL=9'])
            else:
                image.BuildOverviews("AVERAGE", [2,4,8,16])
                
                # Do the second translate for the hilshade and COG
                translate_options2 = gdal.TranslateOptions(creationOptions = 
                                                        ['COMPRESS=DEFLATE',
                                                        'TILED=YES',
                                                        'BIGTIFF=YES',
                                                        'COPY_SRC_OVERVIEWS=YES',
                                                       'ZLEVEL=9'])
            
            
            
            
            if temp_name == cog_temp:
                print('\nFinal COG translation {:} ...'.format(file))
                gdal.Translate(str(cog_name), str(cog_temp), options = translate_options2)
            else:
                print('\nFinal hillshade translation {:} ...'.format(file))
                gdal.Translate(str(hillshade_name), str(hillshade_temp), options = translate_options2)

        
        # Calculate statistics 
        print('\nCalculating statistics for {:} ...'.format(file))
        
        
        info = gdal.Info(cog_name, stats=True)
        with open(stats_name, "w") as text_file:
            text_file.write(info)
                
        
        time_end = time.perf_counter()
        
        if time_end-time_start > 60:
            print('\nImage processed in {:.2f} min'.format((time_end-time_start)/60))
        else:
            print('\nImage processed in {:.2f} sec'.format(time_end-time_start))
    
    image = None
    
    for file in glob.glob("*.ovr"):
        os.replace(file, 'Outputs/' + file)
        
    os.chdir(outpath)
    # Remove temp files
    for file in glob.glob("*temp*"):
        os.remove(file)    

    # Notification of empty folder
    if glob.glob("*.tiff") == []:
        print("\nNo GEOTIFFS were found for the voyage:" + voyage_input)
    
    t1 = time.perf_counter()

    print('\nTotal completion time: {:.2f} min\n\n'.format((t1-t0)/60))
