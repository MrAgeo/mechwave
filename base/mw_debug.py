# -*- coding: iso-8859-15 -*-

import meshio

import numpy as np
import numpy.linalg as LA

from core.solver import ensamblarMatrices, solve, Jacobiano, getConstants
from core.helper import analizarMalla

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.close()
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111, projection='3d')

mesh = meshio.read("examples/Rectangulo_2.msh")

bcondList = {'Superior': (1.0, 0.0, 'lambda x,y: 0'),
             'Izquierdo': (1.0, 0.0, 'lambda x,y: 0'),
             'Inferior': (1.0, 0.0, 'lambda x,y: 0'),
             'Derecho': (1.0, 0.0, 'lambda x,y: 0')}
materialsList = {'Material1(Sólido)': 10.64581294844754, 'Material2(Sólido)': 31.83289703016886}

selectionMaterials = {'11': 'Material1(Sólido)', '12': 'Material2(Sólido)'}
fuente = eval('lambda x,y,t: 44')

t = analizarMalla(mesh)
minDX = t[0]
        
# trianglesPts
for i in range(t[1].shape[2]):
    ax.plot(t[1][0,:,i],t[1][1,:,i], 'k')
# linesPts
for i in range(t[2].shape[2]):
    ax.plot(t[2][0,:,i],t[2][1,:,i])
# verticesPts
for i in range(t[3].shape[1]):
    x = t[3][0,i]
    y = t[3][1,i]
    ax.plot([x],[y], 'o')
    
plt.show()
        
membershipIDs = t[4]
selectionsList = t[5]

# El dt segun el numero de courant
# C < 0.25
C = 0.05

maxVel = max(materialsList.values())
dt = minDX*C/maxVel

# Lambdificar g en bcondList
aux = dict()
for k,v in bcondList.items():
    aux[k] = (v[0],v[1], eval(v[2]))
bcondList = aux

I =  lambda x,y: 0
v0 = lambda x,y: 0

#%% solucion

phis, wi,xi = getConstants()

pts = mesh.points
triangles = mesh.cells['triangle']

# Primera iteracion
# Ya conocemos u0 y u_m1:

K, M, d = ensamblarMatrices(pts,t[6], triangles, list(membershipIDs),
                            dt,bcondList, materialsList, selectionMaterials)


# Definimos los vectores para la solución
u_n = np.zeros(len(pts))
u_nm1 = np.zeros(len(pts))
u_nm2 = np.zeros(len(pts))


# Primera iteración
for i,pt in enumerate(pts):
    u_nm1[i] = I(pt[0],pt[1])
    u_nm2[i] = v0(pt[0],pt[1])

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
                    sumaj += wk*wj*phis[idx](rk,sj)*(1-sj)*fuente(triPts[idx,0],triPts[idx,1],i*dt)*detJ
                
                sumai += sumaj
        
            qLoc[idx] = sumai
    
    
    q[tri] += qLoc        

q += d

b = 0.5*(dt**2*q - K @ u_nm1) + 2*dt*u_nm2

print(M)
u = LA.solve(M,b)
print(0,u)
u_nm2 = u_nm1
u_nm1 = u

for i in range(10):
    u = solve(M, K, d, fuente, i, dt, u_nm1, u_nm2, triangles, pts)
    print(i,u)
    u_nm2 = u_nm1
    u_nm1 = u