from geo.Geoserver import Geoserver
from zipfile import ZipFile
import pathlib
import os 
import glob
import sys

class ASB:

    def __init__(self):       
        pass


    def get_voyage_folder(self):

        self.root_path = "/datasets/work/ncmi-gsm/reference/AusSeabed/"

        self.voyage_id = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()
        # If the voyage ID can't be found prompt again
        while not pathlib.Path(self.root_path + self.voyage_id).exists():
            print("\nI can't find the voyage ID: " + self.voyage_id)
            self.voyage_id = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
    
            if self.voyage_id == "exit":
                sys.exit("\nBye-bye")

        self.voyage_path = pathlib.Path(self.root_path + self.voyage_id)
        os.chdir(self.voyage_path)

   
    def logins(self):
        self.usrnm = input('\nInput Geoserver username: ')

        if self.usrnm.lower() == "exit":
            sys.exit("\nBye-bye")

        self.pword = input('\nInput geoserver password: ')

    
    def connect(self):
        try:
            self.geo = Geoserver('https://www.cmar.csiro.au/geoserver', username=self.usrnm, password = self.pword)
        except:
            print('\nGeoserver connection could not be established. Check username and password. Type exit to leave.\n')
            self.logins()
    

    def publish_overlays(self):

        for file in glob.glob("FP Geotiff/Outputs/*OV.tiff") :
            name = pathlib.Path(file).stem
            try:
                self.geo.create_coveragestore(layer_name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'Bathymetry_transparent', workspace = 'AusSeabed')
                print('\nOverlay {:} has been created and published'.format(name))
            except Exception:
                raise Exception


    def publish_hillshades(self):

        for file in glob.glob("FP Geotiff/Outputs/*HS.tiff") :
            name = pathlib.Path(file).stem
            try: 
                self.geo.create_coveragestore(layer_name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'Bathymetry_hillshade', workspace = 'AusSeabed')
                print('\nHillshade {:} has been created and published'.format(name))
            except Exception:
                raise Exception


    def publish_shapefile(self):
        for file in glob.glob("Shapefile/Outputs/*.shp") :
            zip_file = os.path.splitext(file)[0]+'.zip'

            with ZipFile(zip_file, 'w') as zipf:
                zipf.write(file)

        for file in glob.glob("Shapefile/Outputs/*.zip") :
            name = pathlib.Path(file).stem

            try:
                self.geo.create_datastore(name = name, path = file, workspace = 'AusSeabed')
                self.geo.publish_style(layer_name = name, style_name = 'BBOX', workspace = 'AusSeabed')
                print('\nShapefile {:} has been created and published'.format(name))
            except Exception:
                raise Exception

     
asb = ASB()
asb.get_voyage_folder()
asb.logins()
asb.connect()
asb.publish_overlays()
asb.publish_hillshades()
asb.publish_shapefile()