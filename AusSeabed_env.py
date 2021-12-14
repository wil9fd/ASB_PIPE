# -*- coding: utf-8 -*-
"""
Created on Mon Dec  13 14:07:00 2021

@author: wil9fd

"""

from subprocess import run
from distutils.dir_util import copy_tree,remove_tree
from pathlib import Path

ENV = 'AusSeabed'


newenv = Path.home() / "anaconda3/envs" / ENV


def conda_create(environment):
    proc = run(["conda", "create", "-y", "--name", environment], text=True, capture_output=False, check=True)
    return proc.stdout

def conda_install_condaforge(environment, packages):
    proc = run(["conda", "install", "-y", "-c", "conda-forge", "--name", environment] + packages, text=True, capture_output=False, check=True)
    return proc.stdout
    

#base packages:
basepackages = ["numpy", "geos", "pyproj", "matplotlib", "rasterio","pdal", "python-pdal", "gdal", "entwine"]

print("Creating {} environment...".format(ENV))
out = conda_create(ENV)
print("Created {} environment. Messages:\n{}".format(ENV, out))

print("Installing packages in {}...\n".format(ENV))
out = conda_install_condaforge(ENV, basepackages)
print("Installed packages in {}. Messages:\n{}".format(ENV,out))