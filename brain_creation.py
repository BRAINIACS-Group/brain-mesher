# -*- coding: utf-8 -*-
"""
Brain creator 

Created on Thu Jun 15 09:34:00 2023

@author: grife

This script runs the full execution required to create a 3D brain model from a
freesurfer aseg file.

Input file given by path + fileIn
Preferences for model creation are defined in ConfigFile class
Output is a folder Models created in current working directory

main - the main function of the script
"""

from BrainHexMesh import BrainHexMesh
from mesh.PostProcessorFactory import PostProcessorFactory
from point_cloud.PointCloud import PointCloud
from config.Config import ConfigFile
from voxel_data import Preprocessor
from writers.aseg_manipulate import create_aseg
from writers.Writers import Writer

def run(config):

    brainCreator = BrainHexMesh(config)

    # Writes configuration preferences to output location
    config.open_config_file()
    config.write_preamble()

    # Gets aseg data as 3D of segmentation labels in voxels
    data = brainCreator.import_data()

    # Homogenizes data label according to Materials label as defined in Config class
    data = brainCreator.homogenize_data(data)

    # Pre-processes data to ensure valid mesh base on config setting:
    preprocessor = Preprocessor.PreProcessorFactory.get_preprocessor(config, data)
    assert isinstance(preprocessor, Preprocessor.IPreprocessor)
    data_new = preprocessor.preprocess_data()
    create_aseg(config.get("file_in_path"), config.get("file_in"), config.get("file_out_path"), config.get("fileout"),
                data_new)

    # Creates point cloud from voxel data
    pointCloud = PointCloud()
    pointCloud.create_point_cloud_from_voxel(data_new)

    # Creates mesh from point cloud
    mesh = brainCreator.make_mesh(pointCloud.pcd)
    brainCreator.clean_mesh(mesh)

    # Moves mesh to the center of the corpus callosum
    mesh.center_mesh_by_region()

    # Wrapping of post-processing operations (operation selection defined in config file)
    post_processor = PostProcessorFactory.get_post_processor(mesh, config)
    post_processor.post_process()

    # Close config file write out
    config.close_config_file()

    return mesh


def write(mesh_to_write, file_out_path, fileout, file_types=None):
    if file_types is None:
        file_types = ['vtk', 'ucd']
    for fileType in file_types:
        print("########## Writing data as a " + fileType.upper() + " file ##########")
        writer = Writer()
        writer.openWriter(fileType, fileout, file_out_path)
        writer.writeMeshData(mesh_to_write)
        writer.closeWriter()


if __name__ == "__main__":
    file_path_in = "./IOput/in"
    file_in = "aseg.mgz"
    file_path_out = "./IOput/out"
    file_out = "full_brain_model"

    # Model type options: basic_fullcsf, basic_partilacsf, basic_nocsf
    config = ConfigFile(file_path_in, file_in, file_path_out, file_out, model_type='basic_nocsf')
    mesh = run(config)
    write(mesh, config.get('file_out_path'), config.get('fileout'))



