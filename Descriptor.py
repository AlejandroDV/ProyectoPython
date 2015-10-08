# coding=utf-8
__author__ = 'Alejandro'

import cv2
from Tkinter import *
import tkMessageBox
import numpy as np
import tkFileDialog
import cv2.cv as cv
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from ttk import *
from numpy import genfromtxt

vtnPrincipal = Tk()
px_mm_x = 0.0
px_mm_y = 0.0
medidas = []
medidas_suavizadas = []
altura_real = 0.0
error_admitido = 0.0


def buscar_datos_config():
    global px_mm_x
    global px_mm_y
    global medidas
    archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if archivo:
        with open(archivo.name, "r") as ins:
            array = []
            for line in ins:
                array.append(float(line))
        px_mm_x = array[0]
        px_mm_y = array[1]
        txt_x.insert(0, px_mm_x)
        txt_y.insert(0, px_mm_y)
        if len(medidas) > 0:
            activar_pestania2()


def activar_pestania2():
    contenedor_pestanas.tab(1,state="normal")


def buscar_matriz():
    global medidas
    global px_mm_y
    global px_mm_x
    archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if archivo:
        medidas = genfromtxt(archivo.name, delimiter=';')
        txt_matriz_cargada.delete(0,END)
        txt_matriz_cargada.insert(0,"OK")
        if (px_mm_y != 0) and (px_mm_y != 0):
            activar_pestania2()


def dibujar_3d(opcion):
    global medidas
    global px_mm_x
    global px_mm_y
    global medidas_suavizadas

    Z=[]
    if opcion==1:
        Z=medidas
    elif opcion==2:
        Z=medidas_suavizadas

    if (px_mm_y != 0) and (px_mm_y != 0) and (len(Z) > 0):


        alto, largo = Z.shape[:2]
        X = np.zeros(largo)
        Y = np.zeros(alto)

        for c in range(len(X)):
            X[c] = px_mm_x * c

        for c in range(len(Y)):
            Y[c] = px_mm_y * c

        #np.savetxt('test.txt', medidas, fmt='%1.2f', delimiter=';')

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        X, Y = np.meshgrid(X, Y)

        # Tipo de gráfico
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

        # configuraciones del eje z
        ax.set_zlim(-1.01, 15)
        ax.zaxis.set_major_locator(LinearLocator(10))
        ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        fig.colorbar(surf, shrink=0.5, aspect=5)

        plt.show()
    else:
        tkMessageBox.showerror("Error", "Faltan Buscar Datos")


def suavizar():
    global altura_real
    global error_admitido
    global medidas
    global medidas_suavizadas
    alto, largo = medidas.shape[:2]
    try:
        altura_real = float(txt_altura_real.get())
        error_admitido = float(txt_error.get())
        medidas_suavizadas = np.copy(medidas)
        for f in range(alto):
            for c in range(largo):
                if ( abs( altura_real - medidas_suavizadas[f, c] ) <= error_admitido ):
                    medidas_suavizadas[f, c] = altura_real
        np.savetxt('suavizado.txt', medidas_suavizadas, fmt='%1.2f', delimiter=';')
    except ValueError:
        tkMessageBox.showerror("Error", "Verifique los datos cargados")


def binarizar():
    global medidas_suavizadas
    global altura_real
    if len(medidas_suavizadas)==0:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
        if archivo:
            medidas_suavizadas = genfromtxt(archivo.name, delimiter=';')
    alto, largo = medidas_suavizadas.shape[:2]
    size = (alto,largo, 1)
    img = np.zeros(size)
    for f in range(alto):
        for c in range(largo):
            if medidas_suavizadas[f, c] == altura_real:
                img[f, c] = 255
    cv2.imshow('result', img)
    cv2.imwrite('binario.png',img)


contenedor_pestanas = Notebook(vtnPrincipal)
pestana_cargar_datos = Frame(contenedor_pestanas)
pestana_suavizado = Frame(contenedor_pestanas)
pestana_binarizar = Frame(contenedor_pestanas)
contenedor_pestanas.add(pestana_cargar_datos, text="Cargar Datos")
contenedor_pestanas.add(pestana_suavizado, text="Suavizado")
contenedor_pestanas.add(pestana_binarizar, text="Binarizar")
contenedor_pestanas.pack()

# region Pestaña de selección de datos
btn_seleccionar_configuracion = Button(pestana_cargar_datos, text="Buscar Datos Configuracion", command=buscar_datos_config)
lbl_x =                         Label(pestana_cargar_datos, text="X:" )
txt_x =                         Entry(pestana_cargar_datos, width=7)
lbl_y =                         Label(pestana_cargar_datos, text="Y:")
txt_y =                         Entry(pestana_cargar_datos, width=7)
btn_seleccionar_matriz =        Button(pestana_cargar_datos, text="Seleccionar Matriz", command=buscar_matriz)
lbl_matriz_cargada =            Label(pestana_cargar_datos, text="Matriz cargada:")
txt_matriz_cargada =            Entry(pestana_cargar_datos, width=7)
btn_dibujar_3d =                Button(pestana_cargar_datos, text="Dibujar 3D", command=lambda: dibujar_3d(1))

txt_matriz_cargada.insert(0,"No")

btn_seleccionar_configuracion.grid( row=0, column=0, columnspan=2)
lbl_x.grid(                         row=1, column=0)
txt_x.grid(                         row=1, column=1)
lbl_y.grid(                         row=2, column=0)
txt_y.grid(                         row=2, column=1)
btn_seleccionar_matriz.grid(        row=3, column=0, columnspan=2)
lbl_matriz_cargada.grid(            row=4, column=0)
txt_matriz_cargada.grid(            row=4, column=1)
btn_dibujar_3d.grid(                row=5, column=0, columnspan=2)

contenedor_pestanas.tab(1,state="disabled")

# endregion

# region Suavizado de superficie
lbl_altura_real = Label(pestana_suavizado, text="Valor Real:")
txt_altura_real = Entry(pestana_suavizado, width=7)
lbl_error = Label(pestana_suavizado, text="Error admitido:")
txt_error = Entry(pestana_suavizado, width=7)
btn_suavizar = Button(pestana_suavizado, text="Suavizar:", command=suavizar)
btn_dibujar_3d_suavizado = Button(pestana_suavizado, text="Dibujar 3D:", command=lambda: dibujar_3d(2))

lbl_altura_real.grid(           row=0, column=0)
txt_altura_real.grid(           row=0, column=1)
lbl_error.grid(                 row=1, column=0)
txt_error.grid(                 row=1, column=1)
btn_suavizar.grid(              row=2, column=0, columnspan=2)
btn_dibujar_3d_suavizado.grid(  row=3, column=0, columnspan=2)

# endregion

# region Binarizacion

btn_binarizar = Button(pestana_binarizar, text="Binarizar", command=binarizar)
btn_binarizar.grid(row=0, column=0)

#endregion
vtnPrincipal.mainloop()
