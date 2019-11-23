# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 14:59:00 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


ComboBox Item Delegate
-----------------

Permite tener un ComboBox en un QTableView.

Basado en el código para C++ de https://wiki.qt.io/Combo_Boxes_in_Item_Views



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
from PyQt5 import QtCore, QtWidgets

class ComboBoxItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super(ComboBoxItemDelegate, self).__init__(*args, **kwargs)
        self.cbItems = {"Item 1", "Item 2","Item 3"}
    
    
    def setComboBoxItems(self,items):
        if items != {}:
            self.cbItems = items 
    
    
    def createEditor(self, parent, option, index):
        cb = QtWidgets.QComboBox(parent)
        
        for item in self.cbItems:
            cb.addItem(item)
        
        return cb
    
    def setEditorData(self, cb, index):
        currentTxt = str(index.data(role=QtCore.Qt.EditRole))
        cbIndex = cb.findText(currentTxt)
        
        if cbIndex >=0:
            cb.setCurrentIndex(cbIndex)
    
    
    def setModelData(self, cb, model, index):
        model.setData(index, cb.currentText(), QtCore.Qt.EditRole)