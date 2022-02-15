#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 16:22:44 2022

@author: wil9fd

@organisation: CSIRO

@detail: Take bathymetry shapefiles and collect geometries into  

@version: 1.0
"""

## Package Setup
import time
from osgeo import ogr
import os
import glob
import metadata as md
import csv


def import_metadata(root_input, voyage_input):

    """
    Brief:  This function finds all '*.xml' files for a voyage, 
            then uses lxml, re, OGR and Geopandas to populate metadata fields of 
            merged shapefiles.

    Parameters: Root path, Voyage ID 

    Return: Shapefile
    
    Author: wil9fd
    """
    t0= time.perf_counter()
   
    # ROOT is setup to be run from HPC
    branch_1 = "/Metadata"
    branch_2 = "/Shapefile/Outputs"
    inpath_1 = root_input + voyage_input + branch_1
    inpath_2 = root_input + voyage_input + branch_2
    
    
    os.chdir(inpath_2)
    # List all merged shapefiles and get their names
    shape_file_list = glob.glob("*_merged.shp", recursive=True)
    # List all metadata files and get their names
    os.chdir(inpath_1)
    meta_file_list = glob.glob("*_metadata.xml", recursive=True)
    
    area_list = []
    
    # Perform an elementwise matching algorithm that ties the xml file to its 
    # relevant shapefile 
    for meta_file in meta_file_list:
       for shp_file in shape_file_list:
           for schema in [meta_file.strip('_metadata.xml').split('_')]:
               if all(parts in shp_file for parts in schema):
        
                    time_start = time.perf_counter()
                    print('\nReading {:} ...'.format(meta_file))        
                    
                    # Open the shapefile and get the field names in a list
                    os.chdir(inpath_2)
                    driver = ogr.GetDriverByName('ESRI Shapefile')
                    dataSource = driver.Open(shp_file, 1)
                    layer = dataSource.GetLayer()
                    field_names = [field.name for field in layer.schema]
                    
                    # Calculate the area from the shapefile
                    area = md.get_area(shp_file)
                    
                    # Get all of the metadata field values from the xml 
                    os.chdir(inpath_1)
                    nsmap = md.get_namespaces(meta_file)
                    survey_id = md.get_survey_id(meta_file)
                    survey_name = md.get_survey_name(meta_file)
                    start_date = md.get_start_date(meta_file, nsmap)
                    end_date = md.get_end_date(meta_file, nsmap)
                    resolution = md.get_resoution(meta_file, nsmap)
                    start_location = md.get_start_location(meta_file)
                    end_location = md.get_end_location(meta_file)
                    platform_class = md.get_platform_class(meta_file)
                    platform_name = md.get_platform_name(meta_file, nsmap)
                    product_type = md.get_product_type(meta_file)
                    sensor_type = md.get_sensor_type(meta_file, nsmap)
                    dataset_url = md.get_dataset_url(meta_file)
                    metadata_url = md.get_meta_url(meta_file)
                    vertical_datum = md.get_vertical_datum(meta_file, nsmap)
                    
                    # List the values
                    field_values = [survey_id,survey_name,start_date,end_date,resolution,start_location, 
                                    end_location, platform_class, platform_name, product_type, sensor_type,
                                    dataset_url, metadata_url, vertical_datum, area]
                    
                    # Polulate the relevant fields with the respective value
                    for feature in layer:
                        for name, value in zip(field_names,field_values):
                            feature.SetField(str(name), str(value))
                            layer.SetFeature(feature)
                    
                    time_end = time.perf_counter()
                        
                        
                    if time_end-time_start > 60:
                        print('\nMetadata populated in {:.2f} min'.format((time_end-time_start)/60))
                    else:
                        print('\nMetadata populated in {:.2f} sec'.format(time_end-time_start))
                    
                    # List the areas of each file 
                    area_list.append([shp_file,float(area)])
    
    # Calculate the total area covered
    area_list.append(['Total',sum(item[1] for item in area_list)])
    
    # Save the areas as a csv
    with open("areas_km2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        os.chdir(inpath_1)
        writer.writerows(area_list)
                        
    t1 = time.perf_counter()
    
    if t1-t0 > 60:
        print('\nTotal metadata population time {:.2f} min\n\n'.format((t1-t0)/60))
    else:
        print('\nTotal metadata population time {:.2f} sec\n\n'.format(t1-t0))
    
    
        
    # Notification of empty folder
    if glob.glob("*.xml") == []:
        print("\nNo METADATA files were found for the voyage:" + voyage_input)
