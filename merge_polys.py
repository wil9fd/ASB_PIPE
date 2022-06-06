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
import dbf
import re


def merge_polys(root_input, voyage_input):

    """
    Brief:  This function finds all '*.shp' files for a voyage, 
            then uses OGR and Geopandas to produce a single feature and standard metadata fields.

    Parameters: Root path, Voyage ID

    Return: Shapefile
    
    Author: wil9fd
    """
       # Start timer
    t0 = time.perf_counter()

    # ROOT is setup to be run from HPC
    branch = "/Shapefile"
    inpath = root_input + voyage_input + branch
    if 'Outputs' not in os.listdir(inpath):
        os.mkdir(inpath + "/Outputs")
    outpath = inpath + "/Outputs/"
    
    # Set the working directory to the inpath
    os.chdir(inpath)
    
    # Loop through all the .shp files in the folder
    # Exclude files without the "cvrage(A)" suffix
    for file in set(glob.glob("*.shp")) - set(glob.glob("*merged*")):
         
            time_start = time.perf_counter()
            print('\nReading {:} ...'.format(file))
            #Define the input and temp file name 
            in_name = file
            stem_name = str(pathlib.Path(file).stem)
            prefix = r'(.*?)_AusSeabed_Outputs_Shapefile_'
            stem_name = re.sub(prefix, "",stem_name)
            out_name = inpath + '/Outputs/'+ stem_name +'_merged.shp'
            merge_polys.filename = stem_name +'_merged.shp'
            
            # Open the shp
            shape =  gpd.read_file(in_name)
            bounds = shape[['geometry']]
            m_poly = bounds.dissolve()
            
            # Define the metadata fields
            schema = [
                'SURVEY_ID',
                'SURV_NAME',
                'FILENAME',
                'LICENCE',
                'SOURCE',
                'PRIN_INVST',
                'DATE_START',
                'DATE_END',
                'RESOLUTION',
                'LOC_START',
                'LOC_END',
                'PLAT_CLASS',
                'PLAT_NAME',
                'INSTR_TYP',
                'SENSOR_TYP',
                'DATA_URL',
                'META_URL',
                'DATUM_VERT',
                'AREA_KM2'
                ]

            data_type = [
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "D",
                "D",
                "N",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "C",
                "N"
                ]
            

            out_path = pathlib.Path(out_name)
            # save the GeoDataFrame
            m_poly.to_file(driver = 'ESRI Shapefile', filename = out_path)

            dbf_out_name = inpath + '/Outputs/'+ stem_name +'_merged.dbf'
            with dbf.Table(dbf_out_name) as db:
                for field_name, field_type in zip(schema,data_type):
                    if field_type == "C":
                        field_string = str(field_name + ' ' + field_type + '(' + '254'+')')
                    elif field_type == "D":
                        field_string = str(field_name + ' ' + field_type)
                    elif field_type == "N":
                        field_string = str(field_name + ' ' + field_type + '(' + '19, 4'+')')

                    db.add_fields(field_string)
                db.delete_fields('FID')
         
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
