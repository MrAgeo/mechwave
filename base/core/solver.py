# -*- coding: iso-8859-15 -*-
"""
Created on Fri Nov  8 12:41:25 2019

@author: Sergio Jurado Torres & Juan Esteban Ramirez Mendoza

Solver
------

Soluciona la malla para las condiciones dadas



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
import numpy.linalg as LA

from math import *

phi0 = lambda r,s: 1-r-s
phi1 = lambda r,s: r
phi2 = lambda r,s: s


phis = [phi0, phi1, phi2]

## Pesos y puntos de la cuadratura de Gauss
xi = np.array([-0.774597, 0, 0.774597])
wi = np.array([0.555556, 0.888889, 0.555556])


# Matriz de derivadas de phi
D = np.array([[-1, 1, 0],
              [-1, 0, 1]])

def getConstants():
    return phis, wi,xi


def Jacobiano(pts, triangle):
    """
    Devuelve el jacobiano del triángulo
    """
    a = pts[triangle][0];
    b = pts[triangle][1];
    c = pts[triangle][2];
    
    return np.array([[b[0]-a[0], c[0]-a[0]],
                     [b[1]-a[1], c[1]-a[1]]])


def ensamblarMatrices(pts, boundNodes, triangles, memberships, dt, bcondList,
          materialsList, selectionMaterials):
    """
    Ensambla las matrices del problema.
    
    Parámetros:
        pts (numpy.narray):
            Lista con los puntos con coordenadas X,Y,Z.
            
        boundNodes (dict):
            Diccionario con los nodos que pertenecen a cada
            borde. Esquema {borde: listaNodos(list)}
        
        triangles(numpy.array):
            Lista con las conectividades de cada triángulo.
        
        memberships (list):
            Lista con el número de sección al que pertenece
            el elemento. Por ejemplo, [1,3,3,1] indica que el primer y último
            elemento pertenecen a la sección con ID 1 y el segundo y tercero a
            la sección con ID 3.
        
        dt (float):
            El espacio entre cada tiempo t a evaluar.
        
        bcondList (dict):
            Diccionario con las condiciones de frontera: Esquema
            {borde: (alpha, beta, g)}. Alpha y beta son tipo float y g
            una función que recibe dos parámetros y devuelve un valor float.
            
        materialsList (dict):
            Diccionario con el nombre del material y la
            velocidad de propagacion dentro de éste.
            Esquema {nombre: velocidad(float)}
        
        selectionMaterials (dict): 
            Diccionario con el ID de cada seccción y el nombre del material
            asignado a ésta. Esquema {id: nombreMaterial(str)}
            
    Devuelve:
        
        La matrices K, M y el vector de carga d generado por las condiciones
        de Neumann (todos son numpy.array).
    """
    
    aGlob = np.zeros((len(pts), len(pts)))
    
    mGlob = np.zeros((len(pts), len(pts)))
    
    
    ### Integral en los bordes
    # Crear el diccionario con los nodos de cada borde
    # (para pasárselo a integrarBordes())
    bordes = dict()
    for k,v in boundNodes.items():
        bordes[k] = pts[v]
        
        
    # Integrar cada borde y obtener las matriz y vector global C y M
    # dGlob -> Neumann
    # cGlob -> Dirichlet
    cGlob, dGlob = integrarBordes(boundNodes, bordes, bcondList, len(pts))
    
    ### Integrar cada elemento
    # Obtener matrices y vectores locales
    # (recorrer cada triángulo)
    for numTriangulo, tri in enumerate(triangles):
        
        # El Jacobiano y su inverso y determinante
        J = Jacobiano(pts, tri)
        invJ = LA.inv(J)
        detJ = LA.det(J)
        
        # Obtener velocidad del elemento
        
        ms = str(memberships[numTriangulo])
        smt = selectionMaterials[ms]
        vel = materialsList[smt]
        
        # Matriz A local

        #   integral 0->1 (integral 0->1-s (1) dr) ds
        # = integral 0->1 (1-s) ds
        # = [s-0.5*s^2],s->1 - [s-0.5*s^2],s->0
        # = 1/2
        
        aLoc = D.T @ invJ.T @ invJ @ D
        aLoc *= -0.5*vel**2*detJ
        
        # Matriz M local
        # integral 0->1 (integral 0->1-s (phi_i*phi_j) dr) ds
        
        mLoc = np.array([[2,1,1],[1,2,1],[1,1,2]], dtype='float64')
        mLoc /= 24
        
        ## Ensamblar A y M global
        # Pasar por cada fila de A Local y M Local
        # (i.e. 3 filas = 3 nodos en el elemento)
        for numFila in range(3):
            aGlob[tri[numFila],tri] += aLoc[numFila, :]
            mGlob[tri[numFila],tri] += mLoc[numFila, :]

        
    kGlob = aGlob + cGlob
        
    # Nueva matriz K
    kGlob2 = dt*kGlob - 2*mGlob
    
    return kGlob2, mGlob, dGlob
    
    
def solve(M, K, d, f, i, dt, u_m1, u_m2, triangles, pts):
    """
    Resuelve el sistema de ecuaciones del problema.
    
    Parámetros:
        
        M (numpy.array):
            La matriz de masa global.
        
        K (numpy.array):
            La matriz de rigidez global.
        
        d (numpy.array):
            El vector de carga d generado por las condiciones de Neumann.
            
        f (function):
            Función que recibe tres valores float y devuelve otro float. Es
            la función de carga de la ecuación diferencial.
            
        i (int):
            El número de iteración actual (advertencia: comienza en 0).
            
        dt (float):
            El espacio entre cada tiempo t a evaluar.    
            
        u_m1 (numpy.array):
            El vector de la solución en el tiempo anterior.
            
        u_m2 (numpy.array):
            El vector de la solución dos tiempos atrás.
            
        triangles(numpy.array):
            Lista con las conectividades de cada triángulo.
        
        pts (numpy.narray):
            Lista con los puntos con coordenadas X,Y,Z.
    """
    
    
    
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
                        sumaj += wk*wj*phis[idx](rk,sj)*(1-sj)*f(triPts[idx,0],triPts[idx,1],i*dt)*detJ
                    
                    sumai += sumaj
            
                qLoc[idx] = sumai
        
        
        q[tri] += qLoc        

    q += d
    
    b = dt**2*q - K @ u_m1 - M @ u_m2
    
    u = LA.solve(M, b)
    
    return u


def integrarBordes(boundNodes, ptsBordes, bcondList, nodosTotales):
    """
    Función que integra cada borde del dominio.
    
    Parámetros:
        boundNodes (dict):
            Diccionario con los nodos que pertenecen a cada
            borde. Esquema {borde: listaNodos(list)}
            
        pts (dict):
            Diccionario con los puntos de cada borde con coordenadas X,Y,Z.
            Esquema {borde: puntos(numpy.array)}}
            
        bcondList (dict):
            Diccionario con las condiciones de frontera: Esquema
            {borde: (alpha, beta, g)}. Alpha y beta son tipo float y g
            una función que recibe dos parámetros y devuelve un valor float.
    
        nodosTotales (int):
            Cantidad de nodos que hay en la malla
            
    Devuelve:
        La matriz y vector C y M Global generados por las condiciones de 
        Dirichlet y Neumann, respectivamente.
    """
    
    # Matriz C y vector M globales
    cGlob = np.zeros((nodosTotales, nodosTotales))
    dGlob = np.zeros(nodosTotales)

    phiG0 = lambda x: (1-x)/2
    phiG1 = lambda x: (1+x)/2
    
    phisG = [phiG0, phiG1]
    
    # Transformar de -1 a 1 en x0 a x1
    xEval = lambda r, h, x0 :(h/2)*(r+1) + x0
    
    
    bordes = ['Superior', 'Inferior', 'Derecho', 'Izquierdo']
    for borde in bordes:
        pts = ptsBordes[borde]
        
        # D_T = [-1/2, 1/2]
        # X =  [x0; x1]
        #
        # J = D_T @ X = (X1 - X0)/2
        
        # Lista con el jacobiano de cada elemento
        detJ = np.zeros(len(ptsBordes[borde])-1)
        
        for i in range(len(pts)-1):
            detJ[i] = LA.norm(pts[i+1]-pts[i])/2
            
        
        # Crear matrices locales
        cLoc = np.zeros((2,2))
        dLoc = np.zeros(2)
        
        # Obtener alpha, beta y g(x,y)
        alpha = bcondList[borde][0]
        beta = bcondList[borde][1]
        g = bcondList[borde][2]
        
        # Integrar en cada elemento
        for nElm in range(len(pts)-1):
            
            if alpha == 0: # Neumann
            
                for i in range(2):
                    sumai=0
                    # Recorrer cada punto de la cuadratura en i
                    for wk, rk in zip(wi,xi):
                        ## Cálculo de m_i
                        # Calcular g dependiendo de x(r)
                        aux = 0
                        if borde in ['Superior', 'Inferior']:
                            x = xEval(rk,2*detJ[nElm],pts[nElm,0])
                            aux = g(x,pts[nElm,1])
                        else:
                            y = xEval(rk,2*detJ[nElm],pts[nElm,1])
                            aux = g(pts[nElm,0],y)
                       
                        sumai += wk*aux*phisG[i](rk)
                   
                    dLoc[i] = sumai/beta
            elif beta == 0: # Dirichlet
                # Recorrer cada phi en i
                for i in range(2):
                    
                    ## Cálculo de c_ij
                    sumai=0
                    # Recorrer cada phi en j
                    for j in range(2):             
                        # Recorrer cada punto de la cuadratura en i
                        for wk, rk in zip(wi,xi):
                            # Calcular g dependiendo de x(r)
                            aux = 0
                            if borde in ['Superior', 'Inferior']:
                                x = xEval(rk,2*detJ[nElm],pts[nElm,0])
                                aux = g(x,pts[nElm,1])
                            else:
                                y = xEval(rk,2*detJ[nElm],pts[nElm,1])
                                aux = g(pts[nElm,0],y)
                            
                            sumai += wk*aux*phisG[i](rk)*phisG[j](rk)
                    
                        cLoc[i,j] = sumai/alpha
                
            else: # Robin
                # Recorrer cada phi en i
                for i in range(2):
                    # Suma para el elemento  m_i
                    suma_m_i=0
                    # Recorrer cada phi en j
                    for j in range(2):
                        
                        sumai2=0                        
                        # Recorrer cada punto de la cuadratura en i
                        for wk, rk in zip(wi,xi):
                            sumaj=0
                            
                            # Calcular g dependiendo de x(r)
                            aux = 0
                            if borde in ['Superior', 'Inferior']:
                                x = xEval(rk,2*detJ[nElm],pts[nElm,0])
                                aux = g(x,pts[nElm,1])
                            else:
                                y = xEval(rk,2*detJ[nElm],pts[nElm,1])
                                aux = g(pts[nElm,0],y)
                                
                            suma_m_i += wk*phisG[i](rk)/aux
                            
                            # Recorrer cada punto de la cuadratura en j
                            for wj, sj in zip(wi,xi):
                                sumaj += wk*wj*phisG[i](rk)*phisG[j](sj)
                            
                            sumai2 += sumaj
                    
                        cLoc[i,j] = sumai2 * beta/alpha
                    dLoc[i] = suma_m_i*detJ[nElm]*beta**2/alpha
            
            # Ensamblar la matriz Global
            for fila in range(2):
                nodos = boundNodes[borde][nElm:nElm+2]
                cGlob[nodos[fila], nodos] += cLoc[fila,:]
                dGlob[nodos[fila]] += dLoc[fila]
    
    return cGlob,dGlob