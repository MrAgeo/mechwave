# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 19:50:12 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza

mechwave_mainWindow
-------------------

La ventana principal de MechWave


-------
   Copyright (C) 2019  Sergio Jurado Torres & Juan Esteban Ramirez Mendoza

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
   



   Este programa hace parte de MechWave(https://github.com/MrAgeo/mechwave),
   el simulador de ondas acusticas.
"""

import numpy as np
from numpy import linalg as LA

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel
import os

from ui.dialogs.mw__boundary_dlg import BoundaryConditionsDialog
from ui.dialogs.mw__materials_dlg import MaterialsDialog
from ui.dialogs.mw__selections_dlg import SelectionsDialog

from base.core.solver import ensamblarMatrices, solve, Jacobiano, getConstants
from base.core.helper import errorMessage, analizarMalla


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
#import matplotlib.animation as animation

from mpl_toolkits.mplot3d import Axes3D

from math import *

import meshio

# Definimos los vectores para la solución
u_nm1 = None
u_nm2 = None


cdir = os.path.dirname(os.path.abspath(__file__))
class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi(cdir+'/main_window.ui', self)
        
        self.buscarChildren()
        
        
        self.action_Salir.triggered.connect(self.close)#QtWidgets.qApp.quit)
        self.action_BoundaryCond.triggered.connect(self.showBoundDialog)
        self.action_Materiales.triggered.connect(self.showMaterialsDialog)
        self.action_Importar_malla.triggered.connect(self.openFileNameDialog)
        self.action_Asignar_materiales.triggered.connect(self.showSelectionsDialog)
        self.actionDefinir_Termino_Fuente.triggered.connect(self.setFuente)
        self.actionDefinir_Perfil_inicial.triggered.connect(self.setUzero)
        self.actionDefinir_Velocidad_inicial.triggered.connect(self.setVzero)
        self.actionFrame_number.triggered.connect(self.setFrameNumber)
        self.action_Solucionar.triggered.connect(self.goSolving)
        
#        self.action_Generar_Script.triggered.connect(self.generateScript)
        
        # Numero de frames a mostrar en la animacion
        self.nframes = 100
        
        
        #Opción de dibujar líneas y vértices
        self.lineON = True
        self.vtxON = True
        
        ## Tabla y lista de condiciones de frontera
        self.BCondTable = None
        # Diccionario tipo {borde: (alpha,beta,g)}
        self.BCondList = dict()
        
        
        ## Tabla y lista de materiales
        self.MaterialsTable = None
        # Diccionario tipo {nombre: velocidad}
        self.materialsList = dict()
        
        
        ## Diccionario de secciones y materiales
        # tipo {membershipID: nombreMaterial}
        self.selectionMaterials= dict()
        
        # Velocidad máxima de los materiales
        self.maxVel = None
        
        # Distancia minima entre nodos
        self.minDX = None
        
        # La malla
        self.mesh = None
        self.mesh_filename = None
        
        # Fuente
        self.fuente = None
        self.fuente_text = None
        
        # Perfil Inicial
        self.u_zero = None
        self.uzero_text = None
        
        # Velocidad inicial
        self.v_zero = None
        self.vzero_text = None
        
        #                     w, h
        self._fig = Figure(figsize=(4, 4), dpi=100)
        self._axes = self._fig.add_subplot(111)
        
        self.canvas = FigureCanvas(self._fig)
        self.canvas.setParent(self)
        
        h = self.height()-self.menubar.height()
        self.canvas.setGeometry(0,self.menubar.height(),self.width(), h)

        
    def buscarChildren(self):
        self.menubar = self.findChild(QtWidgets.QMenuBar, 'menubar')
        self.action_BoundaryCond = self.findChild(QtWidgets.QAction,
                                                  'action_BoundaryCond')
        self.action_Materiales = self.findChild(QtWidgets.QAction,
                                                'action_Materiales')
        self.action_Importar_malla = self.findChild(QtWidgets.QAction,
                                                    'action_Importar_malla')
        self.action_Asignar_materiales = self.findChild(QtWidgets.QAction,
                                                        'action_Asignar_materiales')
        self.actionDefinir_Termino_Fuente = self.findChild(QtWidgets.QAction,
                                                           'actionDefinir_Termino_Fuente')
        self.actionDefinir_Perfil_inicial = self.findChild(QtWidgets.QAction,
                                                           'actionDefinir_Perfil_inicial')
        self.actionDefinir_Velocidad_inicial = self.findChild(QtWidgets.QAction,
                                                           'actionDefinir_Velocidad_inicial')
        self.actionFrame_number = self.findChild(QtWidgets.QAction,
                                                           'actionFrame_number')
        self.action_Solucionar = self.findChild(QtWidgets.QAction, 'action_Solucionar')
#        self.action_Generar_Script = self.findChild(QtWidgets.QAction, 'action_Generar_Script')

    
    def redrawCanvas(self, pts=None):
        if pts is None:
            pts = self.trianglePts
        # trianglesPts
        for i in range(self.trianglePts.shape[2]):
            self._axes.plot(pts[0,:,i],pts[1,:,i], 'k')
        # linesPts
        
        if self.lineON:
            for i in range(self.linePts.shape[2]):
                self._axes.plot(self.linePts[0,:,i],self.linePts[1,:,i])
        # verticesPts
        if self.vtxON:
            for i in range(self.verticesPts.shape[1]):
                x = self.verticesPts[0,i]
                y = self.verticesPts[1,i]
                self._axes.plot([x],[y], 'o')
        
        self.canvas.draw()


# TODO: Generar Script
#    def generateScript(self):
#        if not self.mesh:
#            errorMessage(self,"Debe primero importar una malla antes de guardar el script.")
#        elif not self.BCondList:
#            errorMessage(self,"Debe primero crear condiciones de borde antes de guardar el script.")
#        elif not self.materialsList:
#            errorMessage(self,"Debe primero crear materiales antes de guardar el script.")
#        elif not self.selectionMaterials:
#            errorMessage(self,"Debe primero asignar materiales antes de guardar el script.")
#        elif not self.fuente:
#            errorMessage(self, "Debe primero seleccionar una fuente antes de guardar el script.")
#        else:
#            text = "".join(
#                    ["mesh = ",self.mesh_filename,
#                     "\nbcondList = ", str(self.BCondList),
#                     "\nmaterialList = ", str(self.materialsList),
#                     "\nselectionMaterials = ", str(self.selectionMaterials),
#                     "\nfuente = eval(", self.fuente_text,")"])
##            fname = QtGui.QFileDialog.getSaveFileName(self, 'Guardar Sctript')
#        
#            with open("mw_script.py",'w') as f:
#                f.write(text)
    
    
    def showBoundDialog(self):
        dialog = BoundaryConditionsDialog(self, self.BCondTable)
        
        # Si el usuario presiona aceptar, clonar tabla
        if dialog.exec_():
            rows = dialog.tabla.rowCount()
            cols = dialog.tabla.columnCount()
            self.BCondTable = QStandardItemModel(rows,cols)
            
            for row in range(rows):
                borde = dialog.tabla.index(row,1).data()
                alpha = float(dialog.tabla.index(row,2).data())
                beta = float(dialog.tabla.index(row,3).data())
                
                g = None
                try:
                    g = "lambda x,y: "+ dialog.tabla.index(row,4).data()#eval("lambda x,y: "+ dialog.tabla.index(row,4).data())
                    f = eval(g)
                    assert type(f(0,0)) == float or type(f(0,0)) == int
                    
                    self.BCondList[borde] = (alpha,beta,f)
                
                except Exception as error:
                    self.BCondList = dict()
                    errorMessage(self,
                                 "Hubo un error al procesar g(x,y) en la condicion %d.\n" % (row+1)+
                                 "Favor verificar. (tal vez la función no devuelve un número?)",
                                 detailedText=str(error))
                for col in range(cols):
                    item = dialog.tabla.item(row,col).clone()
                    self.BCondTable.setItem(row,col,item)


    def showMaterialsDialog(self):
            dialog = MaterialsDialog(self, self.MaterialsTable)
            
            # Si el usuario presiona aceptar, clonar tabla
            if dialog.exec_():
                rows = dialog.tabla.rowCount()
                cols = dialog.tabla.columnCount()
                self.MaterialsTable = QStandardItemModel(rows,cols)
                
                # Clonar tabla
                for row in range(rows):
                    for col in range(cols):
                        item = dialog.tabla.item(row,col).clone()
                        self.MaterialsTable.setItem(row,col,item)
                
                # Crear diccionarios con materiales y velocidades
                self.materialsList = dict()
                for row in range(rows):
                    shearData = dialog.tabla.index(row,3).data()
                    
                    
                    nombreMaterial = dialog.tabla.index(row, 0).data()
                    tipoMaterial =  dialog.tabla.index(row,1).data()
                    nombre = nombreMaterial+'(%s)'%tipoMaterial
                    
                    bulk = float(dialog.tabla.index(row,2).data())
                    shear = None if tipoMaterial == "Fluido" else float(shearData)
                    density = float(dialog.tabla.index(row,4).data())
                    
                    vel = sqrt((bulk + 4/3*shear)/density) if tipoMaterial == "Sólido" \
                          else sqrt(bulk/density)
                    
                    self.materialsList[nombre] = vel
               
                self.maxVel = max(self.materialsList.items())[1]
    
    
    def showSelectionsDialog(self):
        
        # Si ya se crearon materiales
        if not self.mesh:
            errorMessage(self,"Debe primero importar una malla antes de asignar materiales.")
            
        elif self.materialsList:
            dialog = SelectionsDialog(self, self.selectionsList, [n for n in self.materialsList.keys()])
            
            # Si el usuario presiona aceptar, clonar tabla
            if dialog.exec_():
                rows = dialog.tabla.rowCount()
                
                for row in range(rows):
                        sID = dialog.tabla.index(row,1).data()
                        materialName = dialog.tabla.index(row,2).data()
                        self.selectionMaterials[sID]= materialName
        else:
            errorMessage(self,"Debe primero crear materiales antes de asignar uno.")
    
    
    def setFuente(self):
        text, ok = QtWidgets.QInputDialog().getText(self, "Definir término fuente",
                                     "f(x,y,t)")
        if text and ok:
            self.fuente_text = text
            try:
                f = eval("lambda x,y,t: " + text)
                assert type(f(0,0,0)) == float or type(f(0,0,0)) == int
                self.fuente = f
            except Exception as error:
                errorMessage(self,
                             "Hubo un error al procesar f(x,y,t). Favor verificar."+
                              "\n(tal vez la función no devuelve un número?)",
                              detailedText=str(error))
                
                
    def setUzero(self):
        text, ok = QtWidgets.QInputDialog().getText(self, "Definir perfil inicial",
                                     "I(x,y)")
        if text and ok:
            self.uzero_text = text
            try:
                f = eval("lambda x,y: " + text)
                assert type(f(0,0)) == float or type(f(0,0)) == int
                self.u_zero = f
            except Exception as error:
                errorMessage(self,
                             "Hubo un error al procesar I(x,y). Favor verificar."+
                              "\n(tal vez la función no devuelve un número?)",
                              detailedText=str(error))            
    
    def setFrameNumber(self):
        text, ok = QtWidgets.QInputDialog().getText(self, "Definir el numero de frames",
                                     "nframes=")
        if text and ok:
            self.nframes_text = text
            try:
                f = int(text)
                self.nframes = f
            except Exception as error:
                errorMessage(self,
                             "Hubo un error al procesar nframes. Favor verificar."+
                              "\n(tal vez no se ingresó un número?)",
                              detailedText=str(error))
                
                
    def setVzero(self):
        text, ok = QtWidgets.QInputDialog().getText(self, "Definir velocidad inicial",
                                     "V(x,y)")
        if text and ok:
            self.vzero_text = text
            try:
                f = eval("lambda x,y: " + text) 
                assert type(f(0,0)) == float or type(f(0,0)) == int
                self.v_zero = f
            except Exception as error:
                errorMessage(self,
                             "Hubo un error al procesar f(x,y,t). Favor verificar."+
                              "\n(tal vez la función no devuelve un número?)",
                              detailedText=str(error))
    
    
    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Importar Malla", "","MSH Files (*.msh)", options=options)
        if fileName:
            self.mesh = meshio.read(fileName)
            self.mesh_filename = fileName
        
        t = analizarMalla(self.mesh)
        
        self.minDX = t[0]
        
        self.trianglePts = t[1]
        self.linePts = t[2]
        self.verticesPts = t[3]
        
        self.redrawCanvas()
        
        self.membershipIDs = t[4]
        self.selectionsList = t[5]
        self.boundNodes = t[6]
    
    def goSolving(self):
        
        if not self.mesh:
            errorMessage(self,"Debe primero importar una malla antes de solucionar.")
        elif not self.BCondList:
            errorMessage(self,"Debe primero crear condiciones de borde antes de solucionar.")
        elif not self.materialsList:
            errorMessage(self,"Debe primero crear materiales antes de solucionar.")
        elif not self.selectionMaterials:
            errorMessage(self,"Debe primero asignar materiales antes de solucionar.")
        elif not self.fuente:
            errorMessage(self, "Debe primero seleccionar una fuente antes de solucionar.")
        elif not self.u_zero:
            errorMessage(self, "Debe primero seleccionar un perfil inicial antes de solucionar.")
        elif not self.v_zero:
            errorMessage(self, "Debe primero seleccionar una velocidad inicial antes de solucionar.")
        else:
            # El dt segun el numero de courant
            # C < 0.25
            fig = plt.figure(1)
            ax = fig.add_subplot(111, projection='3d')
            
            C = 0.01
        
            dt = self.minDX*C/self.maxVel
            
            phis, wi,xi = getConstants()

            pts = self.mesh.points
            triangles = self.mesh.cells['triangle']
            
            # Primera iteracion
            # Ya conocemos u0 y u_m1:
            
            K, M, d = ensamblarMatrices(pts,self.boundNodes, triangles,
                                        list(self.membershipIDs), dt,
                                        self.BCondList, self.materialsList,
                                        self.selectionMaterials)
            
            # Definimos los vectores para la solución
            u_nm1 = np.zeros(len(pts))
            u_nm2 = np.zeros(len(pts))
            
            
            
            # Primera iteración
            for i,pt in enumerate(pts):
                u_nm1[i] = self.u_zero(pt[0],pt[1])
                u_nm2[i] = self.v_zero(pt[0],pt[1])
            
            q = np.zeros(len(pts))
                
            for numTriangulo, tri in enumerate(triangles):
                triPts = pts[tri]
                qLoc = np.zeros(3)
                
                # El Jacobiano y su determinante
                J = Jacobiano(pts, tri)
                detJ = LA.det(J)
            
                # Vector de carga
                # Recorrer cada phi en r
                for idx in range(3):
                        sumai=0                        
                        # Recorrer cada punto de la cuadratura en r
                        for wk, rk in zip(wi,xi):
                            sumaj=0
                            # Recorrer cada punto de la cuadratura en s
                            for wj, sj in zip(wi,xi):
                                sumaj += wk*wj*phis[idx](rk,sj)*(1-sj) \
                                *self.fuente(triPts[idx,0],triPts[idx,1],i*dt)\
                                *detJ
                            
                            sumai += sumaj
                    
                        qLoc[idx] = sumai
                
                
                q[tri] += qLoc        
            
            q += d
            
            b = 0.5*(dt**2*q - K @ u_nm1) + 2*dt*u_nm2
            
            u = LA.solve(M,b)
            
            self.u_nm2 = u_nm1
            self.u_nm1 = u
            
            
            for i in range(self.nframes):
                u = solve(M, K, d, self.fuente, i, dt, u_nm1, u_nm2, triangles, pts)
                    
                u_nm2 = u_nm1
                u_nm1 = u
                
                ax.cla()
                trianglesPts = np.zeros((3,4,len(triangles)))
                for i,triangle in enumerate(triangles):
                    trianglesPts[0,:3,i] = pts[triangle,0]
                    trianglesPts[1,:3,i] = pts[triangle,1]
                    trianglesPts[2,:3,i] = u[triangle]
                
                    trianglesPts[0,3,i] = pts[triangle,0][0]
                    trianglesPts[1,3,i] = pts[triangle,1][0]
                    trianglesPts[2,3,i] = u[triangle][0]
                
                
                for i in range(trianglesPts.shape[2]):
                        ax.plot(trianglesPts[0,:,i],trianglesPts[1,:,i],trianglesPts[2,:,i],
                                'k')
                plt.pause(.1)