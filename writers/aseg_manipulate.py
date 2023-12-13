# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 13:47:49 2023

@author: grife
"""

import os
import nibabel as nb
import numpy as np
from voxel_data import voxel_data_utils as bm


def add_cc_data(fileInPath,homogenized_data):
    # Step 1: Using freesurfer and 'recon-all' create in outputs. Ensure aseg.mgz is created.
    t1_file_cc = "/".join([fileInPath, "in/cc.mgz"])
    t1_cc = nb.load(t1_file_cc)
    # t1.orthoview()
    cc_data = np.asarray(t1_cc.dataobj)

    cc_data = bm.create_binary_image(cc_data)
    bm.override_voxel_data(cc_data, homogenized_data, 251)


def remove_ventricle_data(data_new):
    current_dimensions = data_new.shape
    for x in range(current_dimensions[0]):
        if np.sum(data_new[x, :, :]) > 0:
            for y in range(current_dimensions[1]):
                if np.sum(data_new[x, y, :]) > 0:
                    for z in range(current_dimensions[2]):
                        if data_new[x, y, z] == 4:
                            data_new[x, y, z] = 0


def create_aseg(fileInPath, filename, fileoutpath, fileout, data_new, remove_ventricle=True):
          
    # Step 1: Using freesurfer and 'recon-all' create in outputs. Ensure aseg.mgz is created.
    t1_file = "/".join([fileInPath, filename])
    t1 = nb.load(t1_file)
    # t1.orthoview()
    data = np.copy(data_new)
    if remove_ventricle:
        remove_ventricle_data(data)

    # Now we can save the changed data into a new NIfTI file
    new_img = nb.Nifti1Image(data, affine=t1.affine, header=t1.header)
    pathOut = fileoutpath + "/tmp"
    file_in_split = filename.split(".")
    file_name_out = fileout + "_" + file_in_split[0]
    if len(file_in_split) == 1:
        file_name_out += '.mgz'
    else:
        file_name_out += '.' + file_in_split[1]
    if not os.path.exists(pathOut):
        os.mkdir(pathOut)
    nb.save(new_img, "/".join([pathOut, file_name_out]))
