# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:41:58 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza

helper
------

Contiene algunas funciones utiles que se usan en el codigo.
"""

from PyQt5 import QtWidgets

import numpy as np
import numpy.linalg as LA

def es_numero(s):
    """
    Recibe un string y devuelve True si es un numero o False en caso contrario.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False
    
    
def analizarMalla(mesh):
    # Buscar el dx con menor longitud
    minLine = LA.norm(mesh.points[mesh.cells['line'][0]][0,:] - \
                      mesh.points[mesh.cells['line'][0]][1,:])
    
    trianglesPts = np.zeros((2,4,len(mesh.cells['triangle'])))
    for i,triangle in enumerate(mesh.cells['triangle']):
        trianglesPts[0,:3,i] = mesh.points[triangle,0]
        trianglesPts[1,:3,i] = mesh.points[triangle,1]
        
        trianglesPts[0,3,i] = mesh.points[triangle,0][0]
        trianglesPts[1,3,i] = mesh.points[triangle,1][0]
        
        ab = LA.norm(mesh.points[triangle][0,:] - \
                     mesh.points[triangle][1,:])
        bc = LA.norm(mesh.points[triangle][1,:] - \
                     mesh.points[triangle][2,:])
        ca = LA.norm(mesh.points[triangle][2,:] - \
                     mesh.points[triangle][0,:])
            
        minLine = min(minLine, ab, bc, ca)
    
    linesPts = np.zeros(((2,2,len(mesh.cells['line']))))
    for i, line in enumerate(mesh.cells['line']):
        linesPts[0,:,i] = mesh.points[line, 0]
        linesPts[1,:,i] = mesh.points[line, 1]
    
    
    vertices = mesh.cells['vertex']
    verticesPts = np.zeros(((2,len(vertices))))
    
    verticesPts[0,:] = mesh.points[vertices, 0].T
    verticesPts[1,:] = mesh.points[vertices, 1].T
    
    
    triangleMemberships = mesh.cell_data['triangle']['gmsh:physical']
    membershipIDs = set(triangleMemberships)
    
    selectionsList = dict()
    for i, membershipID in enumerate(membershipIDs):
        selectionsList["Seleccion"+str(i)] = membershipID
    
    
    # Valores de las X y Y para los bordes    
    sup = max(mesh.points[:,1])
    inf = min(mesh.points[:,1])
    der = max(mesh.points[:,0])
    izq = min(mesh.points[:,0])
    
    boundNodes = dict()
    
    nums = np.arange(len(mesh.points))
    
    cond = mesh.points[:,1] == sup 
    boundNodes['Superior'] = nums[cond]
    
    cond = mesh.points[:,1] == inf
    boundNodes['Inferior'] = nums[cond]
    
    cond = mesh.points[:,0] == der 
    boundNodes['Derecho'] = nums[cond]
    
    cond = mesh.points[:,0] == izq 
    boundNodes['Izquierdo'] = nums[cond]
    return (minLine, trianglesPts,
            linesPts, verticesPts,
            list(triangleMemberships), selectionsList,
            boundNodes)
    
def errorMessage(parent=None, msg="Hubo un error", windowTitle="Error", detailedText=None):
    msgBox = QtWidgets.QMessageBox(parent)
    msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    msgBox.setWindowTitle(windowTitle)
    msgBox.setText(msg)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msgBox.setFixedSize(500,200)
    msgBox.setDetailedText(detailedText)
    msgBox.exec_()
    return msg