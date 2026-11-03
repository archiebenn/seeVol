# stag_beetle.py - visibility test on a stag beetle volume to test seevol/other dtypes

import seevol
import numpy as np
from pathlib import Path

data_dir = Path(__file__).resolve().parent

# stag beetle volume - 	(The stag beetle from Georg Glaeser, Vienna University of Applied Arts, Austria, 
# was scanned with an industrial CT by Johannes Kastner, Wels College of Engineering, Austria, 
# and Meister Eduard Gröller, Vienna University of Technology, Austria.)
# downloaded from: http://klacansky.com/open-scivis-datasets/
vol = np.fromfile(data_dir/"stag_beetle_832x832x494_uint16.raw", dtype=np.uint16)

# z, y, x order
vol = vol.reshape((494, 832, 832)) 

# simple strided downsample (fast, lossy - just picks every nth voxel)
small = vol[::3, ::3, ::3]  # e.g. 494x832x832 -> ~124x208x208

# pick based on vol.min() and max()
threshold = 900 

# threshold to binary 0/1
binary = (small > threshold).astype(np.uint8)

# run visualiser
seevol.visibility_visualiser(binary, verbose=True)