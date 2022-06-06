from make_vis_layers import make_vis_layers
import pathlib
import sys

# Prompt for entering voyage name
voyage = input('\nPLEASE ENTER THE VOYAGE ID:\n').lower()

root_path = "//datasets/work/ncmi-gsm/reference/AusSeabed/"
# Set root path to the ASB reference folder 
# '''Note: this path is accessed throught putty on the HPC'''

# If the voyage ID can't be found prompt again
while not pathlib.Path(root_path + voyage).exists():
    print("\nI can't find the voyage ID: " + voyage)
    voyage = input('\nPLEASE ENTER THE VOYAGE ID AGAIN OR TYPE EXIT TO LEAVE:\n').lower()
    
    if voyage == "exit":
        sys.exit("\nBye-bye")

make_vis_layers(root_path, voyage)
