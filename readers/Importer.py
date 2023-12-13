# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 08:58:07 2023

@author: grife
"""

from abc import ABC, abstractmethod
from os.path import exists
import nibabel
import numpy as np

class IImport(ABC):
    
    @abstractmethod
    def getData(self):
        raise NotImplementedError
        
class ImportFromFile(IImport):
        
    def __init__(self, path, filename):        
        self.fullPath = "/".join([path, filename])
        assert exists(self.fullPath), "Path {} does not exist.".format(self.fullPath)
    
    def getData(self):
        try:
            # Step 1: Using freesurfer and 'recon-all' create in outputs. Ensure aseg.mgz is created.
            t1_file = self.fullPath
            t1 = nibabel.load(t1_file)
            # t1.orthoview()
            data = np.asarray(t1.dataobj)
            return data
        except:
            print("Error importing file from {}".format(self.fullPath))
            return []
        
        