# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 15:25:18 2022

@author: wil9fd

@detail: Take bathymetry geotiffs and output contour shapefiles 

@version: 1.0
"""

from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import time
import os
import glob

def make_contours(root_input, voyage_input):
    """
    Brief:  This function finds all '*.tif' files for a voyage, 
            then uses gdal, osr and ogr to create 100m contour grids.

    Parameters: Root path, Voyage ID 

    Return: Shapefile
    
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
        
        
        indataset1 = gdal.Open(file, gdal.GA_ReadOnly)
        
        in1 = indataset1.GetRasterBand(1)
        
        dst_filename = outpath + file + '_contour.shp'
        ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(dst_filename)        
        sr = osr.SpatialReference(indataset1.GetProjection())
        contour_shp = ogr_ds.CreateLayer('contour', sr)
        field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
        contour_shp.CreateField(field_defn)
        field_defn = ogr.FieldDefn("mdROS", ogr.OFTReal)
        contour_shp.CreateField(field_defn)
        
        intervals = list(range(-10000, 10000, 100))
        gdal.ContourGenerate(in1, 100, 0, intervals, 0, 0, contour_shp, 0, 1)
        ogr_ds = None
        del ogr_ds
        
        time_end = time.perf_counter()
        
        if time_end-time_start > 60:
            print('\nContours created in {:.2f} min'.format((time_end-time_start)/60))
        else:
            print('\nContours created in {:.2f} sec'.format(time_end-time_start))
            
    t1 = time.perf_counter()

    print('\nTotal completion time: {:.2f} min\n\n'.format((t1-t0)/60))
