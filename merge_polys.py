#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 10:17:42 2022

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry shapefiles and collect geometries into  

@version: 1.0
"""

## Package Setup
import time
import geopandas as gpd
from osgeo import ogr
import os
import glob
import pathlib


def merge_polys(root_input, voyage_input):

    """
    Brief:  This function finds all '*.shp' files for a voyage, 
            then uses OGR and Geopandas to produce a single feature and standard metadata fields.

    Parameters: Root path, Voyage ID

    Return: Shapefile
    
    Author: wil9fd
    """
    t0 = time.perf_counter()
    
    # ROOT is setup to be run from HPC
    branch = "/Shapefile"
    inpath = root_input + voyage_input + branch
    
    
    # Set the working directory to the inpath
    os.chdir(inpath)
    if 'Outputs' not in os.listdir():
        os.mkdir('Outputs')
    
    # Loop through all the .shp files in the folder
    # Exclude files without the "cvrage(A)" suffix
    for file in set(glob.glob("*.shp")) - set(glob.glob("*merged*")):
         
            time_start = time.perf_counter()
            print('\nReading {:} ...'.format(file))
            #Define the input and temp file name 
            in_name = file
            stem_name = str(pathlib.Path(file).stem)
            out_name = inpath + '/Outputs/'+ stem_name +'_merged.shp'
            
            # Open the shp
            shape =  gpd.read_file(in_name)
            bounds = shape[['geometry']]
            m_poly = bounds.dissolve()
            
            # Define the metadata fields
            schema = [
                'SURVEY_ID',
                'SURV_NAME',
                'START_DATE',
                'END_DATE',
                'RESOLUTION',
                'START_LOC',
                'END_LOC',
                'PLAT_CLASS',
                'PLAT_NAME',
                'PROD_TYPE',
                'SENSR_TYPE',
                'DATA_URL',
                'META_URL',
                'VERT_DATUM',
                'AREA_KM2'
                ]
            
            # save the GeoDataFrame
            m_poly.to_file(driver = 'ESRI Shapefile', filename = out_name)
            
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(out_name, 1)
            
            # Write new fields to shapefile
            for field in schema:
                fldDef = ogr.FieldDefn(field, ogr.OFTString)
                
                if field == ['AREA_KM2']:
                    fldDef = ogr.FieldDefn(field, ogr.OFTReal)
                    fldDef.SetPrecision(4)
                    
                fldDef.SetWidth(32)
                layer = dataSource.GetLayer()
                layer.CreateField(fldDef)
                
            layer.DeleteField(0)
            
            time_end = time.perf_counter()
            
            
            if time_end-time_start > 60:
                print('\nShapefile merge completed in {:.2f} min'.format((time_end-time_start)/60))
            else:
                print('\nShapefile merge completed in {:.2f} sec'.format(time_end-time_start))

    t1 = time.perf_counter()
    
    if t1-t0 > 60:
        print('\nTotal polygon merge time {:.2f} min\n\n'.format((t1-t0)/60))
    else:
        print('\nTotal polygon merge time {:.2f} sec\n\n'.format(t1-t0))
        
    # Notification of empty folder
    if glob.glob("*.shp") == []:
        print("\nNo SHAPEFILES were found for the voyage:" + voyage_input)
