# coding=utf-8
__author__ = 'Alejandro'


from Tkinter import *
import numpy as np
from numpy import genfromtxt

vtnPrincipal = Tk()

nombre=""
direccion=""

def escribir():
    global nombre
    global direccion
    m=np.ones((2,3))*3
    print m
    nombre = txt_escribir_nombre.get()
    direccion = txt_escribir_direccion.get()
    if len(nombre) == 0:
        nombre = "nombre Vacio"
    if len(direccion) == 0:
        direccion = "direccion Vacio"
    f = open("a.txt","w")
    f.write(nombre)
    f.write("\n")
    f.write(direccion)
    f.write("\n")
    f.close()
    np.savetxt('b.txt', m, fmt='%1.2f', delimiter=';')

def leer():
    m = genfromtxt("b.txt",delimiter=';')
    print m
    with open("a.txt", "r") as ins:
        array = []
        for line in ins:
            array.append(line)
    nombre = array[0]
    direccion = array[1]

    print nombre, direccion


lblf_escribir = LabelFrame(vtnPrincipal, text="Escribir")
lblf_leer = LabelFrame(vtnPrincipal, text="Leer")


lbl_escribir_nombre =       Label(lblf_escribir, text="Nombre:")
txt_escribir_nombre =       Entry(lblf_escribir)
lbl_escribir_direccion =    Label(lblf_escribir, text="Direccion:")
txt_escribir_direccion =    Entry(lblf_escribir)
btn_escribir =              Button(lblf_escribir, text="Escribir", command=escribir)


lblf_escribir.grid(         row=0, column=0)
lbl_escribir_nombre.grid(   row=0, column=0)
txt_escribir_nombre.grid(   row=0, column=1)
lbl_escribir_direccion.grid(row=1, column=0)
txt_escribir_direccion.grid(row=1, column=1)
btn_escribir.grid(          row=2, column=0, columnspan=2)

lbl_leer_nombre =           Label(lblf_leer, text="Nombre:")
txt_leer_nombre =           Entry(lblf_leer)
lbl_leer_direccion =        Label(lblf_leer, text="Direccion:")
txt_leer_direccion =        Entry(lblf_leer)
btn_leer =                  Button(lblf_leer, text="Leer", command=leer)


lblf_leer.              grid(row=1, column=0)
lbl_leer_nombre.        grid(row=0, column=0)
txt_leer_nombre.        grid(row=0, column=1)
lbl_leer_direccion.     grid(row=1, column=0)
txt_leer_direccion.     grid(row=1, column=1)
btn_leer.               grid(row=2, column=0, columnspan=2)


vtnPrincipal.mainloop()