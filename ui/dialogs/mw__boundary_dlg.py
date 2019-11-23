# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 20:04:51 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


mechwave_dlg_BoundaryConditions
-------------------------------

Diálogo para editar las condiciones de frontera


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

from ui.labels.mathtextlabel import MathTextLabel
from ui.widgets.cbid import ComboBoxItemDelegate

from base.core.helper import es_numero, errorMessage

import os

cdir = os.path.dirname(os.path.abspath(__file__))
class BoundaryConditionsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, tabla=None,*args, **kwargs):
        super(BoundaryConditionsDialog,self).__init__(parent,*args, **kwargs)
        
        mathText=r'$\alpha\,u  + \beta\,\frac{\partial u}{\partial\hat{n}} = g(x,y)$'
        self.lbl_eq = MathTextLabel(mathText, self)
        self.lbl_eq.setGeometry(QtCore.QRect(170, 80, 61, 21))
        self.lbl_eq.setObjectName("lbl_eq")
        
        uic.loadUi(cdir+'/dialog_BoundaryConditions.ui', self)
        
        self.buscarChildren()
        self.anadirTabla(tabla)
        
        self.btn_anadirFila.clicked.connect(self.anadirFila)
        
        self.btn_borrarFila.clicked.connect(self.borrarFila)
        self.btn_borrarFila.setEnabled(False)
        
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.rejected.connect(self.reject)
        
        
    def buscarChildren(self):
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.tableView_BCond = self.findChild(QtWidgets.QTableView, 'tableView_BCond')
        self.btn_anadirFila = self.findChild(QtWidgets.QPushButton, 'btn_anadirFila')
        self.btn_borrarFila = self.findChild(QtWidgets.QPushButton, 'btn_borrarFila')
        self.lbl_error = self.findChild(QtWidgets.QLabel, 'lbl_error')
    
    
    
    def anadirTabla(self, tabla):
        """
        Crea la tabla, la muestra y le anade el combobox a las columnas 0 y 1
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
            self.verificarCondiciones()
                    
        # Poner los titulos de cada columna
        self.tabla.setHorizontalHeaderLabels(["Tipo Condición", "Borde", "Alpha", "Beta", "g(x,y)" ])
        
        # Conectar la funcion de verificar los datos cuando cambie alguno
        self.tabla.dataChanged.connect(self.verificarDatosItem)
        
        # Asignar la tabla al visualizador
        self.tableView_BCond.setModel(self.tabla)
        
        
        ### Anadir los combobox
        
        # Primera columna (Columna 0)
        cbid = ComboBoxItemDelegate(self.tableView_BCond)
        cbid.setComboBoxItems(["Dirichlet", "Neumann","Robin"])
        
        self.tableView_BCond.setItemDelegateForColumn(0,cbid)
        
        # Segunda columna (Columna 1)
        cbid2 = ComboBoxItemDelegate(self.tableView_BCond)
        cbid2.setComboBoxItems(["Superior", "Inferior","Izquierdo","Derecho"])
        self.tableView_BCond.setItemDelegateForColumn(1,cbid2)
        
        # Anadir los titulos a la tabla
        header = self.tableView_BCond.horizontalHeader()
        header.setDefaultAlignment(QtCore.Qt.AlignHCenter)
#        self.tableView_BCond.resizeColumnsToContents()
        
        # Anadir el listener para cambiar el caption del boton Borrar Condicion
        self.tableView_BCond.selectionModel().selectionChanged.connect(self.cambiarCaption_btnBorrar)

    def anadirFila(self):
        """
        Anade una nueva condicion a la tabla
        """
        alpha = QStandardItem("1")
        beta = QStandardItem("0")
        
        alpha.setEnabled(False)
        beta.setEnabled(False)
        
        self.tabla.appendRow([QStandardItem("Dirichlet"),
                              QStandardItem("Inferior"),
                              alpha,
                              beta,
                              QStandardItem("0")])
    
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
                self.btn_borrarFila.setText("Borrar Condiciones")
            else:
                self.btn_borrarFila.setText("Borrar Condición")
                
            self.selectedRows = sorted(rows,reverse=True)
        else:
            self.btn_borrarFila.setEnabled(False)
            self.btn_borrarFila.setText("Borrar Condición")
    
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
            
            # Si se modifico el tipo de condicion de frontera cambiar
            # alpha y beta
            if col == 0:
                alphaIndex = model.index(row, 2)
                betaIndex = model.index(row, 3)

                alpha = model.itemFromIndex(alphaIndex)
                beta = model.itemFromIndex(betaIndex)
                
                if data == "Dirichlet":
                    
                    model.setData(alphaIndex,"1", QtCore.Qt.EditRole)
                    model.setData(betaIndex, "0", QtCore.Qt.EditRole)
                    
                    alpha.setEnabled(False)
                    beta.setEnabled(False)
                    
                elif data == "Neumann":
                    
                    model.setData(alphaIndex,"0", QtCore.Qt.EditRole)
                    model.setData(betaIndex, "1", QtCore.Qt.EditRole)
                    
                    alpha.setEnabled(False)
                    beta.setEnabled(False)
                    
                elif data == "Robin":
                    model.setData(alphaIndex,"1", QtCore.Qt.EditRole)
                    model.setData(betaIndex, "1", QtCore.Qt.EditRole)
                    
                    alpha.setEnabled(True)
                    beta.setEnabled(True)
            
            # Si se modifico alpha verificar que es un valor numerico
            # (solo para la condicion de Robin)
            elif col == 2 and str(model.index(row,0).data())== "Robin":
                if not es_numero(data):
                    msg = (("El valor ingresado '%s' no es válido.\n\n" % data)+
                           "Si quiere ingresar un decimal, ingrese "+
                           "un punto en vez de una coma\n(por ejemplo "+
                           "'3.15e5' en vez de '3,15e5').")
                          
                    errorMessage(self, msg, "Valor no válido")
                    
                    model.setData(topLeft,'1', QtCore.Qt.EditRole)
                else:
                    if float(str(topLeft.data()))== 0:
                        msg = ("Alpha y beta no pueden ser cero en este tipo de condición. "+
                               "Si quiere aplicar una condición donde "+
                               "alpha o beta sean cero por favor seleccione "+
                               "'Dirichlet' o 'Neumann' en la columna 'Tipo Condición'.")
                        
                        errorMessage(self, msg)
                        
                        model.setData(topLeft, '1', QtCore.Qt.EditRole)
            
            # Si se modifico beta verificar que es un valor numerico
            # (solo para la condicion de Robin)
            elif col == 3 and str(model.index(row,0).data())== "Robin":
                if not es_numero(data):
                    msg = (("El valor ingresado '%s' no es válido.\n\n" % data)+
                           "Si quiere ingresar un decimal, ingrese "+
                           "un punto en vez de una coma\n(por ejemplo "+
                           "'3.15' en vez de '3,15').")
                          
                    errorMessage(self, msg, "Valor no válido")
                    
                    model.setData(topLeft,'1', QtCore.Qt.EditRole)
                else:
                    if float(str(topLeft.data()))== 0:
                        msg = ("Alpha y beta no pueden ser cero en este tipo de condición. "+
                               "Si quiere aplicar una condición donde "+
                               "alpha o beta sean cero por favor seleccione "+
                               "'Dirichlet' o 'Neumann' en la columna 'Tipo Condición'.")
                        
                        errorMessage(self, msg)
                        
                        model.setData(topLeft, '1', QtCore.Qt.EditRole)
                        
        self.verificarCondiciones()
        
        
    def verificarCondiciones(self):
        
        rows = self.tabla.rowCount()
        # Verificar que sean 4 condiciones de frontera
        
        txt = ""
        if rows != 4:
            if 4-rows>0:
                txt += "Falta" +("n {:d} condiciones" if abs(4-rows)>1 else " {:d} condición").format(abs(4-rows))
            else:
                txt += "Sobra" +("n {:d} condiciones" if abs(4-rows)>1 else " {:d} condición").format(abs(4-rows))
            
        
        # Verificar que haya una condición para cada borde
        else:
            bordes = set()
            for row in range(rows):
                valor = self.tabla.index(row, 1).data()
                if valor in bordes:
                    txt += "Hay más de una condición para el\nborde %s" % valor.lower()
                    break
                else:
                    bordes.add(valor)
            
        if txt == "":
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.lbl_error.setText("")
        else:
            self.lbl_error.setText("Error: "+ txt)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)