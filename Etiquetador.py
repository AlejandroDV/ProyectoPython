# coding=utf-8
import tkMessageBox

__author__ = 'Alejandro'

from Tkinter import *
import tkFileDialog
import cv2
import numpy as np
from numpy import genfromtxt

vtnPrincipal = Tk()
imagen=None
regiones = []
etiquetas = []
etiqueta_actual = 0
padres_hijos=[]

def buscar():
    global imagen
    file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if file:
        color = cv2.imread(file.name)
        grises = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        ret, imagen = cv2.threshold(grises, 100, 255, cv2.THRESH_BINARY)
        cv2.imshow("Imagen",imagen)


def identificar_regiones():
    global imagen
    global regiones
    if imagen is None:
        tkMessageBox.showerror("Error", "No se cargo la imagen fuente")
    else:
        alto, largo = imagen.shape[:2]
        size = (alto,largo, 1)
        regiones = np.zeros(size)

        print(imagen)
        for f in range(alto):
            for c in range(largo):
                if(imagen[f,c] == 0):
                    regiones[f,c] = 1
        np.savetxt('regiones.txt', regiones, fmt='%1.0f', delimiter=';')


def etiquetar():
    print "etiquetar"
    global regiones
    global etiquetas
    global etiqueta_actual
    global padres_hijos
    cambio = False
    file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if file:
        regiones = genfromtxt(file.name, delimiter=';')
        alto, largo = regiones.shape[:2]
        size = (alto, largo, 1)
        etiquetas = np.zeros(size)
        padres_hijos = np.zeros((1, 2))

        for f in range(alto):
            for c in range(largo):
                if regiones[f, c] == 1:
                    if c == 0 and f == 0:
                        sm = etiquetas[f, c]
                    elif c == 0 and f > 0:
                        sm = etiquetas[f - 1:f + 1, c:c + 1]
                    elif c > 0 and f == 0:
                        sm = etiquetas[f:f + 1, c - 1:c + 1]
                    else:
                        sm = etiquetas[f - 1:f + 1, c - 1:c + 1]

                    etiquetas[f, c] = etiquetado_vecindad(sm)
        print padres_hijos
        np.savetxt('padre-hijo.txt', padres_hijos, fmt='%1.0f', delimiter=';')
        np.savetxt('etiquetas.txt', etiquetas, fmt='%1.0f', delimiter=';')

        filas, columnas = padres_hijos.shape[:2]

        for f in range(alto):
            for c in range(largo):
                if etiquetas[f,c] != 0:
                    for ff in range(filas):
                        if etiquetas[f,c] == padres_hijos[ff,1]:
                            etiquetas[f,c] = padres_hijos[ff,0]

        np.savetxt('etiquetas_normalizado.txt', etiquetas, fmt='%1.0f', delimiter=';')

def etiquetado_vecindad(matriz):
    global etiqueta_actual
    global padres_hijos
    etiqueta = 0
    try:
        alto, largo = matriz.shape[:2]
    except ValueError:
        alto = 1
        largo = 1
    if (alto * largo) == 4:
        a = np.array([matriz[0, 1], matriz[1, 0]])
        minimo = np.amin(a)
        maximo = np.amax(a)
    else:
        minimo = np.amin(matriz)
        maximo = np.amax(matriz)

    if minimo == 0 and maximo == 0:
        etiqueta_actual += 1
        etiqueta = etiqueta_actual
    elif minimo == 0 and maximo != 0:
        etiqueta = maximo
    elif minimo != 0 and maximo != 0:
        etiqueta = minimo
        filas, columnas = padres_hijos.shape[:2]

        if minimo!=maximo:
            existe=False
            for f in range(filas):
                if padres_hijos[f, 0] == minimo and padres_hijos[f, 1] == maximo:
                    existe=True

            if not existe:
                existe = False
                for ff in range(filas):
                    if padres_hijos[ff,1] == minimo:
                        minimo = padres_hijos[ff,0]
                for f in range(filas):
                    if padres_hijos[f, 0] == minimo and padres_hijos[f, 1] == maximo:
                        existe=True
                if not existe:
                    nuevohijo = np.asmatrix(np.array([minimo, maximo]))
                    padres_hijos = np.r_[padres_hijos, nuevohijo]



    #print matriz, "min: ",minimo,"max: ", maximo, "etiq: ",etiqueta
    #print "*********************************************************"
    return etiqueta

btn_buscar = Button(vtnPrincipal, text="Buscar", command=buscar)
btn_identificar_regiones =Button(vtnPrincipal, text="Identificar Regiones", command=identificar_regiones)
btn_etiquetar = Button(vtnPrincipal,text="Etiquetar", command=etiquetar)

btn_buscar.grid(row=0, column=0)
btn_identificar_regiones.grid(row=1, column=0)
btn_etiquetar.grid(row=2, column=0)

vtnPrincipal.mainloop()
