# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# helpers.py - Small helper functions to be used alongside seeVol

import numpy as np

def binary_swap(vol):
    """
    Inverts a binary NumPy 0/1 volume for easy conversion.
    """

    # Source - https://stackoverflow.com/a/56594688
    # Posted by yatu, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-11-26, License - CC BY-SA 4.0
    # with bitwise XOR operator (^): 1^1 = 0, 0^1 = 1, so can be used to swap 1 <-> 0 easily
    vol_swapped = np.where((vol == 0) | (vol == 1), vol ^ 1, vol)
    return vol_swapped


# TODO make function to extract only the surface voxels of a volume (non-interior)  
def get_voxel_surf():
    return False