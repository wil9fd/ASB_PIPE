from subprocess import run
from distutils.dir_util import copy_tree,remove_tree
from pathlib import Path

ENV = "AusSeabed"

newenv = Path.home() / "Anaconda3/envs" / ENV_SPATIAL

def conda_create(environment, packages):
    proc = run(["conda", "create", "-y", "--name", environment] + packages, text=True, capture_output=False, check=True)
    return proc.stdout

#base packages:
basepackages = ["numpy","gdal", "geos", "pyproj", "matplotlib", "plotly", 
                "spyder", "rasterio", "pdal"]

print("Installing packages in {}...".format(ENV))
out = conda_install(ENV, basepackages)
print("Installed packages in {}. Messages:\n{}".format(ENV, out))
