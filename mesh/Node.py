# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 14:50:29 2023

@author: grife
"""


class INode():
    def __init__(self, number, coords):        
        self.number = number
        self.coords = list(coords)
        self.data = {}
    
    def addData(self,name,value):
        self.data[name] = value
        
    def getData(self,name):
        return self.data.get(name,[])
    
    def setCoords(self, coords):
        self.coords = list(coords)
    
    def getCoords(self):
        return self.coords

    def get_number(self):
        return self.number

    def set_number(self, number):
        self.number = number
        
class Node(INode):    
    pass