# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 01:08:29 2022

@author: wil9fd
"""

from lxml import etree
import re
import geopandas as gpd


def get_namespaces(file_name):
    root = etree.parse(file_name).getroot()
    nsmap = {}
    for ns in root.xpath('//namespace::*'):
        if ns[0]: # Removes the None namespace, neither needed nor supported.
            nsmap[ns[0]] = ns[1]
    return nsmap

def get_survey_id(file_name):
    patterns = "(in\d\d\d\d_\w\d\d)|(in\d\d_\w\d\d)|(ss\d\d\d\d_\w\d\d)|(ss\d\d_\w\d\d)|(ga-\d\d\d\d)"
    survey_id_group = re.search(patterns,file_name,flags = re.I)
    survey_id = survey_id_group.group(1)
    return survey_id

def get_survey_name(file_name):
    # No indicators are in xml metadata or in file name so this is not possible
    return None

def get_filename(file_name):
    filename = str(file_name)
    return filename
    
def get_licence():
    licence = "[CCBY 4.0](https://creativecommons.org/licenses/by/4.0/)"
    return licence

def get_source(): 
    source = "CSIRO"
    return source

def get_prin_invest():
    pass 

def get_start_date(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    start_date_path = 'gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition'
    start_date = (root.find(start_date_path, nsmap)).text
    return start_date

def get_end_date(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    end_date_path = 'gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition'
    end_date = (root.find(end_date_path, nsmap)).text
    return end_date    

def get_resoution(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    resolution_path = 'gmd:spatialRepresentationInfo/gmd:MD_Georectified/gmd:axisDimensionProperties/gmd:MD_Dimension/gmd:resolution/gco:Measure'
    resolution = (root.find(resolution_path, nsmap)).text
    return resolution
    
def get_start_location(file_name):
    patterns = "(in\d\d\d\d_\w\d\d)|(in\d\d_\w\d\d)|(ss\d\d\d\d_\w\d\d)|(ss\d\d_\w\d\d)"
    if bool(re.match(patterns,file_name,flags = re.I)) is True:
        start_location = 'Hobart'
    else: 
        start_location = None
    return start_location

def get_end_location(file_name):
    patterns = "(in\d\d\d\d_\w\d\d)|(in\d\d_\w\d\d)|(ss\d\d\d\d_\w\d\d)|(ss\d\d_\w\d\d)"
    if bool(re.match(patterns,file_name,flags = re.I)) is True:
        end_location = 'Hobart'
    else: 
        end_location = None
    return end_location

def get_platform_class(file_name):
    patterns = "(in\d\d\d\d_\w\d\d)|(in\d\d_\w\d\d)|(ss\d\d\d\d_\w\d\d)|(ss\d\d_\w\d\d)"
    if bool(re.match(patterns,file_name,flags = re.I)) is True:
        platform_class = 'Research Vessel'
    else: 
        platform_class = None
    return platform_class

def get_platform_name(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    platform_name_path = 'gmi:acquisitionInformation/gmi:MI_AcquisitionInformation/gmi:platform/gmi:MI_Platform/gmi:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString'
    platform_name = (root.find(platform_name_path, nsmap)).text
    pattern = "(.*?)_"
    platform_name = (re.match(pattern,platform_name).group(0))
    if platform_name is not None:
        platform_name = platform_name[0:-1]
    if platform_name == "Investigator":
        platform_name = '[Investigator](http://vocab.nerc.ac.uk/collection/C17/current/096U/1)'
    return platform_name

def get_instrument_type(file_name):
    #This tool is intended only for multibeam
    product_type = 'Multibeam'
    return product_type

def get_sensor_type(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    sensor_type_path = 'gmi:acquisitionInformation/gmi:MI_AcquisitionInformation/gmi:platform/gmi:MI_Platform/gmi:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString'
    sensor_type = [name.text for name in root.findall(sensor_type_path, nsmap)]
    pattern = "_(.*)$"
    
    sensor = str(re.search(pattern,sensor_type[0]).group(0))
    for extra_sensor in sensor_type[1::]:
        sensor = sensor + (str(' & ' + str(re.search(pattern,extra_sensor).group(0))))

    sensor = sensor.upper()
    sensor = sensor.replace("_","")
    return sensor

def get_dataset_url(file_name):
    # No indicators are in xml metadata or in file name so this is not possible
    return None

def get_meta_url(file_name):
    # No indicators are in xml metadata or in file name so this is not possible
    return None
    
def get_vertical_datum(file_name, nsmap):
    root = etree.parse(file_name).getroot()
    vertical_datum_path = 'gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString'
    vertical_datum = root.findall(vertical_datum_path, nsmap)
    if len(vertical_datum) > 1:
        vertical_datum = vertical_datum[1].text
        pattern = 'VERT_DATUM\[(.*?)AUTHORITY\["(.*?)","(.*?)"\]\]'
        vertical_datum = re.findall(pattern,vertical_datum,re.DOTALL)
    else: 
        vertical_datum = None

    if vertical_datum is not None:
        vertical_datum = vertical_datum[0][1] + ':' + vertical_datum[0][2]
    else:
        vertical_datum = None
    return vertical_datum

def get_area(file_name):
    gdf = gpd.read_file(file_name)
    gdf = gdf['geometry'].to_crs({'proj':'cea'})
    area = float(gdf.area / 10**6)
    return area
