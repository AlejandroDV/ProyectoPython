# coding=utf-8
__author__ = 'usuario'

import cv2
from Tkinter import *
import tkMessageBox
import copy
import time
from datetime import datetime
import numpy as np
import tkFileDialog
import cv2.cv as cv
import time
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

vtnPrincipal = Tk()
calibracion_base = 444
px_mm_z = 0.188
px_mm_x = 0.162
px_mm_y = 1
id_dispositivo = 0
medidas = []
camara = None
umbral = 250
velocidad = 0.0
video = None
extremo_izquierdo = 20
extremo_derecho = 636


def esqueletizador(imagen_color, calibracion):
    """
    Realiza el esqueletizado de la imagen con la proyección láser, pasada como parámetro
    :param imagen_color: La imagen con la proyección láser
    :param calibracion: si se corresponde a una etapa de calibración o no (True|False)
    :return: La imagen esqueletizada
    """
    global calibracion_base
    global umbral
    global extremo_izquierdo
    global extremo_derecho
    flaco = None

    # Imagen Grises
    grises = cv2.cvtColor(imagen_color, cv2.COLOR_BGR2GRAY)
    # Imagen Binaria
    ret, binario = cv2.threshold(grises, umbral, 255, cv2.THRESH_BINARY_INV)
    # Imagen Suavizada
    suavizado = cv2.medianBlur(binario, 5)
    alto, largo = suavizado.shape[:2]
    # Buscar la primera fila
    # sup = superior(suavizado)
    sup = detectar_extremos(suavizado, "n")[0]
    flaco = copy.copy(suavizado)
    # Esqueletización

    for c in range(largo):
        inicial = 0
        # se acota el range entre el sup y el tamaño de la imagen
        for f in range(sup, alto, 1):
            if suavizado[f, c] == 0:
                inicial = f
            if inicial != 0:
                break
        if inicial == 0:
            # la columna está vacia
            if extremo_izquierdo !=0 and extremo_derecho !=0:
                if calibracion_base == 0:
                    # si no se calibró la línea base
                    flaco[alto - 2, c] = 0
                else:
                    # si se calibró la linea base
                    flaco[calibracion_base, c] = 0
        else:
            # se quitan los píxeles inferiores
            for i in range(inicial + 1, alto, 1):
                flaco[i, c] = 255
    if calibracion:
        cv2.line(flaco, (0, sup), (largo, sup), (0, 200, 200), 1)
        cantidad_bits_contados = (alto * largo) - cv2.countNonZero(suavizado)
        #txt_conteo.delete(0, END)
        #txt_conteo.insert(0, cantidad_bits_contados)
        vtnPrincipal.update()
        calibracion_base = sup
        #txt_superior.delete(0, END)
        #txt_superior.insert(0, sup)

    cv2.imshow('Color', imagen_color)
    cv2.waitKey(5)
    return flaco


def detectar_extremos(imagen, orientacion):
    """
    Detecta los extremos de la imagen. Usada principalmente sobre una imagen esqueletizada
    :param imagen: Imagen Original
    :param orientacion: cadenas con las coordenadas solicitadas "n"(norte)"s"(sur)"e"(este)"o"(oeste)
    :return: vector con los valores extremos solicitados [Norte, Sur, Este, Oeste]
    """
    extremos = [0, 0, 0, 0]
    alto, largo = imagen.shape[:2]
    if "n" in orientacion:
        for f in range(alto):
            if cv2.countNonZero(imagen[f, :]) < largo:
                extremos[0] = f
                break

    if "s" in orientacion:
        for f in range(alto - 1, -1, -1):
            if cv2.countNonZero(imagen[f, :]) < largo:
                extremos[1] = f - 1
                break

    if "e" in orientacion:
        for c in range(largo - 1, -1, -1):
            if cv2.countNonZero(imagen[:, c]) < alto:
                extremos[2] = c
                break

    if "o" in orientacion:
        for c in range(largo):
            if cv2.countNonZero(imagen[:, c]) < alto:
                extremos[3] = c
                break

    return extremos


def buscar_video():
    """
    :return:
    """
    global video
    file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if file:
        video = cv2.VideoCapture(file.name)
        """
        cap = cv.CaptureFromFile(file.name)
        video = cap
        nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
        fps = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
        print "total frame", nframes
        print "fps", fps
        print ' currpos of videofile', cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_POS_MSEC)
        txt_video.delete(0, END)
        txt_video.insert(0, file.name)
        try:
            waitpermillisecond = int(1 * 1000 / fps)
            print "waitpermillisecond", waitpermillisecond
        except:
            pass
        print cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FOURCC)
        """


def reproducir_video():
    """
    :return:
    """
    global video
    if video == None:
        tkMessageBox.showerror("Error", "No se seleccionó el video")
    else:
        nframes = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_COUNT))
        for f in xrange(nframes):
            frameimg = cv.QueryFrame(video)
            cv.ShowImage("hcq", frameimg)
            cv.WaitKey(1)


def generar_3d():
    """
    Generación de la matriz de alturas.
    :return: Matriz de alturas
    """

    global video
    global px_mm_x
    global px_mm_y
    global px_mm_z
    global extremo_izquierdo
    global extremo_derecho
    global calibracion_base

    print video, px_mm_x, px_mm_y, px_mm_z, extremo_izquierdo, extremo_derecho, calibracion_base

    if validar_datos_generar_3d():
        columnas = ((extremo_derecho - extremo_izquierdo) + 1)
        matriz = np.zeros((1, columnas))

        while video.isOpened():
            ret, frame = video.read()
            if frame != None:
                flaco = esqueletizador(frame, False)
                cv2.imshow('Flaco', flaco)
                vector = medicion_perfil(flaco, columnas)
                #transforma el vector a una matriz
                matriz_parciales = np.asmatrix(vector)
                # inserta la nueva matriz en una nueva fila de la matriz de mediciones
                matriz = np.r_[matriz, matriz_parciales]

            else:
                video.release()
        dibujar_3d(matriz)


def medicion_perfil(imagen, columnas):
    """
        se medirá 1 perfil completo
    :return: vector de medidas
    """
    global video
    global extremo_izquierdo
    global extremo_derecho
    global calibracion_base
    global px_mm_z

    medidas = np.zeros(columnas)

    superior = detectar_extremos(imagen, "n")[0]
    alto, largo = imagen.shape[:2]
    for c in range(extremo_izquierdo, extremo_derecho+1, 1):
        for f in range((alto - 1), superior, -1):
            if imagen[f, c] == 0:
                medidas[c-extremo_izquierdo] = ((calibracion_base-f) * px_mm_z)
                break
    return medidas


def validar_datos_generar_3d():

    global px_mm_x
    global px_mm_z
    global px_mm_y
    global calibracion_base
    global video
    global velocidad
    global extremo_derecho
    global extremo_izquierdo

    resultado = True
    mensaje=""

    if px_mm_y == 0:
        if len(txt_y.get()) == 0:
            mensaje = "No se conoce la el patron Y\n"
            resultado=False
        else:
            px_mm_y = float(txt_y.get())

    if px_mm_x == 0:
        if len(txt_x.get()) == 0:
            mensaje = mensaje + "No se conoce el patron en X\n"
            resultado=False
        else:
            px_mm_x = float(txt_x.get())

    if px_mm_z == 0:
        if len(txt_z.get()) == 0:
            mensaje = mensaje + "No se conoce el patron en Z\n"
            resultado=False
        else:
            px_mm_z = float(txt_z.get())

    if calibracion_base == 0:
        if len(txt_base.get()) ==0:
            mensaje = mensaje + "No se conoce la linea base\n"
            resultado=False
        else:
            try:
                calibracion_base = int(txt_base.get())
            except:
                tkMessageBox.showerror("Error de tipo", "El valor de Base debe ser un entero")

    if extremo_izquierdo == 0:
        if len(txt_iz.get()) ==0:
            mensaje = mensaje + "No se conoce el extremo izquierdo\n"
            resultado=False
        else:
            try:
                extremo_izquierdo = int(txt_iz.get())
            except:
                tkMessageBox.showerror("Error de tipo", "El valor de Extremo Izquierdo debe ser un entero")

    if extremo_derecho == 0:
        if len(txt_der.get()) ==0:
            mensaje = mensaje + "No se conoce el extremo derecho\n"
            resultado=False
        else:
            try:
                extremo_derecho = int(txt_der.get())
            except:
                tkMessageBox.showerror("Error de tipo", "El valor de Extremo Izquierdo debe ser un entero")

    if video is None:
        mensaje = mensaje + "No se cargó el video\n"
        resultado=False

    if not resultado:
        tkMessageBox.showerror("Error", mensaje)

    return resultado


def dibujar_3d(Z):
    global px_mm_x
    global px_mm_y

    alto, largo = Z.shape[:2]
    X = np.zeros(largo)
    Y = np.zeros(alto)

    for c in range(len(X)):
        X[c] = px_mm_x * c

    for c in range(len(Y)):
        Y[c] = px_mm_y * c

    print "X ", len(X), X
    print "Y", len(Y), Y
    print "Z", Z.shape

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


lblf_generacion3D = LabelFrame(vtnPrincipal, text="5 - Generación 3D")

# region 5 - Medición y Generación 3D

lbl_x = Label(      lblf_generacion3D, text="X")
lbl_z = Label(      lblf_generacion3D, text="Z")
lbl_y = Label(      lblf_generacion3D, text="Y")
lbl_iz = Label(     lblf_generacion3D, text="Izquierdo")
lbl_der = Label(    lblf_generacion3D, text="Derecho")
lbl_base = Label(   lblf_generacion3D, text="Base")
lbl_video = Label(  lblf_generacion3D, text="Video")

txt_x = Entry(      lblf_generacion3D, width=10)
txt_z = Entry(      lblf_generacion3D, width=10)
txt_y = Entry(      lblf_generacion3D, width=10)
txt_iz = Entry(     lblf_generacion3D, width=10)
txt_der = Entry(    lblf_generacion3D, width=10)
txt_base = Entry(   lblf_generacion3D, width=10)
txt_video = Entry(  lblf_generacion3D, width=10)

btn_buscar_archivo = Button(        lblf_generacion3D, text='Buscar Video', command=buscar_video)
btn_generar3D = Button(             lblf_generacion3D, text="Generar 3D", command=generar_3d)


lblf_generacion3D.grid(         row=0, column=0, sticky="we")
lbl_x.grid(                     row=0, column=0, sticky="we")
txt_x.grid(                     row=0, column=1, sticky="we")
lbl_z.grid(                     row=1, column=0, sticky="we")
txt_z.grid(                     row=1, column=1, sticky="we")
lbl_y.grid(                     row=2, column=0, sticky="we")
txt_y.grid(                     row=2, column=1, sticky="we")
lbl_iz.grid(                    row=3, column=0, sticky="we")
txt_iz.grid(                    row=3, column=1, sticky="we")
lbl_der.grid(                   row=4, column=0, sticky="we")
txt_der.grid(                   row=4, column=1, sticky="we")
lbl_base.grid(                  row=5, column=0, sticky="we")
txt_base.grid(                  row=5, column=1, sticky="we")
btn_buscar_archivo.grid(        row=6, column=0, columnspan=2)
lbl_video.grid(                 row=7, column=0, sticky="we")
txt_video.grid(                 row=7, column=1, sticky="we")
btn_generar3D.grid(             row=8, column=0, columnspan=2)


# endregion
vtnPrincipal.mainloop()