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

    # with XOR operator (^): 1^1 = 0, 0^1 = 1, so can be used to swap 1 <-> 0 easily
    vol_swapped = np.where((vol == 0) | (vol == 1), vol ^ 1, vol)
    return vol_swapped
