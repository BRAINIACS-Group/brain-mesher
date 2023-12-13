# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 08:49:33 2023

@author: grife
"""
import numpy as np
import voxel_data.voxel_data_utils as bm
from abc import ABC, abstractmethod
from scipy import ndimage
import warnings

class IpreProcessAction(ABC):
    """
    Command interface for additional preprocessing step outisde of cleaning
    """
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'performAction') and 
                callable(subclass.performAction) or 
                NotImplemented)
    
    @abstractmethod 
    def performAction(self, data, **kwargs):
        raise NotImplementedError;
        
class CleanLesion(IpreProcessAction):
    """
    Cleans added lesion to ensure smooth lesion boundary
    """
    
    def __init__(self,lesion_label):
        self.label = lesion_label
    
    def performAction(self, current_data):
        print("########## Cleaning Lesion ##########")
        ## TODO: Better creation of featureless lesion (possibly the same way featurless csf is created)
        newData = bm.create_binary_image(current_data, search=self.label)
        lesionOGSize = np.sum(newData)
        if lesionOGSize > 0:
            print("Lesion element size before: {}".format(lesionOGSize))
        
            structure1 = ndimage.generate_binary_structure(3,1)
            structure2 = ndimage.generate_binary_structure(3,3)
            
            newData = ndimage.binary_dilation(newData, structure=structure2, iterations=1).astype(int)
            newData = ndimage.binary_erosion(newData, structure=structure1, iterations=1).astype(int)
            newData = ndimage.binary_dilation(newData, structure=structure2, iterations=1).astype(int)
            newData = ndimage.binary_erosion(newData, structure=structure2, iterations=2).astype(int)
        
            hit_structure1 = np.ones((2,2,2))
            hit_structure1[0,1,0] = 0
            hit_structure2 = np.rot90(hit_structure1)
            hit_structure3 = np.rot90(hit_structure1, k= 2)
            hit_structure4 = np.rot90(hit_structure1, k= 3)
            hit_structure5 = np.rot90(hit_structure1,axes=(1,2))
            hit_structure6 = np.rot90(hit_structure5, k= 1)
            hit_structure7 = np.rot90(hit_structure5, k= 2)
            hit_structure8 = np.rot90(hit_structure5, k= 3)
            total_count = 0;
            count = 1
            iteration = 0
            while (count > 0 and iteration < 10):
                iteration += 1
                count = 0
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure1, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure2, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure3, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure4, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure5, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure6, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure7, fill=1)
                count += bm.hit_and_miss_3d_2x2x2(newData, hit_structure8, fill=1)
                total_count += count
            print("Lesion cleaned after {} iterations and {} elements added".format(iteration,total_count))
            
            count_removed = 0
            current_dimensions = current_data.shape
            for x in range(current_dimensions[0]):
                if (np.any(newData[x,:,:] == 1) or np.any(current_data[x,:,:] == self.label)):
                    for y in range(current_dimensions[1]):
                        if (np.any(newData[x,y,:] == 1) or np.any(current_data[x,y,:] == self.label)):
                            for z in range(current_dimensions[2]):
                                if newData[x,y,z] == 1:
                                    current_data[x,y,z] = self.label
                                if newData[x,y,z] == 0 and (current_data[x,y,z] == self.label):
                                    current_data[x,y,z] = 0;
            print("previous lesion replaced with non-lesion: {}".format(count_removed))
            finalSize = np.sum(newData)
            print("Lesion element size after: {}".format(finalSize))
            if (finalSize == 0):
                warnings.warn("No lesion elements found in data after cleaning")
        else:
            warnings.warn("No lesion elements found in data")
        
class AddEdemicTissue(IpreProcessAction):
    """
    Add layers of edemic tissue to outside of lesion
    """
    
    def __init__(self, lesion_label = 25, edemic_tissue_label = 29, layers = 1 ):
        self.label = lesion_label
        self.edemic_tissue_label = edemic_tissue_label
        self.layers = layers
    
    def performAction(self, current_data):
        print("########## Creating edemic Tissue ##########")
        newData = bm.create_binary_image(current_data, search = self.label)   
        if np.sum(newData)>0:            
            structure2 = ndimage.generate_binary_structure(3,3)
            newData = ndimage.binary_dilation(newData, structure=structure2, iterations=self.layers).astype(int)
            current_dimensions = current_data.shape
            for x in range(current_dimensions[0]):
                if (np.any(newData[x,:,:] == 1) or np.any(current_data[x,:,:] == self.label)):
                    for y in range(current_dimensions[1]):
                        if (np.any(newData[x,y,:] == 1) or np.any(current_data[x,y,:] == self.label)):
                            for z in range(current_dimensions[2]):
                                if newData[x,y,z] == 1 and current_data[x,y,z] != self.label:
                                    current_data[x,y,z] = self.edemic_tissue_label
        else:
            warnings.warn("No edemic tissue added as no lesion elements were found in data")