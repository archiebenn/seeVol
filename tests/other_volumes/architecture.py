# architecture.py - testing seevol visibility on architectural volumes (.glb files)
# 3d models downloaded from: https://www.innerscene.com/tools/library/3d-parts/

from pathlib import Path
import trimesh
import numpy as np
import seevol

# data directory
data_dir = Path(__file__).resolve().parent

# load .glbs
football_scene = trimesh.load(data_dir/"football-stadium.glb")
bus_scene = trimesh.load(data_dir/"bus-terminal.glb")


def glb_to_npy(mesh, voxel_target):

    # concatenate these meshes' faces and vertices together into a single array
    mesh = trimesh.util.concatenate(list(mesh.geometry.values())) 

    # size in x,y,z
    print(mesh.extents) 

    # set the target voxels per axis: this then adjusts pitch during voxelisation
    target_voxels_per_axis = voxel_target
    pitch = mesh.extents.max() / target_voxels_per_axis

    # convert to voxels based on pitch
    voxels = mesh.voxelized(pitch=pitch)  # shell only, skip .fill()

    # set dtype to uint8 for seevol
    vol = voxels.matrix.astype(np.uint8)

    print("shape:", vol.shape)
    print("dtype:", vol.dtype)
    print("memory:", vol.nbytes / 1e6, "MB")

    return vol

# run .glb -> .npy -> seevol -> pyvista visualiser
seevol.visibility_visualiser(glb_to_npy(football_scene, 150), view_type="mip", verbose=True)
