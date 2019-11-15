# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 19:50:12 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


mechwave_mainWindow
-------------------

La ventana principal de MechWave
"""

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtGui import QStandardItemModel
import os

from ui.dialogs.mw__boundary_dlg import BoundaryConditionsDialog
from ui.dialogs.mw__materials_dlg import MaterialsDialog
from ui.dialogs.mw__selections_dlg import SelectionsDialog

from base.core.solver import solve
from base.core.helper import errorMessage

import numpy.linalg as LA

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from math import sqrt

import meshio


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
        self.action_Solucionar.triggered.connect(self.goSolving)
        
        self.action_Generar_Script.triggered.connect(self.generateScript)
        
        ## Tabla y lista de condiciones de frontera
        self.BCondTable = None
        # Diccionario tipo {borde: (alpha,beta,g)}
        self.BCondList = dict()
        
        
        ## Tabla y lista de materiales
        self.MaterialsTable = None
        # Diccionario tipo {nombre: velocidad}
        self.MaterialsList = dict()
        
        
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
        
        #                     w, h
        fig = Figure(figsize=(4, 4), dpi=100)
        self._axes = fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self)
        
        h = self.height()-self.menubar.height()
        self.canvas.setGeometry(0,self.menubar.height(),self.width(), h)

        
    def buscarChildren(self):
        self.menubar = self.findChild(QtWidgets.QMenuBar, 'menubar')
        self.action_BoundaryCond = self.findChild(QtWidgets.QAction, 'action_BoundaryCond')
        self.action_Materiales = self.findChild(QtWidgets.QAction, 'action_Materiales')
        self.action_Importar_malla = self.findChild(QtWidgets.QAction, 'action_Importar_malla')
        self.action_Asignar_materiales = self.findChild(QtWidgets.QAction, 'action_Asignar_materiales')
        self.actionDefinir_Termino_Fuente = self.findChild(QtWidgets.QAction, 'actionDefinir_Termino_Fuente')
        self.action_Solucionar = self.findChild(QtWidgets.QAction, 'action_Solucionar')
        self.action_Generar_Script = self.findChild(QtWidgets.QAction, 'action_Generar_Script')

    def generateScript(self):
        
        if not self.mesh:
            errorMessage(self,"Debe primero importar una malla antes de guardar el script.")
        elif not self.BCondList:
            errorMessage(self,"Debe primero crear condiciones de borde antes de guardar el script.")
        elif not self.MaterialsList:
            errorMessage(self,"Debe primero crear materiales antes de guardar el script.")
        elif not self.selectionMaterials:
            errorMessage(self,"Debe primero asignar materiales antes de guardar el script.")
        elif not self.fuente:
            errorMessage(self, "Debe primero seleccionar una fuente antes de guardar el script.")
        else:
            text = "".join(
                    ["mesh = ",self.mesh_filename,
                     "\nbcondList = ", str(self.BCondList),
                     "\nmaterialList = ", str(self.MaterialsList),
                     "\nselectionMaterials = ", str(self.selectionMaterials),
                     "\nfuente = ", self.fuente_text])
#            fname = QtGui.QFileDialog.getSaveFileName(self, 'Guardar Sctript')
        
            with open("mw_debug.py",'w') as f:
                f.write(text)
    
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
                    self.BCondList[borde] = (alpha,beta,g)
                except SyntaxError:
                    self.BCondList = dict()
                    errorMessage(self, "Hubo un error al procesar g(x,y) en la condicion %d." % (row+1)+
                                 "Favor verificar.")
                for col in range(cols):
                    item = dialog.tabla.item(row,col).clone()
                    self.BCondTable.setItem(row,col,item)


    def showMaterialsDialog(self):
            dialog = MaterialsDialog(self, self.MaterialsTable)
            
            # Si el usuario presiona aceptar, clonar tabla
            if dialog.exec_():
                maxVel = 0
                rows = dialog.tabla.rowCount()
                cols = dialog.tabla.columnCount()
                self.MaterialsTable = QStandardItemModel(rows,cols)
                
                # Clonar tabla
                for row in range(rows):
                    for col in range(cols):
                        item = dialog.tabla.item(row,col).clone()
                        self.MaterialsTable.setItem(row,col,item)
                
                # Crear diccionarios con materiales y velocidades
                self.MaterialsList = dict()
                for row in range(rows):
                    shearData = dialog.tabla.index(row,3).data()
                    
                    
                    nombreMaterial = dialog.tabla.index(row, 0).data()
                    tipoMaterial =  dialog.tabla.index(row,1).data()
                    nombre = nombreMaterial+'(%s)'%tipoMaterial
                    
                    young = float(dialog.tabla.index(row,2).data())
                    shear = None if tipoMaterial == "Fluido" else float(shearData)
                    density = float(dialog.tabla.index(row,4).data())
                    
                    vel = sqrt((young + 4/3*shear)/density) if tipoMaterial == "Sólido" \
                          else sqrt(young/density)
                    
                    maxVel = max(maxVel,vel)
                    
                    self.MaterialsList[nombre] = vel
                self.maxVel = maxVel
    
    def showSelectionsDialog(self):
        
        # Si ya se crearon materiales
        if not self.mesh:
            errorMessage(self,"Debe primero importar una malla antes de asignar materiales.")
            
        elif self.MaterialsList:
            dialog = SelectionsDialog(self, self.selectionsList, [n for n in self.MaterialsList.keys()])
            
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
        text, ok = QtWidgets.QInputDialog().getText(self, "Dedfinir término fuente",
                                     "f(x,y,t)")
        if text and ok:
            try:
                f = eval("lambda x,y,t: "+ text)
                self.fuente_text = text
                self.fuente = f
            except SyntaxError:
                errorMessage(self, "Hubo un error al procesar f(x,y,t). Favor verificar.")
    
    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Importar Malla", "","MSH Files (*.msh)", options=options)
        if fileName:
            self.mesh = meshio.read(fileName)
            self.mesh_filename = fileName
        
        # Buscar el dx con menor longitud
        minLine = LA.norm(self.mesh.points[self.mesh.cells['line'][0]][0,:] - \
                          self.mesh.points[self.mesh.cells['line'][0]][1,:])
        for triangle in self.mesh.cells['triangle']:
            ptsX = list(self.mesh.points[triangle][:,0])
            ptsY = list(self.mesh.points[triangle][:,1])
            
            ptsX.append(self.mesh.points[triangle][0,0])
            ptsY.append(self.mesh.points[triangle][0,1])
            
            ab = LA.norm(self.mesh.points[triangle][0,:]-self.mesh.points[triangle][1,:])
            bc = LA.norm(self.mesh.points[triangle][1,:]-self.mesh.points[triangle][2,:])
            ca = LA.norm(self.mesh.points[triangle][2,:]-self.mesh.points[triangle][0,:])
                
            minLine = min(minLine, ab, bc, ca)
            
            self._axes.plot(ptsX,ptsY, 'k')
        self.minDX = minLine
        
        for line in self.mesh.cells['line']:
            ptsX = self.mesh.points[line,0]
            ptsY = self.mesh.points[line,1] 
            self._axes.plot(ptsX,ptsY)
        
        for vtx in self.mesh.cells['vertex']:
            ptX = self.mesh.points[vtx,0]
            ptY = self.mesh.points[vtx,1]
            self._axes.plot(ptX,ptY, 'o')
            
        self.triangleMemberships = self.mesh.cell_data['triangle']['gmsh:physical']
        self.membershipIDs = set(self.triangleMemberships)
        
        self.selectionsList = dict()
        for i, membershipID in enumerate(self.membershipIDs):
            self.selectionsList["Seleccion"+str(i)] = membershipID
        self.canvas.draw()
        
        
    def goSolving(self):
        
        if not self.mesh:
            errorMessage(self,"Debe primero importar una malla antes de solucionar.")
        elif not self.BCondList:
            errorMessage(self,"Debe primero crear condiciones de borde antes de solucionar.")
        elif not self.MaterialsList:
            errorMessage(self,"Debe primero crear materiales antes de solucionar.")
        elif not self.selectionMaterials:
            errorMessage(self,"Debe primero asignar materiales antes de solucionar.")
        elif not self.fuente:
            errorMessage(self, "Debe primero seleccionar una fuente antes de solucionar.")
        else:
            # El dt segun el numero de courant
            # C < 0.25
            C = 0.2
        
            dt = self.minDX*C/self.maxVel
            
            u = solve(self.mesh.points,self.mesh.cells['triangle'],list(self.membershipIDs),
                      dt, self.BCondList, self.MaterialsList, self.selectionMaterials, self.fuente)
            print(u)
            
            