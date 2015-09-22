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
calibracion_base = 0
px_mm_z = 0.0
px_mm_x = 0.0
id_dispositivo = 0
medidas = []
camara = None
umbral = 254
velocidad = 0.0
video = None
extremo_izquierdo = 0
extremo_derecho = 0


def calibrar_camara_laser():
    '''Calibración de cámara y detección de Láser'''
    global id_dispositivo
    global calibracion_base
    global medidas
    global camara
    global umbral
    # Validacion de Datos
    if validador_datos() == 0:
        id_dispositivo = int(txt_id_dispositivo.get())
        camara = cv2.VideoCapture(id_dispositivo)
        umbral = int(txt_umbral.get())
        frames = 0
        while frames < 50:
            # Lectura de la señal de video
            ret, frame = camara.read()
            flaco = esqueletizador(frame, True)
            if len(flaco) > 0:
                cv2.imshow('Esqueleto', flaco)
            else:
                tkMessageBox.showerror("Error", "Verifique linea láser")
            frames += 1
        camara.release()


def calibrar_patron():
    '''Calibración Vertical y Horizontal del patron'''
    global id_dispositivo
    global px_mm_z
    global px_mm_x
    global calibracion_base
    global medidas
    global camara
    # Validacion de Datos
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        frames = 0
        while frames < 50:
            # Lectura de la señal de video
            ret, frame = camara.read()
            flaco = esqueletizador(frame, False)
            if len(flaco) > 0:
                # region Calibración Z
                sup = detectar_extremos(flaco, "n")[0]
                medida_calibrado = float(txt_valor_muestraV.get())
                if (calibracion_base - sup) > 0:
                    px_mm_z = medida_calibrado / (calibracion_base - sup)
                    txt_pixelmmV.delete(0, END)
                    txt_pixelmmV.insert(0, px_mm_z)

                # endregion

                # region Calibracion X
                extremos = detectar_roi_patron_calibracion(flaco)
                cv2.rectangle(flaco, (extremos[3], extremos[0]), (extremos[2], extremos[1]), (0, 200, 200), 1)
                if (extremos[2] - extremos[3]) > 0:
                    medida_calibrado_horizontal = float(txt_valor_muestraH.get())
                    px_mm_x = medida_calibrado_horizontal / (extremos[2] - extremos[3])
                    txt_pixelmmH.delete(0, END)
                    txt_pixelmmH.insert(0, px_mm_x)

                vtnPrincipal.update()
                cv2.imshow('Esqueleto', flaco)
                # endregion
            else:
                tkMessageBox.showerror("Error", "Verifique linea láser")
            frames += 1
        camara.release()


def control_calibrar_patron():
    ''' Medición de prueba en Vertical y Horizontal'''
    global id_dispositivo
    global px_mm_z
    global px_mm_x
    global calibracion_base
    global medidas
    global camara
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        frames = 0
        while frames < 50:
            ret, frame = camara.read()
            flaco = esqueletizador(frame, False)
            if len(flaco) > 0:


                # region Medicion en Z
                sup = detectar_extremos(flaco, "n")[0]
                diferencia_v = calibracion_base - sup
                medida_v = diferencia_v * px_mm_z
                # endregion

                # region Medicion en X
                extremos = detectar_roi_patron_calibracion(flaco)
                cv2.rectangle(flaco, (extremos[3], extremos[0]), (extremos[2], extremos[1]), (0, 200, 200), 1)
                diferencia_h = extremos[2] - extremos[3]
                medida_h = diferencia_h * px_mm_x
                # endregion

                txt_medidaV.delete(0, END)
                txt_medidaV.insert(0, medida_v)
                txt_medidaH.delete(0, END)
                txt_medidaH.insert(0, medida_h)
                vtnPrincipal.update()
                cv2.imshow('Esqueleto', flaco)
            else:
                tkMessageBox.showerror("Error", "Verifique linea láser")
            frames += 1
        camara.release()


def calibrar_extremos():

    global extremo_derecho
    global extremo_izquierdo

    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        frames = 0
        while frames < 50:
            ret, frame = camara.read()
            flaco = esqueletizador(frame, False)
            if len(flaco) > 0:
                alto, largo = flaco.shape[:2]
                extremos = detectar_extremos(flaco, "eo")
                print extremos
                extremo_izquierdo = extremos[2]
                extremo_derecho = extremos[3]

                cv2.line(flaco, (extremo_izquierdo, 0), (extremo_izquierdo, alto), (0, 0, 0), 1)
                cv2.line(flaco, (extremo_derecho, 0), (extremo_derecho, alto), (0, 0, 0), 1)

                txt_izquierdo.delete(0, END)
                txt_izquierdo.insert(0, extremo_izquierdo)
                txt_derecho.delete(0, END)
                txt_derecho.insert(0, extremo_derecho)
                vtnPrincipal.update()
                cv2.imshow('Esqueleto', flaco)
            else:
                tkMessageBox.showerror("Error", "Verifique linea láser")
            frames += 1
        camara.release()

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
        txt_conteo.delete(0, END)
        txt_conteo.insert(0, cantidad_bits_contados)
        vtnPrincipal.update()
        calibracion_base = sup
        txt_superior.delete(0, END)
        txt_superior.insert(0, sup)

    cv2.imshow('Color', imagen_color)
    cv2.waitKey(1)
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


def detectar_roi_patron_calibracion(imagen):
    """
    Detecta la ROI para el patrón de calibración
    :param imagen: La imagen original
    :return: [Norte, Sur, Este, Oeste]
    """
    alto, largo = imagen.shape[:2]
    n = detectar_extremos(imagen, "n")[0]
    for f in range(n, alto, 1):
        if cv2.countNonZero(imagen[f, :]) == largo:
            s = f - 1
            break
    s_imagen = imagen[n:s, 0:largo]
    eo = detectar_extremos(s_imagen, "eo")
    roi = [n, s, eo[2], eo[3]]
    return roi


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
    """

    :return:
    """
    global inf_velocidad
    global camara
    global id_dispositivo
    frames = 0
    # while frames < 150:
    id_dispositivo = int(txt_id_dispositivo.get())
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)

        while True:
            ret, frame = camara.read()
            inf_velocidad = detector_lineas_velocidad(frame)[1]
            frames += 1
            cv2.waitKey(1)
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break

        cv2.destroyWindow("Color")
        cv2.destroyWindow("subcolor")
        cv2.destroyWindow("Binario")
        camara.release()


def medir_velocidad():
    """
    Mide el tiempo que transcurre desde que la línea superior está en reposo hasta que pasa por la posición de la
    linea inferior
    :return:-
    """
    global inf_velocidad
    global velocidad
    global camara
    patron = 0.0
    id_dispositivo = int(txt_id_dispositivo.get())
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        if len(txt_medida_patron_velocidad.get()) == 0:
            # por defecto, 10mm
            patron = 10
        else:
            patron = float(txt_medida_patron_velocidad.get())

        ret, frame = camara.read()
        supant = detector_lineas_velocidad(frame)[0]
        dif_pixeles = float(inf_velocidad - supant)
        supnue = detector_lineas_velocidad(frame)[0]
        while supant == supnue:
            ret, frame = camara.read()
            supnue = detector_lineas_velocidad(frame)[0]

        t_incial = datetime.now()
        while supnue < inf_velocidad:
            ret, frame = camara.read()
            supnue = detector_lineas_velocidad(frame)[0]
            cv2.waitKey(1)

        cv2.destroyWindow("Color")
        cv2.destroyWindow("subcolor")
        cv2.destroyWindow("Binario")

        t_final = datetime.now()
        t_trancurrido = (t_final - t_incial).total_seconds()
        print t_trancurrido
        velocidad = patron / t_trancurrido
        tiempo_espera = t_trancurrido / 10

        txt_velocidad.delete(0, END)
        txt_velocidad.insert(0, str('{0:.3g}'.format(velocidad)) + " mm/seg")
        txt_tiempo_espera.delete(0, END)
        txt_tiempo_espera.insert(0, str(tiempo_espera) + " seg")
        txt_tiempo.delete(0, END)
        txt_tiempo.insert(0,tiempo_espera)

        camara.release()


def detector_lineas_velocidad(color):
    """
    Identifica las filas de 2 líneas usadas como patrón de calibración de velocidad.
    :return: [Fila Superior, Fila Inferior)
    """
    #global camara
    #global id_dispositivo
    #if camara is None:
    #    camara = cv2.VideoCapture(int(txt_id_dispositivo.get()))
    #ret, color = camara.read()
    supinf = [0, 0]
    cv2.imshow('Color', color)
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
    cv2.line(sub_color, (0, supinf[1]), (largo, supinf[1]), (255, 0, 0), 1)
    cv2.imshow('Color', color)
    # cv2.imshow("subcolor", sub_color)
    cv2.imshow('Binario', binario)
    return supinf


def capturar_video():
    """
    Crea un video capturando los frames interesantes, tomando como referencia la velocidad medida en el etapa anterior
    :return:
    """
    global camara
    global id_dispositivo
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        if camara is None:
            camara = cv2.VideoCapture(id_dispositivo)
        if len(txt_nombre_video.get()) == 0:
            nombre = "prueba.avi"
        else:
            nombre = txt_nombre_video.get() + '.avi'

        if len(txt_tiempo.get()) == 0:
            tiempo = 1.0
        else:
            tiempo = float(txt_tiempo.get())
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter(nombre, fourcc, 20.0, (640, 480))
        while True:
            time.sleep(tiempo)
            ret, color = camara.read()
            out.write(color)
            cv2.imshow('Color', color)
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
        camara.release()


def buscar_video():
    """

    :return:
    """
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
    Se requiere:
        La calibración de la linea base
        La calibración del patron en X y Z
        la calibración de velocidad
    :return: Matriz de alturas
    """


    if validar_datos_generar_3d():
        print "generador de 3D"


def validar_datos_generar_3d():

    global px_mm_x
    global px_mm_z
    global calibracion_base
    global video
    global velocidad

    resultado = True
    mensaje=""

    print px_mm_z
    print px_mm_x
    print calibracion_base
    print video
    print velocidad

    if velocidad == 0:
        mensaje = "No se conoce la velocidad de calibración"
        resultado=False
    if px_mm_x == 0:
        mensaje = "No se conoce el patron en X"
        resultado=False
    if px_mm_z == 0:
        mensaje = "No se conoce el patron en Z"
        resultado=False
    if calibracion_base == 0:
        mensaje = "No se conoce la linea base"
        resultado=False
    if video is None:
        mensaje = "No se cargó el video"
        resultado=False

    if not resultado:
        tkMessageBox.showerror("Error", mensaje)

    return resultado


def medicion_perfil():
    """
        se medirá 1 perfil completo
    :return: vector de medidas
    """
    global video
    """
                elif accion == 4:

                    # region Medicion Vertical
                    if len(medidas) == 0:
                        for c in range(largo):
                            for f in range((alto - 1), sup, -1):
                                if flaco[f, c] == 0:
                                    med = (calibracion_base - f) * px_mm_z
                                    valor = c, " = ", "%.3f" % med
                                    medidas.append(valor)
                                    break

                        for i in medidas:
                            print i

                    vtnPrincipal.update()
                    # endregion

                # endregion

                #cv2.line(flaco, (0, calibracion_base), (largo, calibracion_base), (0, 200, 200), 1)
                #cv2.imshow('Flaco', flaco)
            frames += 1
            # time.sleep(1)
            camara.release()
    """

lblf_enlace_camara = LabelFrame(vtnPrincipal, text="1 - Enlace y calibración de Cámara")
lblf_patron = LabelFrame(vtnPrincipal, text="2 - Calibración con Patrón Eje Z y X")
lblf_Velocidad = LabelFrame(vtnPrincipal, text="3 - Calibración de Velocidad")
lblf_captura_frames = LabelFrame(vtnPrincipal, text="4 - Captura de Video")
lblf_generacion3D = LabelFrame(vtnPrincipal, text="5 - Medición y Generación 3D")


# region 1 - Enlace y calibración de Cámara
lbl_id_dispositivo = Label( lblf_enlace_camara, text="ID Dispositivo: ")
txt_id_dispositivo = Entry( lblf_enlace_camara, width=5)
lbl_umbral = Label(         lblf_enlace_camara, text="Umbral: ")
txt_umbral = Entry(         lblf_enlace_camara, width=5)
btn_acceder = Button(       lblf_enlace_camara, text="Enlazar y Calibrar", command=calibrar_camara_laser)
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
txt_valor_muestraV = Entry(     lblf_patron, width=7)
lbl_valor_muestraH = Label(     lblf_patron, text="X:")
txt_valor_muestraH = Entry(     lblf_patron, width=7)
txt_pixelmmV = Entry(           lblf_patron, width=7)
txt_pixelmmH = Entry(           lblf_patron, width=7)
btn_calibrar_patron = Button(   lblf_patron, text="C", command=calibrar_patron)


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

btn_medir = Button(     lblf_patron, text="Control", command=control_calibrar_patron)
lbl_medidaV = Label(    lblf_patron, text="Z:")
txt_medidaV = Entry(    lblf_patron, width=5)
lbl_mmV = Label(        lblf_patron, text="mm")
lbl_medidaH = Label(    lblf_patron, text="X:")
txt_medidaH = Entry(    lblf_patron, width=5)
lbl_mmH = Label(        lblf_patron, text="mm")

txt_medidaV.insert(0, 0)
txt_medidaH.insert(0, 0)

btn_medir.grid(         row=9, column=0, rowspan=2)
lbl_medidaV.grid(       row=9, column=1, sticky="e")
txt_medidaV.grid(       row=9, column=2, sticky="w")
lbl_mmV.grid(           row=9, column=3, sticky="w")
lbl_medidaH.grid(       row=10, column=1, sticky="e")
txt_medidaH.grid(       row=10, column=2, sticky="w")
lbl_mmH.grid(           row=10, column=3)

# endregion

# region 2 - Calibracion de extremos Izquierdo y Derecho
btn_calibrar_extremos = Button( lblf_patron, text="Expremos", command=calibrar_extremos)
lbl_izquierdo= Label(           lblf_patron, text="Izquierdo:")
txt_izquierdo= Entry(           lblf_patron, width=7)
lbl_derecho= Label(             lblf_patron, text="Derecho:")
txt_derecho= Entry(             lblf_patron, width=7)

btn_calibrar_extremos.grid( row=11, column=0, sticky="w")
lbl_izquierdo.grid(         row=12, column=1, sticky="w")
txt_izquierdo.grid(         row=12, column=2, sticky="w")
lbl_derecho.grid(           row=13, column=1, sticky="w")
txt_derecho.grid(           row=13, column=2, sticky="w")
# endregion

# region 3 - Calibración de Velocidad
btn_calibrar_velocidad = Button(    lblf_Velocidad, text="Calibrar Patron Velocidad", command=calibrar_velocidad)
lbl_patron = Label(                 lblf_Velocidad, text="Medida Patron:")
txt_medida_patron_velocidad=Entry(  lblf_Velocidad, width=5)
btn_medir_velocidad = Button(       lblf_Velocidad, text="Medir Velocidad", command=medir_velocidad)
lbl_velocidad = Label(              lblf_Velocidad, text="velocidad:")
txt_velocidad = Entry(              lblf_Velocidad, width=10)
lbl_tiempo_espera = Label(          lblf_Velocidad, text="t. espera c/mm:")
txt_tiempo_espera = Entry(          lblf_Velocidad, width=10)

txt_medida_patron_velocidad.insert(0,10)

lblf_Velocidad.grid(                row=13, column=0, sticky="we")
btn_calibrar_velocidad.grid(        row=22, column=0, columnspan=2)
lbl_patron.grid(                    row=23, column=0, sticky="e")
txt_medida_patron_velocidad.grid(   row=23, column=1, sticky="w")
btn_medir_velocidad.grid(           row=24, column=0, columnspan=2)
lbl_velocidad.grid(                 row=25, column=0, sticky="e")
txt_velocidad.grid(                 row=25, column=1)
lbl_tiempo_espera.grid(             row=26, column=0, sticky="e")
txt_tiempo_espera.grid(             row=26, column=1)

# endregion

# region 4 - Captua de Frames
lbl_tiempo = Label(                 lblf_captura_frames, text="Tiempo espera:")
txt_tiempo = Entry(                 lblf_captura_frames, width=10)
lbl_nombre_video = Label(           lblf_captura_frames, text="Nombre Video:")
txt_nombre_video = Entry(           lblf_captura_frames)
btn_capturar = Button(              lblf_captura_frames, text="Capturar Video", command=capturar_video)

txt_tiempo.insert(          0, "")
txt_nombre_video.insert(    0, "")


lblf_captura_frames.grid(       row=24, column=0, sticky="we")
lbl_tiempo.grid(                row=24, column=0, sticky="e")
txt_tiempo.grid(                row=24, column=1, sticky="w")
lbl_nombre_video.grid(          row=25, column=0, sticky="e")
txt_nombre_video.grid(          row=25, column=1, sticky="w")
btn_capturar.grid(              row=26, column=0, columnspan=2)

# endregion

# region 5 - Medición y Generación 3D
lbl_tiempo1 = Label(                lblf_generacion3D, text="Tiempo espera:")
txt_tiempo1 = Entry(                lblf_generacion3D, width=10)
btn_buscar_archivo = Button(        lblf_generacion3D, text='Buscar Video', command=buscar_video)
lbl_nombre_archivo = Label(         lblf_generacion3D, text="Nombre:")
txt_nombre_archivo = Entry(         lblf_generacion3D)
lbl_FPS = Label(                    lblf_generacion3D, text="FPS:")
txt_FPS = Entry(                    lblf_generacion3D, width=5)
lbl_frames_archivo = Label(         lblf_generacion3D, text="Frames:")
txt_frames_archivo = Entry(         lblf_generacion3D, width=5)
btn_reproducir = Button(            lblf_generacion3D, text='Reproducir Video', command=reproducir_video)
btn_generar3D = Button(             lblf_generacion3D, text="Generar 3D", command=generar_3d)

txt_nombre_archivo.insert(  0, "")
txt_frames_archivo.insert(  0, "")
txt_FPS.insert(             0, "")

lblf_generacion3D.grid(         row=27, column=0, sticky="we")
btn_buscar_archivo.grid(        row=28, column=0, columnspan=2)
lbl_nombre_archivo.grid(        row=29, column=0, sticky="e")
txt_nombre_archivo.grid(        row=29, column=1, sticky="w")
lbl_FPS.grid(                   row=30, column=0, sticky="e")
txt_FPS.grid(                   row=30, column=1, sticky="w")
lbl_frames_archivo.grid(        row=31, column=0, sticky="e")
txt_frames_archivo.grid(        row=31, column=1, sticky="w")
btn_reproducir.grid(            row=32, column=0, columnspan=2)
lbl_tiempo1.grid(               row=33, column=0, sticky="e")
txt_tiempo1.grid(               row=33, column=1, sticky="w")
btn_generar3D.grid(             row=34, column=0, columnspan=2)


# endregion
vtnPrincipal.mainloop()
