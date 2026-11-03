import seevol
import numpy as np

vol = np.fromfile("stag_beetle_832x832x494_uint16.raw", dtype=np.uint16)
vol = vol.reshape((494, 832, 832))  # z, y, x order — common convention for these datasets
np.save("stag_beetle.npy", vol)