from geo.Geoserver import Geoserver
from geoserver.catalog import Catalog
from xml.etree import ElementTree
import getpass
import requests
import zipfile 
import pathlib
import os 
import glob
import sys
import json 

class ASB:

    def __init__(self):       
        pass


    def get_voyage_folder(self):
        # Set the main directory to the reference-AusSeabed folder 
        self.root_path = "/datasets/work/ncmi-gsm/reference/AusSeabed/"
        self.root_path = r'C:\Users\wil9fd\ASB_geoserver\\'
        self.voyage_id = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()
        # If the voyage ID can't be found prompt again
        while not pathlib.Path(self.root_path + self.voyage_id).exists():
            print("\nI can't find the voyage ID: " + self.voyage_id)
            self.voyage_id = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
    
            if self.voyage_id == "exit":
                sys.exit("\nBye-bye")

        self.voyage_path = pathlib.Path(self.root_path + self.voyage_id)
        # Change the working directory to the relevant voyage
        os.chdir(self.voyage_path)

   
    def logins(self):
        # Prompt for Geoserver logins 
        self.usrnm = input('\nInput Geoserver username: ')

        if self.usrnm.lower() == "exit":
            sys.exit("\nBye-bye")

        self.pword = getpass.getpass('\nInput Geoserver password: ')

    # Connect to csiro's geoserver
    def connect(self):
        try:
            self.geo = Geoserver('https://www.cmar.csiro.au/geoserver', username=self.usrnm, password = self.pword)
            self.cat = Catalog('https://www.cmar.csiro.au/geoserver/rest', username=self.usrnm, password = self.pword)

        except:
            print('\nGeoserver connection could not be established. Check username and password. Type exit to leave.\n')
            self.logins()
    
    # Change the layer's xml to input the desired band name
    def change_band_name(self, coverage_name: str, band_name: str):
        url = 'https://www.cmar.csiro.au/geoserver/rest/workspaces/AusSeabed/coveragestores/{:}/coverages/{:}'.format(coverage_name, coverage_name)
        r = requests.get(url, auth = (self.usrnm, self.pword))
        tree = ElementTree.fromstring(r.content)
        tree.find('dimensions/coverageDimension/name').text = band_name
        #tree.find('serviceConfiguration').text = 'true'
        data = ElementTree.tostring(tree, encoding = 'unicode')
        #jsondict = g.json()
        #jsondict['coverage']['dimensions']['coverageDimension'][0]['name'] = band_name
        r_change_band_name = requests.put(url, auth = (self.usrnm, self.pword), data = data, headers = {'content-type': 'text/xml'})

    # Crawl throught the geotiff outputs folder and publish the overlays
    def publish_overlays(self):

        for file in glob.glob("FP Geotiff/Outputs/*OV.tiff"):
            name = str(pathlib.Path(file).stem)
            try:
                self.geo.create_coveragestore(layer_name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'Bathymetry_transparent', workspace = 'AusSeabed')
                self.change_band_name(coverage_name = name, band_name = 'ELEVATION')
                print('\nOverlay {:} has been created and published'.format(name))
            except Exception:
                raise
            
    # Crawl throught the geotiff outputs folder and publish the hillshades
    def publish_hillshades(self):

        for file in glob.glob("FP Geotiff/Outputs/*HS.tiff"):
            name = str(pathlib.Path(file).stem)
            try: 
                self.geo.create_coveragestore(layer_name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'Bathymetry_hillshade', workspace = 'AusSeabed')
                self.change_band_name(coverage_name = name, band_name = 'SHADED_RELIEF')
                print('\nHillshade {:} has been created and published'.format(name))
            except Exception:
                raise

            

    # Crawl throught the shapefiles folder, add all shapefiles and auxiliary files to zip file and publish 
    def publish_shapefile(self):
        os.chdir(str(self.voyage_path) + "/Shapefile/Outputs")

        stem_list = [pathlib.Path(file).stem for file in glob.glob("*.shp")]
                    
        for stem in stem_list:
            zip_file = stem + '.zip'
            with zipfile.ZipFile(zip_file, 'w') as zipf:
                for file in set(glob.glob(stem+'.cpg')+glob.glob(stem+'.dbf')+glob.glob(stem+'.prj')+glob.glob(stem+'.shp')+glob.glob(stem+'.shx')):
                    zipf.write(file)

        for file in glob.glob("*.zip"):
            name = pathlib.Path(file).stem

            try:
                self.geo.create_shp_datastore(store_name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'BBOX', workspace = 'AusSeabed')
                print('\nShapefile {:} has been created and published'.format(name))
            except Exception:
                raise Exception

            os.remove(file)

     
asb = ASB()
asb.get_voyage_folder()
asb.logins()
asb.connect()
asb.publish_overlays()
asb.publish_hillshades()
asb.publish_shapefile()