# ------------------------------------------------------------------------------------------------------------------
# File: voxel_expansion
# Description: takes the base voxels csv file (voxels.csv) for a unit and based on the desired grid size
#   generates a voxel database (unit_A_voxels.csv) for A* pathing across that unit.
# Author(s): G.LC
# Affiliation(s): Inovation Team (CDG)
# Version: 0.0
# Note(s):
# ------------------------------------------------------------------------------------------------------------------

# Constants
Nx = 241
Ny = 97
Nz = 27
types = ['s', 'g', 'o', 'start', 'goal', 'obstacle']

# Read in the base voxel data file (voxels.csv), this file must be calibrated per unit
# then generate the mesh from the base voxel data
with open(r'AppData\voxels.csv') as ifile:
    for lines in ifile:
        line = lines.strip().split()
        print(line)