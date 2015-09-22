# coding=utf-8
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.gca(projection='3d')

# generación de datos
'''
X = np.arange(-5, 5, 0.25)
Y = np.arange(-5, 5, 0.25)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)
'''
X = [0,1,2,3,4]
Y = [0,1,2,3,4]
X, Y = np.meshgrid(X, Y)
Z = [[1,1,1,1,1],[1,0.5,0.5,0.5,1],[1,0.5,2,0.5,1],[1,0.5,0.5,0.5,1],[1,1,1,1,1]]

# Tipo de gráfico
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,linewidth=0, antialiased=False)

# configuraciones del eje z
ax.set_zlim(-1.01, 4)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

