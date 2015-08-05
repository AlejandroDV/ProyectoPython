# coding=utf-8
__author__ = 'Alejandro'

"""
Acciones:
    1- Es capaz de capturar la señal de video de un dispositivo en particular pasado su identificador
    2- Procesa la señal de video para obtener una versión esqueletizada de la proyección láser
        2.1- El siavizado es con blur51 = cv2.medianBlur(img, 5)
        2.2- Busca los puntos extremos de la línea láser
        2.3- Para la esqueletización se capturan los píxeles correspondientes a la parte superior de la línea láser
    3- Con la información estadística es posible realizar ajustes al proyector láser y a la cámara
    4- Se ingresa la medida en vertical y horizonal del objeto de calibración y luego de procesar la señal de video y
        determinar la región de interés correspondiente al patrón, se calcula la relación pixel-milímetros
    5- Luego de disponer un nuevo objeto en la base, el sistema determinar la separación entre las filas de la
        plataforma de escaneo y el nuevo objeto. El resultado es multiplicado por la medida obtenida en el punto 4
"""

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

vtnPrincipal = Tk()
calibracion = 0
pxXmmV = 0.0
pxXmmH = 0.0
id_dispositivo = 0
medidas = []
camara = None


def enlazar_camara(accion):

    global id_dispositivo
    global pxXmmV
    global pxXmmH
    global calibracion
    global medidas
    global camara
    sup = 0
    inf_patron=0

    frames = 0


    # Validacion de Datos
    if validador_datos() == 0:

        camara = cv2.VideoCapture(int(txt_id_dispositivo.get()))

        while (frames < 10):

            # Lectura de la señal de video
            ret, frame = camara.read()

            # Imagen Grises
            grises = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Imagen Binaria
            ret, binario = cv2.threshold(grises, 254, 255, cv2.THRESH_BINARY_INV)

            # Imagen Suavizada
            suavizado = cv2.medianBlur(binario, 5)

            alto, largo = suavizado.shape[:2]

            # Buscar la primera fila
            sup = superior(suavizado)

            flaco = copy.copy(suavizado)

            for c in range(largo):

                inicial = 0
                # se acota el range entre el sup y el tamaño de la imagen
                for f in range(sup, alto, 1):
                    if suavizado[f, c] == 0:
                        inicial = f
                    if inicial != 0:
                        break
                if inicial == 0:
                    if calibracion == 0:
                        flaco[alto - 2, c] = 0
                    else:
                        flaco[calibracion, c] = 0
                else:
                    for i in range(inicial + 1, alto, 1):
                        flaco[i, c] = 255
            if len(flaco) > 0 and sup != 0:

                # region Casos de Accion

                if accion == 1:
                    """ Calibración de la cámara"""

                    cantidad_bits_contados = (alto * largo) - cv2.countNonZero(suavizado)

                    calibracion = sup

                    txt_conteo.delete(0, END)
                    txt_conteo.insert(0, cantidad_bits_contados)
                    txt_superior.delete(0, END)
                    txt_superior.insert(0, sup)
                    vtnPrincipal.update()

                    cv2.imshow('Color', frame)
                    cv2.imshow('Suavizado', suavizado)

                elif accion == 2:
                    """Calibración Vertical y Horizontal del patron"""

                    # region Calibración Vertical

                    medida_calibrado = float(txt_valor_muestraV.get())
                    if (calibracion - sup) > 0:
                        pxXmmV = medida_calibrado / (calibracion - sup)
                        txt_pixelmmV.delete(0, END)
                        txt_pixelmmV.insert(0, pxXmmV)

                    # endregion

                    # region Calibracion Horizontal
                    extremos = extremos_patron(flaco)
                    cv2.rectangle(flaco, (extremos[1], sup), (extremos[2], extremos[0]), (0, 200, 200), 1)
                    if (extremos[2] - extremos[1]) > 0:
                        medida_calibrado_horizontal = float(txt_valor_muestraH.get())
                        pxXmmH = medida_calibrado_horizontal / (extremos[2] - extremos[1])
                        txt_pixelmmH.delete(0, END)
                        txt_pixelmmH.insert(0, pxXmmH)

                    vtnPrincipal.update()

                    # endregion

                elif accion == 3:
                    """ Medición individual Vertical y Horizontal"""

                    # Vertical
                    diferencia_v = calibracion - sup
                    medida_v = diferencia_v * pxXmmV

                    # Horizontal

                    extremos = extremos_patron(flaco)
                    cv2.rectangle(flaco, (extremos[1], sup), (extremos[2], extremos[0]), (0, 200, 200), 1)
                    diferencia_h = extremos[2] - extremos[1]
                    medida_h = diferencia_h * pxXmmH

                    txt_medidaV.delete(0, END)
                    txt_medidaV.insert(0, medida_v)
                    txt_medidaH.delete(0, END)
                    txt_medidaH.insert(0, medida_h)
                    vtnPrincipal.update()

                elif accion == 4:

                    """ Medicion de un perfil completo"""

                    # region Medicion Vertical
                    if len(medidas) == 0:
                        for c in range(largo):
                            for f in range((alto - 1), sup, -1):
                                if flaco[f, c] == 0:
                                    med = (calibracion - f) * pxXmmV
                                    valor = c, " = ", "%.3f" % med
                                    medidas.append(valor)
                                    break

                        for i in medidas:
                            print i

                    vtnPrincipal.update()
                    # endregion

                # endregion

                cv2.line(flaco, (0, calibracion), (largo, calibracion), (0, 200, 200), 1)
                cv2.imshow('Flaco', flaco)
            frames += 1
            time.sleep(1)



def superior(imagen):
    """
    Retorna el valor de la primera fila que contiene un pixel 0
        Parametros:
            1- Imagen: La imagen a analizar
    """
    retorno = 0
    alto, largo = imagen.shape[:2]
    for f in range(alto):
        if cv2.countNonZero(imagen[f, :]) != largo:
            retorno = f
            break
    return retorno


def extremos_patron(imagen):
    """
    Retorna los valores que delimitan al objeto sobre la plataforma
        Parametros:
            1- Imagen: La imagen a analizar
    """

    # datos[inferior, izquierdo, derecho]
    datos = [0, 0, 0]

    sup = superior(imagen)

    alto, largo = imagen.shape[:2]

    for f in range(sup, alto, 1):
        if cv2.countNonZero(imagen[f, :]) == 640:
            datos[0] = f - 1
            break

    imagen = imagen[sup:datos[0], 0:largo]
    alto, largo = imagen.shape[:2]

    for c in range(largo):
        if cv2.countNonZero(imagen[:, c]) < alto:
            datos[1] = c
            break

    for c in range(largo - 1, -1, -1):
        if cv2.countNonZero(imagen[:, c]) < alto:
            datos[2] = c
            break
    return datos


def validador_datos():
    error = 0
    mensaje = ""
    # ID Invadido
    try:
        int(txt_id_dispositivo.get())
    except (ValueError, TypeError):
        error = 1
        mensaje = "Valor de ID de Dispositivo Incorrecto "

    # Umbral Invalido
    try:
        if (int(txt_umbral.get()) < 0) or (int(txt_umbral.get()) > 255):
            error = 2
            mensaje = "0<=Umbral<=255 "
    except (ValueError, TypeError):
        error = 3
        mensaje = "Valor de Umbral Incorrecto "

    # Camara no detectada
    time.sleep(2)
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        error = 4
        mensaje = "No se detectó la Cámara "

    # Medida de Muestra
    try:
        float(txt_valor_muestraV.get())
    except (ValueError, TypeError):
        error = 5
        mensaje = "Valor de Calibración Incorrecto "

    if error != 0:
        tkMessageBox.showerror("Error", mensaje)
    return error


def calibrar_velocidad():
    global inf_velocidad
    while True:
        inf_velocidad = detector_lineas_velocidad()[1]
        if cv2.waitKey(33) & 0xFF == ord('q'):
            cv.waitKey(1)
            cv.destroyAllWindows()
            cv.waitKey(1)

def medir_velocidad():
    global inf_velocidad

    supant = detector_lineas_velocidad()[0]

    dif_pixeles = float(inf_velocidad - supant)
    print dif_pixeles

    supnue = detector_lineas_velocidad()[0]
    print supant, supnue
    while supant == supnue:
        supnue = detector_lineas_velocidad()[0]
        print supnue, inf_velocidad

    t_incial = datetime.now()
    print t_incial

    cv2.destroyWindow("Color")
    cv2.destroyWindow("subcolor")
    cv2.destroyWindow("Binario")

    while supnue < inf_velocidad:
        supnue = detector_lineas_velocidad()[0]
        print supnue, inf_velocidad

    cv2.destroyWindow("Color")
    cv2.destroyWindow("subcolor")
    cv2.destroyWindow("Binario")
    t_final = datetime.now()
    t_trancurrido = t_final - t_incial
    print "recorrio: ", dif_pixeles, "pixeles en ", t_trancurrido, "segundos"
    print "hacen: ", t_trancurrido / int(dif_pixeles), "segundos por pixel"
    px_mm = float(10 / dif_pixeles)
    print "1 px => ", px_mm, "mm"
    mm_px = 1 / px_mm
    print "1 mm => ", mm_px, "px"


def detector_lineas_velocidad():
    global camara
    if camara is None:
        camara = cv2.VideoCapture(int(txt_id_dispositivo.get()))

    ret, color = camara.read()
    # sub_color = color[190:290, 270:370]
    sub_color = color[30:290, 270:370]
    grises = cv2.cvtColor(sub_color, cv2.COLOR_BGR2GRAY)

    ret, binario = cv2.threshold(grises, 130, 255, cv2.THRESH_BINARY)

    cv2.rectangle(color, (270, 30), (370, 290), (0, 0, 0), 1)

    alto, largo = binario.shape[:2]
    supinf = [0, 0]
    for f in range(alto):
        if cv2.countNonZero(binario[f, :]) != largo:
            supinf[0] = f
            break

    for f in range(alto - 1, -1, -1):
        if cv2.countNonZero(binario[f, :]) != largo:
            supinf[1] = f
            break

    cv2.line(sub_color, (0, supinf[0]), (largo, supinf[0]), (0, 0, 0), 1)
    cv2.line(sub_color, (0, supinf[1]), (largo, supinf[1]), (0, 0, 0), 1)

    cv2.imshow('Color', color)
    cv2.imshow("subcolor", sub_color)
    cv2.imshow('Binario', binario)

    return supinf


def capturar_video():
    global camara
    if camara is None:
        camara = cv2.VideoCapture(int(txt_id_dispositivo.get()))

    nombre = txt_nombre_video.get() + '.avi'
    txttiempo = txt_tiempo.get()

    if len(txttiempo) == 0:
        tiempo = 1.0
    else:
        tiempo = float(txttiempo)

    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    out = cv2.VideoWriter(nombre, fourcc, 20.0, (640, 480))

    while True:
        time.sleep(tiempo)
        ret, color = camara.read()

        out.write(color)

        cv2.imshow('Color', color)
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break


def buscar_video():

    global video

    file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')

    if file:

        cap = cv.CaptureFromFile(file.name)

        video = cap

        nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
        fps = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
        print "total frame", nframes
        print "fps", fps
        print ' currpos of videofile', cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_POS_MSEC)

        txt_nombre_archivo.delete(0, END)
        txt_FPS.delete(0, END)
        txt_frames_archivo.delete(0, END)

        txt_nombre_archivo.insert(0, file.name)
        txt_FPS.insert(0, fps)
        txt_frames_archivo.insert(0, nframes)

        try:
            waitpermillisecond = int(1 * 1000 / fps)
            print "waitpermillisecond", waitpermillisecond
        except:
            pass
        print cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FOURCC)


def reproducir_video():
    """

    :rtype : aaa
    """
    global video
    nframes = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_COUNT))
    for f in xrange(nframes):
        frameimg = cv.QueryFrame(video)
        cv.ShowImage("hcq", frameimg)
        cv.WaitKey(1)


lblf_enlace_camara = LabelFrame(vtnPrincipal, text="1 - Enlace y calibración de Cámara")
lblf_patron = LabelFrame(vtnPrincipal, text="2 - Calibración con Patrón Eje Z y X")
lblf_Velocidad = LabelFrame(vtnPrincipal, text="3 - Calibración de Velocidad")
lblf_captura_frames = LabelFrame(vtnPrincipal, text="4 - Captua de Frames")


# region 1 - Enlace y calibración de Cámara
lbl_id_dispositivo = Label( lblf_enlace_camara, text="ID Dispositivo: ")
txt_id_dispositivo = Entry( lblf_enlace_camara, width=5)
lbl_umbral = Label(         lblf_enlace_camara, text="Umbral: ")
txt_umbral = Entry(         lblf_enlace_camara, width=5)
btn_acceder = Button(       lblf_enlace_camara, text="Enlazar y Calibrar",command=lambda: enlazar_camara(1))
lbl_conteo = Label(         lblf_enlace_camara, text="Conteo Px:")
txt_conteo = Entry(         lblf_enlace_camara, width=5)
lbl_superior = Label(       lblf_enlace_camara, text="Fila:")
txt_superior = Entry(       lblf_enlace_camara, width=5)

txt_id_dispositivo.insert(0, 0)
txt_umbral.insert(0, 254)
txt_conteo.insert(0, 0)
txt_superior.insert(0, 0)

lblf_enlace_camara.grid(row=0, column=0, sticky="we")

lbl_id_dispositivo.grid(row=0, column=0, sticky="e")
txt_id_dispositivo.grid(row=0, column=1, sticky="w")
lbl_umbral.grid(        row=1, column=0, sticky="e")
txt_umbral.grid(        row=1, column=1, sticky="w")
btn_acceder.grid(       row=2, column=0, columnspan=2)
lbl_conteo.grid(        row=3, column=0, sticky="e")
txt_conteo.grid(        row=3, column=1, sticky="w")
lbl_superior.grid(      row=4, column=0, sticky="e")
txt_superior.grid(      row=4, column=1, sticky="w")

# endregion

# region 2 - Calibración con Patrón Eje Z y X
lbl_valor = Label(              lblf_patron, text="Valor")
lbl_PixelMM = Label(            lblf_patron, text="Px-MM")
lbl_valor_muestraV = Label(     lblf_patron, text="Z:")
txt_valor_muestraV = Entry(     lblf_patron, width=5)
lbl_valor_muestraH = Label(     lblf_patron, text="X:")
txt_valor_muestraH = Entry(     lblf_patron, width=5)
txt_pixelmmV = Entry(           lblf_patron, width=5)
txt_pixelmmH = Entry(           lblf_patron, width=5)
btn_calibrar_patron = Button(   lblf_patron, text="C", command=lambda: enlazar_camara(2))

txt_valor_muestraV.insert(  0, 10)
txt_valor_muestraH.insert(  0, 12)
txt_pixelmmV.insert(        0, 0)
txt_pixelmmH.insert(        0, 0)

lblf_patron.grid(           row=6, column=0, sticky="we")
lbl_valor.grid(             row=6, column=1)
lbl_PixelMM.grid(           row=6, column=3)
lbl_valor_muestraV.grid(    row=7, column=0, sticky="e")
txt_valor_muestraV.grid(    row=7, column=1, sticky="w")
lbl_valor_muestraH.grid(    row=8, column=0, sticky="e")
txt_valor_muestraH.grid(    row=8, column=1, sticky="w")
txt_pixelmmV.grid(          row=7, column=3, sticky="w")
txt_pixelmmH.grid(          row=8, column=3, sticky="w")
btn_calibrar_patron.grid(   row=7, column=2, rowspan=2)
# endregion

# region 2 - Prueba Medición Total en Z y X

btn_medir = Button(     lblf_patron, text="Control", command=lambda: enlazar_camara(3))
lbl_medidaV = Label(    lblf_patron, text="Z:")
txt_medidaV = Entry(    lblf_patron, width=5)
lbl_mmV = Label(        lblf_patron, text="mm")
lbl_medidaH = Label(    lblf_patron, text="X:")
txt_medidaH = Entry(    lblf_patron, width=5)
lbl_mmH = Label(        lblf_patron, text="mm")

txt_medidaV.insert(0, 0)
txt_medidaH.insert(0, 0)

btn_medir.grid(         row=11, column=0, rowspan=2)
lbl_medidaV.grid(       row=11, column=1, sticky="e")
txt_medidaV.grid(       row=11, column=2, sticky="w")
lbl_mmV.grid(           row=11, column=3, sticky="w")
lbl_medidaH.grid(       row=12, column=1, sticky="e")
txt_medidaH.grid(       row=12, column=2, sticky="w")
lbl_mmH.grid(           row=12, column=3)

# endregion

# region 3 - Calibración de Velocidad
btn_calibrar_velocidad = Button(    lblf_Velocidad, text="Calibrar Velocidad", command=calibrar_velocidad)
btn_medir_velocidad = Button(       lblf_Velocidad, text="Medir Velocidad", command=medir_velocidad)


lblf_Velocidad.grid(            row=13, column=0, sticky="we")
btn_calibrar_velocidad.grid(    row=22, column=0, columnspan=2)
btn_medir_velocidad.grid(       row=23, column=0, columnspan=2)


# endregion

# region 4 - Captua de Frames
lbl_tiempo = Label(                 lblf_captura_frames, text="Tiempo espera:")
txt_tiempo = Entry(                 lblf_captura_frames, width=5)
lbl_nombre_video = Label(           lblf_captura_frames, text="Nombre Video:")
txt_nombre_video = Entry(           lblf_captura_frames)
btn_capturar = Button(              lblf_captura_frames, text="Capturar Video", command=capturar_video)
btn_buscar_archivo = Button(        lblf_captura_frames, text='Buscar Video', command=buscar_video)
lbl_nombre_archivo = Label(         lblf_captura_frames, text="Nombre:")
txt_nombre_archivo = Entry(         lblf_captura_frames)
lbl_FPS = Label(                    lblf_captura_frames, text="FPS:")
txt_FPS = Entry(                    lblf_captura_frames, width=5)
lbl_frames_archivo = Label(         lblf_captura_frames, text="Frames:")
txt_frames_archivo = Entry(         lblf_captura_frames, width=5)
btn_reproducir = Button(            lblf_captura_frames, text='Reproducir Video', command=reproducir_video)

txt_tiempo.insert(          0, "")
txt_nombre_video.insert(    0, "")
txt_nombre_archivo.insert(  0, "")
txt_frames_archivo.insert(  0, "")
txt_FPS.insert(             0, "")

lblf_captura_frames.grid(       row=24, column=0, sticky="we")
lbl_tiempo.grid(                row=24, column=0, sticky="e")
txt_tiempo.grid(                row=24, column=1, sticky="w")
lbl_nombre_video.grid(          row=25, column=0, sticky="e")
txt_nombre_video.grid(          row=25, column=1, sticky="w")
btn_capturar.grid(              row=26, column=0, columnspan=2)
btn_buscar_archivo.grid(        row=27, column=0, columnspan=2)
lbl_nombre_archivo.grid(        row=28, column=0, sticky="e")
txt_nombre_archivo.grid(        row=28, column=1, sticky="w")
lbl_FPS.grid(                   row=29, column=0, sticky="e")
txt_FPS.grid(                   row=29, column=1, sticky="w")
lbl_frames_archivo.grid(        row=30, column=0, sticky="e")
txt_frames_archivo.grid(        row=30, column=1, sticky="w")
btn_reproducir.grid(            row=31, column=0, columnspan=2)

# endregion
vtnPrincipal.mainloop()
