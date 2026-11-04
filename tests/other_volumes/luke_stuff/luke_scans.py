import seevol
import numpy as np
from pathlib import Path

data_dir = Path(__file__).resolve().parent

# luke leckie volume
vol = np.fromfile(data_dir / "BinaryROI1.raw", dtype=np.uint8)

# information contained within .dat indicated these as the shape
vol = vol.reshape((538, 666, 654))
vol = (vol != 0).astype(np.uint8)

# downscale by factor of 10 to get about 56x67x65 
factor = 2
ds_vol = vol[::factor, ::factor, ::factor]

print(ds_vol.min()) # 0 - ideal
print(ds_vol.max()) # 1 - ideal

print("shape:", ds_vol.shape, "open voxels:", int(ds_vol.sum()))

# run visibility visualiser
seevol.visibility_visualiser(ds_vol, verbose=True)