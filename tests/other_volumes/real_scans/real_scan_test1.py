import seevol
import numpy as np
from pathlib import Path

data_dir = Path(__file__).resolve().parent

# luke leckie volume
vol = np.fromfile(data_dir / "BinaryROI1.raw", dtype=np.uint8)

# read the .dat file for to get volume info
print((data_dir / "BinaryROI1.dat").read_text()[:500]) 
# <Resolution X="654" Y="666" Z="538" T="1" />

# information contained within .dat indicated these as the shape
# reshape as (Z,Y,X), as this is the convention as data is stored X fastest, then Y, then Z
# convention is then slowest-> fastest in reshaping (independent of any numpy stuff, this is scanner info)  
vol = vol.reshape((538, 666, 654))
# transpose to (X, Y, Z)
vol = vol.transpose(2, 1, 0) 
# create bool array where non-0 = True, 0 = False, then convert that to binary 1/0  
vol = (vol != 0).astype(np.uint8)

# downscale vol  by factor - 
factor = 3
ds_vol = vol[::factor, ::factor, ::factor]

print(ds_vol.min()) # 0 - ideal
print(ds_vol.max()) # 1 - ideal

print("shape:", ds_vol.shape, "open voxels:", int(ds_vol.sum()))

# run visibility visualiser
seevol.visibility_visualiser(ds_vol, verbose=True)

# get open voxel coords
coords = np.argwhere(ds_vol == 1)

# run spatial visualiser
x,y,z = coords[100000]
assert(ds_vol[x, y, z]) == 1
seevol.spatial_visualiser(ds_vol, x0 =x, y0 =y, z0 =z)