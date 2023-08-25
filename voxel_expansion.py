# ------------------------------------------------------------------------------------------------------------------
# File: voxel_expansion
# Description: takes the base voxels csv file (voxels.csv) for a unit and based on the desired grid size
#   generates a voxel database (unit_A_voxels.csv) for A* pathing across that unit.
# Author(s): G.LC
# Affiliation(s): Inovation Team (CDG)
# Version: 0.0
# Note(s): Unit A voxels.csv
# x, y, z, type, name
# 0, 0, 0, start, home
# 9, 9, 9, goal, goal
# -482000, 0, 0, obstacle, _x_limit
# 0, -1892000, 0, obstacle, _y_limit
# 0, 0, -1350000, obstacle, _z_limit
# -179000, 0, 1350000, obstacle, _dg32_upper_right_corner
# -92400, -253000, 1350000, obstacle, _dna_quant_a
# -264600, -353000, -1000000, obstacle, _sample_rack_a
# -381600, 0, -1160000, obstacle, _pre_amp_upper_right_corner
# -328600, -639342, -910000, obstacle, _32_deep_well_upper_right_corner
# -328600, -1409342, -1060000, obstacle, _mag_separator
# ------------------------------------------------------------------------------------------------------------------

# Constants
unit = 'A'
Nx = 241
Ny = 97
Nz = 27
types = ['s', 'g', 'o', 'start', 'goal', 'obstacle']

# Read in the base voxel data file (voxels.csv), this file must be calibrated per unit
# then generate the mesh from the base voxel data
with open(r'AppData\voxels.csv') as ifile:
    for lines in ifile:
        line = lines.strip().split()
        
        if line[0] != '#' and len(line) == 5:
            # Get the 
            a = 1
            
# Create the yz-plane chassis wall obstacle voxels
for j in range(Ny):
    for k in range(Nz):
        x = 1
        y = 1
        z = 1      
