<!-- omit in toc -->
# Contents
- [Introduction:](#introduction)
- [Installation:](#installation)
- [Operation:](#operation)
- [Updating:](#updating)
- [Uninstall:](#uninstall)
- [Details:](#details)
  * [Main functions:](#main-functions)
    + [make_vis_layers.py:](#make-vis-layers.py-)
    + [make_contours.py:](#make-contours.py-)
    + [merge_polys.py:](#merge-polys.py-)
    + [import_metadata.py:](#import-metadata.py-)
  * [Limitations:](#limitations)
    + [Paths:](#paths)
    + [Filenames:](#filenames)
    + [Changes to standards:](#changes-to-standards)

# Introduction:
AusSeabed is Australia’s seabed mapping coordination program. The aim of the program is to improve seabed data access to the community.
ASB_PIPE is a set of tools written in Python to aid in the automation of publishing L3 AusSeabed bathymetry data products.

![ASB (1)](https://user-images.githubusercontent.com/95448591/153500148-6a82fc6e-185e-4d19-8ff5-63260447f298.jpg)


# Installation: 
_**The installation and application of the pipeline are performed through PUTTY on CSIRO's HPC (High Powered Computing) server.**_
* Open remote access and login to the bracewell-HPC server
* Open Putty
* Login to the MBSystem server 
    * See (https://confluence.csiro.au/x/nDf9Xw) for help.
* Login as prompted
* 
**Install conda and setup the ASB environment in HPC's PUTTY shell as previously described via;**
```
git clone -c core.autocrlf=false https://github.com/wil9fd/ASB_PIPE.git
bash ASB_PIPE/setup.sh

```
___

**NOTE:** 
* _The installation will automatically start conda, activate the environment and cd into the ASB_PIPE directory._
___

# Operation:
To run a program e.g. asb_vis_beta.py you must **ensure your conda ASB env is active within PUTTY**

Then run a la; 
```
python asb_pipe.py

```
>_Ensure you explicity define the path to the script. i.e. python path/to/script.py_

# Updating:
Simply paste the following into PUTTY:
```
cd
rm -rf ASB_PIPE
git clone -c core.autocrlf=false https://github.com/wil9fd/ASB_PIPE.git
exec bash

```

# Uninstall:
Simply paste the following into PUTTY:
```
bash uninstall.sh

```

# Details: 
ASB_PIPE consists of several scripts which produce AusSeabed geotiff, shapefile and metadata products.
The all encompasing master script is dubbed 
* ```asb_pipe.py```

Sub-scripts can be run individually by envoking them with the same method as above: 
* ```asb_vis_layers.py```
* ```asb_contours.py```
* ```asb_polys.py```
* ```asb_metadata.py```


## Main functions: 

### make_vis_layers.py:
  **make_vis_layers** searches the FP Geotiff folder of a voyage directory, then loops through all Geotiffs creating cloud optimized geotiffs, hillshade and stats files in an output folder ready for publishing. 
  
The workflow used was created by Geoscience Australia to be used in their version of an AusSeabed Pipeline (https://github.com/ausseabed/processing-pipeline#gdal), it was adapted to run inside a conda environment and python scripts with the following workflow:

_Geotiff → gdal_optimized_gtiff & gdal_hillshade  → gdal_build_overviews → gdal_translate → gdal_optimized_gtiff & gdal_hillshade_

The GDAL python functions used are: 
* ```gdal.Translate``` (For COG and Hillshade)
* ```gdal.DEMProcessing``` (For Hillshade)
* ```gdal.Dataset.BuildOverviews``` (For COG and Hillshade)
* ```gdal.Info``` (For Stats File)

### make_contours.py:
**make_contours** also searches the FP Geotiff folder of a voyage directory, looping through all Geotiffs creating 100 m contour shapefiles for each Geotiff. 

The GDAL pythonfunction used is: 
* ```gdal.ContourGenerate```

### merge_polys.py:
**make_polys** searches the Shapefile folder of the input voyage directory, and merged using GeoPandas all features (polygons) within the file. OGR is then used to create a new field schema for the merged polygon based on the AusSeabed Web Mapping Service minimum metadata requirements for L3 products:

![image](https://user-images.githubusercontent.com/95448591/153442344-4943abe6-1ca2-4828-a875-659b7859be20.png)

The GeoPandas function used to collect geometries are:
* ```geopandas.dissolve```

The OGR function used to 
* ```ogr.FieldDefn```
* ```ogr.CreateField```

### import_metadata.py:
**import_metadata** searches the Shapefile folder created by **make_polys**, and matches this file with its corresponding metadata file. It then populates the newly created fields using GeoPandas, lxml and OGR. An additional csv file of each file's area and the sum of the areas is created in the metadata folder.

The GeoPandas function used to calculate area is:
* ```geopandas.geodataframe.area``` 

>_The layer is projected to a flat surface; cea (cylyndrical equal area) to preserve polygonal area._

The lxml function used to return the metadata values is:
* ```lxml.etree.parse```

The OGR function used to append the values to the fields are:
* ```ogr.SetField```
* ```ogr.SetFeature```

___

**NOTE:** 
* The xml PATHS are pre-defined within the code so any changes to xml structure must be updated in the ```metadata.py``` script.
* **If any field value cannot be found it will be left blank so it is important to review the fields before publishing.**
* The matching of meta and shapefiles relies on the naming conventions outlined in: https://confluence.csiro.au/x/PJgqY
 
    Pattern - {SurveyID/SurveyName/Location}_{ProductType}_{SurveyYearEnd}_{Resolution}_[{Sensor_Identifier}]_{VerticalDatum}_{CRS format=EPSG}_[{VersionIdentifier}].{FormatExtension}

    {Mandatory} ({Conditional})[{Optional}] 

    Example - in2019_e01_Bathymetry_0p5m_EM710_CUBE_EGM2008_EPSG32753_20201214[T052921Z].tif
___

## Limitations: 

### Paths:
The code is explicity written to search for the voyage in ```/datasets/work/ncmi-gsm/reference/AusSeabed/```, so if the datastorage structure changes the path will need updating. This must be updated in all scripts with the ```asb_``` prefix.

### Filenames: 
The shapefile field population from the xml is contingent upon the shapefile name containing the contents of the xml filename without the 'metadata' suffix. This makes the field population impossible in some older voyages where the naming conventions are inconsistent.  

### Changes to standards: 
If any AusSeabed product standards change in the future, the scripts will have to be run for each voyage again. 
