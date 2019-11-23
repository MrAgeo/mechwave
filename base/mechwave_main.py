# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 19:18:52 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


mechwave_main
-------------

    Abre la ventana principal de mechwave


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

from PyQt5 import QtWidgets

# Anadir el directorio principal a PYTHONPATH
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__+"/..")))

from ui.mw__main_window import MainWindow
from ui.dialogs.mw__boundary_dlg import BoundaryConditionsDialog
from ui.dialogs.mw__materials_dlg import MaterialsDialog

def run_from_ipython():
    """
    Devuelve True si estamos en una consola de IPython
    """
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

if __name__ == "__main__":
    if run_from_ipython():
        mainWindow = MainWindow()
        mainWindow.show()
#        dialog = MaterialsDialog()
#        dialog = BoundaryConditionsDialog()
#        dialog.show()
        
    else:
        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
#        dialog = MaterialsDialog()
#        dialog = BoundaryConditionsDialog()
#        dialog.show()
        app.exec_()