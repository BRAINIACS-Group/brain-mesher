"""
Created on Wed May 10 09:11:56 2023

@author: grife
"""
import warnings

import numpy as np

import voxel_data.voxel_data_utils as bm
from mesh.Mesh import Mesh
from readers import Importer as inp


class BrainHexMesh:
    """
    A class used to facilitate 3D brain model creation.

    """
    
    def __init__(self, configFile):
        self.VOXEL_SIZE = 1
        self.config = configFile
        self.material_labels = configFile.MATERIAL_LABELS
        self.configured = True

    @staticmethod
    def __get_data__(path, file):
        importer = inp.ImportFromFile(path, file)
        return importer.getData()
    
    def import_data(self, path="", file=""):

        assert self.configured, "config file has not been set for this. Please run config(cf -> ConfigFile) before importing data"

        if (path == "") and (file == ""):
            path = self.config.get('file_in_path')
            file = self.config.get('file_in')
        data = BrainHexMesh.__get_data__(path, file)

        values_in_data = list(np.unique(data))
        if not values_in_data.count(251):
            warnings.warn("There is no corpus callosum in this data set")
        return data
    
    def homogenize_data(self, data, unusedLabel="Unused"):
        """
        Homogenizes data based on materials labels

        Parameters
        ----------
        data : 3D array
            voxel data
        unusedLabel : string
            label name of voxel label numbers to be removed at the end of the model creation
            
        Outputs
        ----------
        3D array:
            3D data array of voxels with label numbers
        """
        # Homogenize labels
        label_number = self.material_labels.labelsMap.get(unusedLabel, [0])[0]
                    
        # Replace regions with multiple labels with only one label, if label is not required replace with unused/0
        data = self.material_labels.homogenize_material_labels(data, replace=label_number)
        return data

    def make_mesh(self, pc_data):
        """
        Makes mesh from voxel point Cloud data

        Parameters
        ----------
        pc_data : nx4 array
            point data of n points with columns 0:3 specifying coordinates 
            and column 3 giving the material label
            
        Outputs
        ----------
        mesh: Mesh
            mesh object
            
        Errors
        ----------
        Error raised if voxel size has not been specified, i.e. pre-processing has not been performed
        """
        
        assert hasattr(self, "VOXEL_SIZE"), "Voxel size has not been specified, ensure" + \
            " you have run preprocess() method on voxel data before progressing"
            
        print("########## Creating mesh from point cloud ##########")
        mesh = Mesh()        
        mesh.create_mesh_from_Point_Cloud(pc_data,2)
        return mesh
    
    def clean_mesh(self, mesh, wm=False):
        """
        Cleans mesh by removing/replacing poorly connected elements and/or 
        nodes on the followign boundaries:\n
        1. Grey matter, if CSF added\n
        2. Outer boundary\n
        3. White matter, if specified

        Parameters
        ----------
        mesh: Mesh
            mesh object to be cleaned
        wm: boolean, optional
            parameter to indiciate white matter boundary cleaning needed
            Default is True
            
        """
        
        if self.config.get('add_csf'):
            # Clean grey matter boundary
            print("####### Cleaning grey matter boundary #######")
            mesh.clean_mesh(elementsNotIncluded=[24], replace=24)
            
        # Clean outer boundary
        print("####### Cleaning outer boundary #######")    
        mesh.clean_mesh()
        
        # Clean white matter boundary
        if wm:
            print("####### Cleaning white matter boundary #######")
            mesh.clean_mesh(elementsNotIncluded=[24,3], replace=2)
        
        # Replace any white matter on boundary with grey matter
        elementsOnBoundary = mesh.locate_elements_on_boundary(elementsNotIncluded=[24])
        mesh.replace_outer_region(2, elementsOnBoundary)

    @staticmethod
    def add_region(cc_data, current_data, region_value):
        """
        ADd region to voxel data by overwriting current data

        Parameters
        ----------
        cc_data : 3D array
            voxel data of new region to be added
        current_data : 3D array
            voxel data to eb overwritten
        region_value : 3D array
            label to be assigned to overwritten data
            
        Errors
        ----------
        Error raised cc_data and current_data are not the same size
        """
        
        assert np.all(cc_data.shape == current_data.shape),"Region associated with added data is not the same size as the current data set"
        bm.override_voxel_data(cc_data, current_data, region_value)




