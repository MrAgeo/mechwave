# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 20:04:51 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza





mechwave_dlg_Materials
----------------------

Diálogo para editar los materiales


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

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from ui.widgets.cbid import ComboBoxItemDelegate

from base.core.helper import es_numero, errorMessage

import os

cdir = os.path.dirname(os.path.abspath(__file__))
class MaterialsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, tabla=None,*args, **kwargs):
        super(MaterialsDialog,self).__init__(parent,*args, **kwargs)
        uic.loadUi(cdir+'/dialog_Materials.ui', self)
        
        self.buscarChildren()
        self.anadirTabla(tabla)
            
        self.btn_anadirFila.clicked.connect(self.anadirFila)
        
        self.btn_borrarFila.clicked.connect(self.borrarFila)
        self.btn_borrarFila.setEnabled(False)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.verificarCondiciones()
        
        
    def buscarChildren(self):
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.tableView_BCond = self.findChild(QtWidgets.QTableView, 'tableView_BCond')
        self.btn_anadirFila = self.findChild(QtWidgets.QPushButton, 'btn_anadirFila')
        self.btn_borrarFila = self.findChild(QtWidgets.QPushButton, 'btn_borrarFila')
        self.lbl_error = self.findChild(QtWidgets.QLabel, 'lbl_error')
    
    
    
    def anadirTabla(self, tabla):
        """
        Crea la tabla, la muestra y le anade el combobox a las columna 1
        """
        
        if tabla is None:
            # Crear la tabla
            self.tabla = QStandardItemModel();
        else:
            rows = tabla.rowCount()
            cols = tabla.columnCount()
            self.tabla = QStandardItemModel(rows,cols)
            
            for row in range(rows):
                for col in range(cols):
                    item = tabla.item(row,col).clone()
                    self.tabla.setItem(row,col,item)
        
        # Poner los titulos de cada columna
        self.tabla.setHorizontalHeaderLabels(["Nombre Material",
                                              "Tipo Material",
                                              "Módulo Compresibilidad (GPa)",
                                              "Módulo Cizalladura (GPa)",
                                              "Densidad (Kg/m^3)" ])
        
        # Conectar la funcion de verificar los datos cuando cambie alguno
        self.tabla.dataChanged.connect(self.verificarDatosItem)
        
        # Asignar la tabla al visualizador
        self.tableView_BCond.setModel(self.tabla)
        
        
        ### Anadir los combobox
        
        # Primera columna (Columna 0)
        cbid = ComboBoxItemDelegate(self.tableView_BCond)
        cbid.setComboBoxItems(["Fluido", "Sólido"])
        
        self.tableView_BCond.setItemDelegateForColumn(1,cbid)
        
        
        # Anadir los titulos a la tabla
        header = self.tableView_BCond.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignHCenter)
        self.tableView_BCond.resizeColumnsToContents()
        
        # Anadir el listener para cambiar el caption del boton Borrar Material
        self.tableView_BCond.selectionModel().selectionChanged.connect(self.cambiarCaption_btnBorrar)
    
    
    def anadirFila(self):
        """
        Anade una nueva condicion a la tabla
        """
        
        self.tabla.appendRow([QStandardItem("Material%d" % (self.tabla.rowCount()+1)),
                              QStandardItem("Sólido"),
                              QStandardItem("1e5"),
                              QStandardItem("1e4"),
                              QStandardItem("1000")])
    
        self.verificarCondiciones()
    
    def cambiarCaption_btnBorrar(self, selected, deselected):
        
        select = self.tableView_BCond.selectionModel()
        
        if select.hasSelection():
            self.btn_borrarFila.setEnabled(True)
            itemRange = select.selection()
            
            rows = set()
            
            for index in itemRange.indexes():
                rows.add(index.row())
            if len(rows)>1:
                self.btn_borrarFila.setText("Borrar Materiales")
            else:
                self.btn_borrarFila.setText("Borrar Material")
                
            self.selectedRows = sorted(rows,reverse=True)
        else:
            self.btn_borrarFila.setEnabled(False)
            self.btn_borrarFila.setText("Borrar Material")
    
    def borrarFila(self):
        """
        Borra la fila del item seleccionado
        """
    
        for row in self.selectedRows:
            self.tabla.removeRow(row)

        self.verificarCondiciones()
    
    def verificarDatosItem(self, topLeft, bottomRight, roles):
        """
        Verifica los datos de Alpha y Beta, y cambia los valores de estos
        cuando se selecciona una condicion de frontera diferente.
        """
        
        # Editar datos si el item es valido
        if topLeft.isValid():
            
            # Obtener la fila, columna y el dato del item (celda)
            row = topLeft.row()
            col = topLeft.column()
            data = str(topLeft.data())
            
            # Obtener la tabla del item
            model = topLeft.model()
            
            if col == 1:
                youngIndex = model.index(row, 2)
                shearIndex = model.index(row, 3)
                densityIndex = model.index(row, 4)

                shear = model.itemFromIndex(shearIndex)
                
                if data == "Sólido":
                    
                    model.setData(youngIndex,"1e5", QtCore.Qt.EditRole)
                    model.setData(shearIndex, "1e4", QtCore.Qt.EditRole)
                    model.setData(densityIndex, "1000", QtCore.Qt.EditRole)
                    
                    shear.setEnabled(True)
                    
                elif data == "Fluido":
                    
                    model.setData(youngIndex,"1e5", QtCore.Qt.EditRole)
                    model.setData(shearIndex, "N/A", QtCore.Qt.EditRole)
                    model.setData(densityIndex, "1000", QtCore.Qt.EditRole)
                    
                    shear.setEnabled(False)
                    
            # Si se modifico una celda verificar que es un valor numerico
            # (solo para la condicion de Robin)
            if col > 1:
                if not es_numero(data):
                    if col != 3 or str(model.index(row,1).data()) != "Fluido":
                        msg = (("El valor ingresado '%s' no es válido.\n\n" % data)+
                           "Si quiere ingresar un decimal, ingrese "+
                           "un punto en vez de una coma\n(por ejemplo "+
                           "'3.15e7' en vez de '3,15e7').")
                          
                        errorMessage(self, msg, "Valor no válido")
                        
                        model.setData(topLeft,'1', QtCore.Qt.EditRole)
                else:
                    if float(str(topLeft.data())) == 0:
                        msg = (" Los valores no pueden ser cero. "+
                               "Por favor ingrese un valor positivo")
                        
                        errorMessage(self, msg)
                    elif float(str(topLeft.data())) <0:
                        msg = (" Los valores no pueden ser negativos. "+
                               "Por favor ingrese un valor positivo")
                    
                        errorMessage(self, msg)
                    
                        model.setData(topLeft, '1', QtCore.Qt.EditRole)
        
        self.verificarCondiciones()
        
        
    def verificarCondiciones(self):
        
        rows = self.tabla.rowCount()
        # Verificar que sean 4 condiciones de frontera
        
        txt = ""
        if rows == 0:
            txt += "Falta 1 material"
        
        # Verificar que haya una condición para cada borde
        else:
            nombres = set()
            for row in range(rows):
                valor = self.tabla.index(row, 0).data()
                tipo =  self.tabla.index(row,1).data()
                nombre = valor+'(%s)'%tipo
                if nombre in nombres:
                    txt += "Hay dos %ss con nombre '%s'" % (tipo.lower(),valor)
                    break
                else:
                    nombres.add(nombre)
        if txt == "":
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.lbl_error.setText("")
        else:
            self.lbl_error.setText("Error: "+ txt)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)