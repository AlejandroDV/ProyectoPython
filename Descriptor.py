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
import os

vtnPrincipal = Tk()
px_mm_x = 0.0
px_mm_y = 0.0
medidas = []
medidas_suavizadas = []
altura_real = 0.0
error_admitido = 0.0
nombre_archivo = ""
imagen_binarizada = None
imagen_descriptiva = None

regiones = []
etiquetas = []
etiqueta_actual = 0
padres_hijos = []


def buscar_datos_config():
    """
    Permite al usuario la carga del archivo de configuración
    :return:
    """
    global px_mm_x
    global px_mm_y
    global medidas
    try:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar el archivo con los Datos de Configuracion')
        if archivo:
            with open(archivo.name, "r") as ins:
                array = []
                for line in ins:
                    array.append(float(line))
            px_mm_x = array[0]
            px_mm_y = array[1]
            txt_x.insert(0, px_mm_x)
            txt_y.insert(0, px_mm_y)
            activar_pestania_suavizado()
    except ValueError:
        tkMessageBox.showerror("Error", "Verifique el archivo seleccionado")
    except:
        tkMessageBox.showerror("Error", "Error Inesperado")


def activar_pestania_suavizado():

    global medidas
    global px_mm_y
    global px_mm_x
    if len(medidas) > 0 and (px_mm_y != 0) and (px_mm_y != 0):
        contenedor_pestanas.tab(1, state="normal")


def buscar_matriz():
    """
    Permite al usuario la selección de la matriz de medidas
    :return:
    """
    global medidas
    global px_mm_y
    global px_mm_x
    global nombre_archivo
    try:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar el archivo con la Matriz de Medidas')
        if archivo:
            medidas = genfromtxt(archivo.name, delimiter=';')
            activar_pestania_suavizado()
            nombre = os.path.split(archivo.name)[1]
            for i in nombre:
                if i != ".":
                    nombre_archivo += i
                else:
                    break
            txt_matriz_cargada.delete(0, END)
            txt_matriz_cargada.insert(0, nombre_archivo)
    except ValueError:
        tkMessageBox.showerror("Error", "Verifique el archivo seleccionado")
    except:
        tkMessageBox.showerror("Error", "Error Inesperado")


def dibujar_3d(opcion):
    """
    Realiza el trazado 3D de la superficie seleccionada
    :param opcion:
    :return:
    """
    global medidas
    global px_mm_x
    global px_mm_y
    global medidas_suavizadas

    z = []
    if opcion == 1:
        z = medidas
    elif opcion == 2:
        z = medidas_suavizadas

    if (px_mm_y != 0) and (px_mm_y != 0) and (len(z) > 0):

        alto, largo = z.shape[:2]
        x = np.zeros(largo)
        y = np.zeros(alto)

        for c in range(len(x)):
            x[c] = px_mm_x * c

        for c in range(len(y)):
            y[c] = px_mm_y * c

        #np.savetxt('test.txt', medidas, fmt='%1.2f', delimiter=';')

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x, y = np.meshgrid(x, y)

        # Tipo de gráfico
        surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

        # configuraciones del eje z
        ax.set_zlim(-1.01, 15)
        ax.zaxis.set_major_locator(LinearLocator(10))
        ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        fig.colorbar(surf, shrink=0.5, aspect=5)

        plt.show()
    else:
        tkMessageBox.showerror("Error", "Faltan Buscar Datos")


def suavizar():
    """
    Realiza el suavizado de la matriz de medidas
    :return:
    """
    global altura_real
    global error_admitido
    global medidas
    global medidas_suavizadas
    global nombre_archivo
    alto, largo = medidas.shape[:2]
    try:
        altura_real = float(txt_altura_real.get())
        error_admitido = float(txt_error.get())
        medidas_suavizadas = np.copy(medidas)
        for f in range(alto):
            for c in range(largo):
                if abs( altura_real - medidas_suavizadas[f, c]) <= error_admitido:
                    medidas_suavizadas[f, c] = altura_real
        nombre_archivo_txt = nombre_archivo + '_suavizado.txt'
        np.savetxt(nombre_archivo_txt, medidas_suavizadas, fmt='%1.2f', delimiter=';')
        tkMessageBox.showinfo("Atención", "Las medidas suavizadas se almacenaron en: " + nombre_archivo_txt)
    except ValueError:
        tkMessageBox.showerror("Error", "Verifique los datos cargados")


def binarizar():
    """
    Binariza la matriz de medidas acorde al valor esperado
    :return:
    """
    global medidas_suavizadas
    global altura_real
    global nombre_archivo
    global imagen_binarizada
    if len(medidas_suavizadas) == 0:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
        if archivo:
            medidas_suavizadas = genfromtxt(archivo.name, delimiter=';')
    alto, largo = medidas_suavizadas.shape[:2]
    size = (alto, largo, 1)
    imagen_binarizada = np.zeros(size)
    for f in range(alto):
        for c in range(largo):
            if medidas_suavizadas[f, c] == altura_real:
                imagen_binarizada[f, c] = 255
    nombre_archivo_imagen = nombre_archivo + '_binario.png'
    cv2.imshow(nombre_archivo + ' Binarizado', imagen_binarizada)
    cv2.imwrite(nombre_archivo_imagen, imagen_binarizada)
    tkMessageBox.showinfo("Atención", "La imagen Binarizada se guardaron en: " + nombre_archivo_imagen)
    txt_imagen_binarizada.insert(0, nombre_archivo_imagen)


def buscar_imagen_binarizada():
    """
    Permite al usuario seleccionar una imagen binaria
    :return:
    """
    global imagen_binarizada
    if imagen_binarizada is None:
        file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar la Imagen Binarizada a Etiquetar')
        if file:
            color = cv2.imread(file.name)
            grises = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
            ret, imagen_binarizada = cv2.threshold(grises, 100, 255, cv2.THRESH_BINARY)
            cv2.imshow("Imagen Binarizada", imagen_binarizada)
            nombre_imagen_binarizada = os.path.split(file.name)[1]
            txt_imagen_binarizada.insert(0, nombre_imagen_binarizada)


def identificar_regiones():
    """
    Ientifica las regiones existentes en la imagen binarizada
    :return:
    """
    global imagen_binarizada
    global regiones
    global nombre_archivo
    if imagen_binarizada is None:
        tkMessageBox.showerror("Error", "No se cargo la imagen fuente")
    else:
        alto, largo = imagen_binarizada.shape[:2]
        size = (alto, largo, 1)
        regiones = np.zeros(size)

        print(imagen_binarizada)
        for f in range(alto):
            for c in range(largo):
                if imagen_binarizada[f, c] == 0:
                    regiones[f, c] = 1
        nombre_etiquetas_archivo = nombre_archivo + '_regiones.txt'
        np.savetxt(nombre_etiquetas_archivo, regiones, fmt='%1.0f', delimiter=';')
        tkMessageBox.showinfo("Atención", "Se guardo el registro de regiones detectadas en:" + nombre_etiquetas_archivo)


def etiquetar():
    """
    Realiza el proceso de etiquetado según la matriz de regiones detectadas
    :return:
    """
    global regiones
    global etiquetas
    global etiqueta_actual
    global padres_hijos
    global nombre_archivo
    global imagen_binarizada
    cambio = False
    if len(regiones) == 0:
        file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar El archivo con las Regiones Detectadas')
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

    nombre_padre_hijo = nombre_archivo + '_padre-hijo.txt'
    nombre_etiquetas_archivo = nombre_archivo + '_etiquetas.txt'

    np.savetxt(nombre_padre_hijo, padres_hijos, fmt='%1.0f', delimiter=';')
    np.savetxt(nombre_etiquetas_archivo, etiquetas, fmt='%1.0f', delimiter=';')

    filas, columnas = padres_hijos.shape[:2]

    for f in range(alto):
        for c in range(largo):
            if etiquetas[f, c] != 0:
                for ff in range(filas):
                    if etiquetas[f, c] == padres_hijos[ff, 1]:
                        etiquetas[f, c] = padres_hijos[ff, 0]

    nombre_etiquetas_normalizadas = nombre_archivo + '_etiquetas_normalizado.txt'
    np.savetxt(nombre_etiquetas_normalizadas, etiquetas, fmt='%1.0f', delimiter=';')

    tkMessageBox.showinfo("Atención", "Se guardaron 3 archivos:\n"
                                        "1- Prioridad de Etiquetas: " + nombre_padre_hijo + "\n"
                                        "2- Etiquetas: "+nombre_etiquetas_archivo + "\n"
                                        "3- Etiquetas Normalizadas: " + nombre_etiquetas_normalizadas
                          )


def etiquetado_vecindad(matriz):
    """
    Gestiona la matriz de Prioridades
    :param matriz:
    :return:
    """
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

        if minimo != maximo:
            existe = False
            for f in range(filas):
                if padres_hijos[f, 0] == minimo and padres_hijos[f, 1] == maximo:
                    existe = True

            if not existe:
                existe = False
                for ff in range(filas):
                    if padres_hijos[ff, 1] == minimo:
                        minimo = padres_hijos[ff, 0]
                for f in range(filas):
                    if padres_hijos[f, 0] == minimo and padres_hijos[f, 1] == maximo:
                        existe = True
                if not existe:
                    nuevohijo = np.asmatrix(np.array([minimo, maximo]))
                    padres_hijos = np.r_[padres_hijos, nuevohijo]

    #print matriz, "min: ",minimo,"max: ", maximo, "etiq: ",etiqueta
    #print "*********************************************************"
    return etiqueta


def buscar_etiquetas():
    """
    Permite al usuario seleccionar una matriz de etiquetas reconocidas
    :return:
    """
    global etiquetas
    global nombre_archivo
    img_preliminar = []

    if len(etiquetas) == 0:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar El archivo con las Regiones Detectadas')
        if file:
            etiquetas = genfromtxt(archivo.name, delimiter=';')
            if len(nombre_archivo) == 0:
                nombre = os.path.split(archivo.name)[1]
                print nombre
                for i in nombre:
                    if i != ".":
                        nombre_archivo += i
                    else:
                        break
            txt_etiquetas.delete(0, END)
            txt_etiquetas.insert(0, nombre_archivo)
    for item in np.unique(etiquetas):
        lst_etiquetas.insert(END, item)


def describir_etiqueta():
    """
    Compendio de descriptores de región
    :return:
    """
    global etiquetas
    global imagen_descriptiva
    global px_mm_x
    global px_mm_y
    #alto, largo = etiquetas.shape[:2]
    largo, ancho = etiquetas.shape[:2]
    print largo, ancho
    if len(etiquetas) != 0:

        etiqueta_seleccionada = int(lst_etiquetas.get(lst_etiquetas.curselection()))

        "Se describitá el número identificador de la etiqueta seleccionada"
        tamanio = "L: " + str(largo * px_mm_y) + "mm ; A: " + str(ancho * px_mm_x) + "mm"
        #txt_otrosdescriptores.insert(END, ("Ancho: " + str(ancho) + " x " + str(px_mm_x) + " = " + str(ancho * px_mm_x) + "mm" + "\n"))
        #txt_otrosdescriptores.insert(END, ("Alto: " + str(largo) + " x " + str(px_mm_x) + " = " + str(largo * px_mm_y) + "mm" + "\n"))
        txt_descriptor_tamanio.delete(0, END)
        txt_descriptor_tamanio.insert(0, tamanio)

        "Se mostrará la imagen representativa"
        imagen_descriptiva = np.ones((largo, ancho)) * 255
        for f in range(largo):
            for c in range(ancho):
                if etiquetas[f, c] == etiqueta_seleccionada:
                    imagen_descriptiva[f, c] = 0
        cv2.imshow('Region', imagen_descriptiva)
        np.savetxt("etiqueta_filtrada.txt", imagen_descriptiva, fmt='%1.0f', delimiter=';')

        "Se contarán los píxeles que forman la imagen"
        contador_etiqueta = 0
        contador_fondo = 0
        for f in range(largo):
            for c in range(ancho):
                if imagen_descriptiva[f, c] == 0:
                    contador_etiqueta += 1
                else:
                    contador_fondo += 1
        #print contador_etiqueta, contador_fondo, contador_etiqueta+contador_fondo
        txt_descriptor_contador.delete(0, END)
        txt_descriptor_contador.insert(0, contador_etiqueta)

        "Se determinará el contorno usando cv2.findContours. Se creará una nieva imagen invertida"
        imagen_descriptiva = imagen_descriptiva.astype(np.uint8)
        ret, imagen_descriptiva_inv = cv2.threshold(imagen_descriptiva, 200, 255, cv2.THRESH_BINARY_INV)
        #cv2.imshow('Region invertida', imagen_descriptiva_inv)
        contours, hierarchy = cv2.findContours(imagen_descriptiva_inv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #print "**************************************************"
        #print contours, hierarchy
        cv2.drawContours(imagen_descriptiva_inv, contours, -1, (255, 255, 255), 1)
        cv2.imshow('Imagen Invertida', imagen_descriptiva_inv)
        txt_coordenadas.delete(1.0, END)
        for i in contours:
            txt_coordenadas.insert(END, i)

        #perimetro = cv2.arcLength(contours,True)
        #print perimetro

        txt_otrosdescriptores.delete(1.0, END)
        "Descripción de Superficie"
        txt_otrosdescriptores.insert(END, ("Superficie: " + str('{0:.3g}'.format(((px_mm_x * px_mm_y) * contador_etiqueta))) + "mm2" + "\n"))



    else:
        tkMessageBox.showinfo("Atención", "No existe una matriz de Etiquetas cargada:")


#-------------------------------------------------------
#GUI
contenedor_pestanas = Notebook(vtnPrincipal)
pestana_cargar_datos = Frame(contenedor_pestanas)
pestana_suavizado = Frame(contenedor_pestanas)
pestana_etiquetar = Frame(contenedor_pestanas)
pestana_descriptor = Frame(contenedor_pestanas)
contenedor_pestanas.add(pestana_cargar_datos, text="Cargar Datos")
contenedor_pestanas.add(pestana_suavizado, text="Suavizado y Binarizado")
contenedor_pestanas.add(pestana_etiquetar, text="Etiquetado")
contenedor_pestanas.add(pestana_descriptor, text="Descripción")
contenedor_pestanas.pack()

# region Pestaña de selección de datos
btn_seleccionar_configuracion = Button(pestana_cargar_datos, text="Buscar Datos Configuracion", command=buscar_datos_config)
lbl_x =                         Label(pestana_cargar_datos, text="X:")
txt_x =                         Entry(pestana_cargar_datos, width=7)
lbl_y =                         Label(pestana_cargar_datos, text="Y:")
txt_y =                         Entry(pestana_cargar_datos, width=7)
btn_seleccionar_matriz =        Button(pestana_cargar_datos, text="Seleccionar Matriz", command=buscar_matriz)
lbl_matriz_cargada =            Label(pestana_cargar_datos, text="Matriz cargada:")
txt_matriz_cargada =            Entry(pestana_cargar_datos, width=14)
btn_dibujar_3d =                Button(pestana_cargar_datos, text="Dibujar 3D", command=lambda: dibujar_3d(1))

txt_matriz_cargada.insert(0, "No")

btn_seleccionar_configuracion.grid( row=0, column=0, columnspan=2)
lbl_x.grid(                         row=1, column=0)
txt_x.grid(                         row=1, column=1)
lbl_y.grid(                         row=2, column=0)
txt_y.grid(                         row=2, column=1)
btn_seleccionar_matriz.grid(        row=3, column=0, columnspan=2)
lbl_matriz_cargada.grid(            row=4, column=0)
txt_matriz_cargada.grid(            row=4, column=1)
btn_dibujar_3d.grid(                row=5, column=0, columnspan=2)

contenedor_pestanas.tab(1, state="disabled")

# endregion

# region Suavizado y Binarizado
lbl_altura_real = Label(pestana_suavizado, text="Valor Real:")
txt_altura_real = Entry(pestana_suavizado, width=7)
lbl_error = Label(pestana_suavizado, text="Error admitido:")
txt_error = Entry(pestana_suavizado, width=7)
btn_suavizar = Button(pestana_suavizado, text="Suavizar:", command=suavizar)
btn_dibujar_3d_suavizado = Button(pestana_suavizado, text="Dibujar 3D:", command=lambda: dibujar_3d(2))
btn_binarizar = Button(pestana_suavizado, text="Binarizar", command=binarizar)

txt_altura_real.insert(0, 15)
txt_error.insert(0, 1)

lbl_altura_real.grid(           row=0, column=0)
txt_altura_real.grid(           row=0, column=1)
lbl_error.grid(                 row=1, column=0)
txt_error.grid(                 row=1, column=1)
btn_suavizar.grid(              row=2, column=0, columnspan=2)
btn_dibujar_3d_suavizado.grid(  row=3, column=0, columnspan=2)
btn_binarizar.grid(             row=4, column=0, columnspan=2)

# endregion

# region Etiquetado

btn_buscar_imagen_binarizada = Button(pestana_etiquetar, text="Buscar Imagen Bin", command=buscar_imagen_binarizada)
txt_imagen_binarizada = Entry(pestana_etiquetar)
btn_identificar_regiones = Button(pestana_etiquetar, text="Identificar Regiones", command=identificar_regiones)
btn_etiquetar = Button(pestana_etiquetar, text="Etiquetar", command=etiquetar)

btn_buscar_imagen_binarizada.grid(  row=0, column=0)
txt_imagen_binarizada.grid(         row=0, column=1)
btn_identificar_regiones.grid(      row=1, column=0)
btn_etiquetar.grid(                 row=2, column=0)

# endregion

# region Descripción
btn_buscar_etiquetas = Button(pestana_descriptor, text="Buscar Matriz Etiquetas", command=buscar_etiquetas)
txt_etiquetas = Entry(pestana_descriptor)
btn_describir_etiqueta = Button(pestana_descriptor, text="Describir", command=describir_etiqueta)
lst_etiquetas = Listbox(pestana_descriptor)
lst_etiquetas.pack()
lbl_descriptor_tamanio = Label(pestana_descriptor, text="Tamaño: ")
txt_descriptor_tamanio = Entry(pestana_descriptor)
lbl_descriptor_contador = Label(pestana_descriptor, text="Contador:")
txt_descriptor_contador = Entry(pestana_descriptor)
lbl_coordenadas = Label(pestana_descriptor, text="Codigo Cadena:")
txt_coordenadas = Text(pestana_descriptor, width=17, height=5)
txt_otrosdescriptores = Text(pestana_descriptor, width=50, height=5)

btn_buscar_etiquetas.grid(      row=0, column=0)
txt_etiquetas.grid(             row=0, column=1, columnspan=2)
lst_etiquetas.grid(             row=1, column=0, rowspan=4)
btn_describir_etiqueta.grid(    row=1, column=1, columnspan=2)
lbl_descriptor_tamanio.grid(         row=2, column=1, sticky="e")
txt_descriptor_tamanio.grid(         row=2, column=2)
lbl_descriptor_contador.grid(   row=3, column=1, sticky="e")
txt_descriptor_contador.grid(   row=3, column=2)
lbl_coordenadas.grid(row=4, column=1, sticky="n")
txt_coordenadas.grid(row=4, column=2)
txt_otrosdescriptores.grid(row=5, column=0, columnspan=3)
# endregion

vtnPrincipal.mainloop()
