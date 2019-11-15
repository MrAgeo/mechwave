# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 19:18:52 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza


mechwave_main
-------------

    Abre la ventana principal de mechwave
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