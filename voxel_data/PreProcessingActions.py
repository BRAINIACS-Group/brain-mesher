# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 08:49:33 2023

@author: grife
"""
from abc import ABC, abstractmethod

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
        raise NotImplementedError