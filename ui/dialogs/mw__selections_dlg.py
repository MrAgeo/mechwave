# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 20:04:51 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


mechwave_dlg_Selections
----------------------

Diálogo para asignar los materiales a las selecciones
"""

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from ui.widgets.cbid import ComboBoxItemDelegate

from base.core.helper import es_numero, errorMessage

import os

cdir = os.path.dirname(os.path.abspath(__file__))
class SelectionsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent, selections, materialNames, *args, **kwargs):
        super(SelectionsDialog,self).__init__(parent,*args, **kwargs)
        uic.loadUi(cdir+'/dialog_setMaterials.ui', self)
        
        self.buscarChildren()
        self.anadirTabla(materialNames)
        self.anadirFilas(selections, materialNames)
        
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        
    def buscarChildren(self):
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.tableView_BCond = self.findChild(QtWidgets.QTableView, 'tableView_BCond')
        self.lbl_error = self.findChild(QtWidgets.QLabel, 'lbl_error')
    
    
    
    def anadirTabla(self, materialNames):
        """
        Crea la tabla, la muestra y le anade el combobox a las columna 2
        """
        
        self.tabla = QStandardItemModel();
        
        # Poner los titulos de cada columna
        self.tabla.setHorizontalHeaderLabels(["Nombre Selección",
                                              "ID Selección",
                                              "Nombre Material"])
        
        
        # Asignar la tabla al visualizador
        self.tableView_BCond.setModel(self.tabla)
        
        
        ### Anadir el combobox en la columna 2
        cbid = ComboBoxItemDelegate(self.tableView_BCond)
        cbid.setComboBoxItems(materialNames)
        
        self.tableView_BCond.setItemDelegateForColumn(2,cbid)
        
        
        # Anadir los titulos a la tabla
        header = self.tableView_BCond.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignHCenter)
        self.tableView_BCond.resizeColumnsToContents()
    
    
    def anadirFilas(self, selections, materialNames):
        """
        Anade las condiciones a la tabla
        """
        
        for name, selectionID in selections.items():
            sName = QStandardItem(name)
            sName.setEditable(False)
            
            sID = QStandardItem(str(selectionID))
            sID.setEditable(False)
            self.tabla.appendRow([sName,
                                  sID,
                                  QStandardItem(materialNames[0])])