# coding=utf-8
from ttk import Notebook

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
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

vtnPrincipal = Tk()
calibracion_base = 0
px_mm_z = 0.0
px_mm_x = 0.0
px_mm_y = 0.0
id_dispositivo = 0
medidas = []
camara = None
umbral = 245
velocidad = 0.0
video = None
extremo_izquierdo = 0
extremo_derecho = 0
nombre_video = ""


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
        while frames < 200:
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
                #print extremos
                extremo_izquierdo = extremos[3]
                extremo_derecho = extremos[2]

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
        frames = 0
        while frames < 200:
            ret, frame = camara.read()
            inf_velocidad = detector_lineas_velocidad(frame)[1]
            frames += 1
            cv2.waitKey(1)
            #if cv2.waitKey(33) & 0xFF == ord('q'):
             #   break
            frames += 1
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
        #print t_trancurrido
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
    sub_color = color[350:450, 270:370]
    grises = cv2.cvtColor(sub_color, cv2.COLOR_BGR2GRAY)
    ret, binario = cv2.threshold(grises, 160, 255, cv2.THRESH_BINARY)
    cv2.rectangle(color, (270, 350), (370, 450), (0, 0, 0), 1)
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
    global nombre_video
    file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
    if file:
        video = cv2.VideoCapture(file.name)

        nombre_video = file.name
        txt_video.insert(0, file.name)
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

    if validar_datos_generar_3d():
        #print video, px_mm_x, px_mm_y, px_mm_z, extremo_izquierdo, extremo_derecho, calibracion_base
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
    #print superior, calibracion_base
    alto, largo = imagen.shape[:2]
    for c in range(extremo_izquierdo, extremo_derecho + 1, 1):
        for f in range(superior, calibracion_base, 1):
            if imagen[f, c] == 0:
                altura_mm = round(((calibracion_base - f) * px_mm_z), 2)
                medidas[c - extremo_izquierdo] = altura_mm
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
    global nombre_video

    alto, largo = Z.shape[:2]
    X = np.zeros(largo)
    Y = np.zeros(alto)

    for c in range(len(X)):
        X[c] = px_mm_x * c

    for c in range(len(Y)):
        Y[c] = px_mm_y * c

    #print "X ", len(X), X
    #print "Y", len(Y), Y
    #print "Z", Z.shape


    archivo_medidas = nombre_video+"-medidas.txt"
    np.savetxt(archivo_medidas, Z, fmt='%1.2f', delimiter=';')

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


def guardar_configuracion():
    """
    Se guardan los datos de configuración del escaneo
    :return:
    """
    global px_mm_x, px_mm_y, px_mm_z
    global calibracion_base
    global extremo_izquierdo, extremo_derecho
    datos = [px_mm_x, px_mm_y, px_mm_z, calibracion_base, extremo_izquierdo, extremo_derecho]


contenedor_pestanas = Notebook(vtnPrincipal)
pestana_calibracion_camara = Frame(contenedor_pestanas)
pestana_calibracion_velocidad = Frame(contenedor_pestanas)
pestana_captura_video = Frame(contenedor_pestanas)
pestana_generacion_3d = Frame(contenedor_pestanas)

contenedor_pestanas.add(pestana_calibracion_camara, text="Cámara")
contenedor_pestanas.add(pestana_calibracion_velocidad, text="Velocidad")
contenedor_pestanas.add(pestana_captura_video, text="Video")
contenedor_pestanas.add(pestana_generacion_3d, text="3D")

contenedor_pestanas.pack()

# region Enlace y calibración de Cámara

btn_ver_camara = Button(pestana_calibracion_camara, text="Ver Camara")
btn_ver_camara.grid(row=1, column=0, columnspan=2 )

lblf_enlace_camara = LabelFrame(pestana_calibracion_camara, text="1 - Calibración de Cámara")
lblf_patron = LabelFrame(pestana_calibracion_camara, text="2 - Calibración Eje Z y X")
lblf_extremos = LabelFrame(pestana_calibracion_camara, text="3 - Calibración de Extremos")

lbl_id_dispositivo = Label( lblf_enlace_camara, text="ID Dispositivo: ")
txt_id_dispositivo = Entry( lblf_enlace_camara, width=5)
lbl_umbral = Label(         lblf_enlace_camara, text="Umbral: ")
txt_umbral = Entry(         lblf_enlace_camara, width=5)
btn_acceder = Button(       lblf_enlace_camara, text="Calibrar", command=calibrar_camara_laser)
lbl_conteo = Label(         lblf_enlace_camara, text="Conteo Px:")
txt_conteo = Entry(         lblf_enlace_camara, width=5)
lbl_superior = Label(       lblf_enlace_camara, text="Fila:")
txt_superior = Entry(       lblf_enlace_camara, width=5)

txt_id_dispositivo.insert(0, 0)
txt_umbral.insert(0, 254)
txt_conteo.insert(0, 0)
txt_superior.insert(0, 0)

lblf_enlace_camara.grid(    row=0, column=0)

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

# region Calibración con Patrón Eje Z y X
#lbl_valor = Label(              lblf_patron, text="Valor")
#lbl_PixelMM = Label(            lblf_patron, text="Px-MM")
lbl_valor_muestraV = Label(     lblf_patron, text="Z:")
txt_valor_muestraV = Entry(     lblf_patron, width=7)
lbl_valor_muestraH = Label(     lblf_patron, text="X:")
txt_valor_muestraH = Entry(     lblf_patron, width=7)
txt_pixelmmV = Entry(           lblf_patron, width=7)
txt_pixelmmH = Entry(           lblf_patron, width=7)
btn_calibrar_patron = Button(   lblf_patron, text="Calibrar", command=calibrar_patron)


txt_valor_muestraV.insert(  0, 10)
txt_valor_muestraH.insert(  0, 12)
txt_pixelmmV.insert(        0, 0)
txt_pixelmmH.insert(        0, 0)

lblf_patron.grid(           row=0, column=1, sticky="n")
#lbl_valor.grid(             row=0, column=1)
#lbl_PixelMM.grid(           row=0, column=3)
lbl_valor_muestraV.grid(    row=1, column=0, sticky="e")
txt_valor_muestraV.grid(    row=1, column=1, sticky="w")
lbl_valor_muestraH.grid(    row=2, column=0, sticky="e")
txt_valor_muestraH.grid(    row=2, column=1, sticky="w")
txt_pixelmmV.grid(          row=1, column=3, sticky="w")
txt_pixelmmH.grid(          row=2, column=3, sticky="w")
btn_calibrar_patron.grid(   row=1, column=2, rowspan=2)

# endregion

# region Calibracion de extremos Izquierdo y Derecho

btn_calibrar_extremos = Button( lblf_extremos, text="Calibrar", command=calibrar_extremos)
lbl_izquierdo= Label(           lblf_extremos, text="Izquierdo:")
txt_izquierdo= Entry(           lblf_extremos, width=7)
lbl_derecho= Label(             lblf_extremos, text="Derecho:")
txt_derecho= Entry(             lblf_extremos, width=7)

lblf_extremos.grid(         row=0, column=1, sticky="sw")
btn_calibrar_extremos.grid( row=0, column=0, sticky="w", rowspan=2)
lbl_izquierdo.grid(         row=0, column=1, sticky="w")
txt_izquierdo.grid(         row=0, column=2, sticky="w")
lbl_derecho.grid(           row=1, column=1, sticky="w")
txt_derecho.grid(           row=1, column=2, sticky="w")
# endregion

#region Calibracion de Velocidad

lblf_calibrar_patron_velocidad =    LabelFrame(pestana_calibracion_velocidad, text="1- Calibración de Patrón")
btn_calibrar_velocidad = Button(    lblf_calibrar_patron_velocidad, text="Calibrar Patron Velocidad", command=calibrar_velocidad)
lbl_patron = Label(                 lblf_calibrar_patron_velocidad, text="Medida Patron:")
txt_medida_patron_velocidad=Entry(  lblf_calibrar_patron_velocidad, width=5)

lblf_medir_velocidad =              LabelFrame(pestana_calibracion_velocidad, text="2- Medir Velocidad")
btn_medir_velocidad = Button(       lblf_medir_velocidad, text="Medir Velocidad", command=medir_velocidad)
lbl_velocidad = Label(              lblf_medir_velocidad, text="velocidad:")
txt_velocidad = Entry(              lblf_medir_velocidad, width=10)

lblf_calcular_tiempo_espera =       LabelFrame(pestana_calibracion_velocidad, text="3- Calcular Tiempo de Espera")
lbl_separacion_perfiles = Label(    lblf_calcular_tiempo_espera, text="Separación")
txt_separacion_perfiles = Entry(    lblf_calcular_tiempo_espera, width=5)
btn_calcular_tiempo_espera = Button(lblf_calcular_tiempo_espera, text="Calcular Tiempo Espera")
lbl_tiempo_espera = Label(          lblf_calcular_tiempo_espera, text="t. espera c/mm:")
txt_tiempo_espera = Entry(          lblf_calcular_tiempo_espera, width=10)

btn_guardar_configuracion = Button( pestana_calibracion_velocidad, text="Guardar Configuración", command=guardar_configuracion)

txt_medida_patron_velocidad.insert(0, 10)

lblf_calibrar_patron_velocidad.grid(    row=0, column=0, sticky="n")
btn_calibrar_velocidad.grid(            row=0, column=0, columnspan=2)
lbl_patron.grid(                        row=1, column=0, sticky="e")
txt_medida_patron_velocidad.grid(       row=1, column=1, sticky="w")

lblf_medir_velocidad.grid(              row=1, column=0, sticky="s")
btn_medir_velocidad.grid(               row=2, column=0, columnspan=2)
lbl_velocidad.grid(                     row=3, column=0, sticky="e")
txt_velocidad.grid(                     row=3, column=1)

lblf_calcular_tiempo_espera.grid(       row=0, column=1, sticky="nw")
lbl_separacion_perfiles.grid(           row=0, column=0)
txt_separacion_perfiles.grid(           row=0, column=1)
btn_calcular_tiempo_espera.grid(        row=1, column=0, columnspan=2)
lbl_tiempo_espera.grid(                 row=2, column=0, sticky="e")
txt_tiempo_espera.grid(                 row=2, column=1)

btn_guardar_configuracion.grid(         row=1, column=1)


#endregion+

# region Captua de Frames
lbl_tiempo = Label(                 pestana_captura_video, text="Tiempo espera:")
txt_tiempo = Entry(                 pestana_captura_video, width=10)
lbl_nombre_video = Label(           pestana_captura_video, text="Nombre Video:")
txt_nombre_video = Entry(           pestana_captura_video)
btn_capturar = Button(              pestana_captura_video, text="Capturar Video", command=capturar_video)

txt_tiempo.insert(          0, "")
txt_nombre_video.insert(    0, "")

lbl_tiempo.grid(                row=0, column=0, sticky="e")
txt_tiempo.grid(                row=0, column=1, sticky="w")
lbl_nombre_video.grid(          row=1, column=0, sticky="e")
txt_nombre_video.grid(          row=1, column=1, sticky="w")
btn_capturar.grid(              row=2, column=0)


# endregion

# region Medición y Generación 3D
lblf_buscar_configuracion = LabelFrame(pestana_generacion_3d, text="1 - Cargar Configuración")
btn_buscar_configuracion = Button(lblf_buscar_configuracion, text="Cargar Configuración")
lbl_x = Label(      lblf_buscar_configuracion, text="X")
lbl_z = Label(      lblf_buscar_configuracion, text="Z")
lbl_y = Label(      lblf_buscar_configuracion, text="Y")
lbl_iz = Label(     lblf_buscar_configuracion, text="Izquierdo")
lbl_der = Label(    lblf_buscar_configuracion, text="Derecho")
lbl_base = Label(   lblf_buscar_configuracion, text="Base")
txt_x = Entry(      lblf_buscar_configuracion, width=10)
txt_z = Entry(      lblf_buscar_configuracion, width=10)
txt_y = Entry(      lblf_buscar_configuracion, width=10)
txt_iz = Entry(     lblf_buscar_configuracion, width=10)
txt_der = Entry(    lblf_buscar_configuracion, width=10)
txt_base = Entry(   lblf_buscar_configuracion, width=10)


lblf_buscar_video = LabelFrame( pestana_generacion_3d, text="2 - Cargar Video")
btn_buscar_video = Button(    lblf_buscar_video, text='Cargar Video', command=buscar_video)
lbl_video = Label(              lblf_buscar_video, text="Video")
txt_video = Entry(              lblf_buscar_video, width=10)


btn_generar3D = Button(             pestana_generacion_3d, text="Generar 3D", command=generar_3d)

txt_x.insert(0, 0.1518)
txt_y.insert(0, 1)
txt_z.insert(0, 0.1960)
txt_iz.insert(0, 13)
txt_der.insert(0, 625)
txt_base.insert(0, 451)

lblf_buscar_configuracion.grid( row=0, column=0, sticky="n")
btn_buscar_configuracion.grid(  row=1, column=0, sticky="we", columnspan=4)
lbl_x.grid(                     row=2, column=0, sticky="we")
txt_x.grid(                     row=2, column=1, sticky="we")
lbl_z.grid(                     row=3, column=0, sticky="we")
txt_z.grid(                     row=3, column=1, sticky="we")
lbl_y.grid(                     row=4, column=0, sticky="we")
txt_y.grid(                     row=4, column=1, sticky="we")
lbl_iz.grid(                    row=2, column=2, sticky="we")
txt_iz.grid(                    row=2, column=3, sticky="we")
lbl_der.grid(                   row=3, column=2, sticky="we")
txt_der.grid(                   row=3, column=3, sticky="we")
lbl_base.grid(                  row=4, column=2, sticky="we")
txt_base.grid(                  row=4, column=3, sticky="we")

lblf_buscar_video.grid(         row=0, column=1, sticky="n")
btn_buscar_video.grid(        row=1, column=0, columnspan=2)
lbl_video.grid(                 row=2, column=0, sticky="we")
txt_video.grid(                 row=2, column=1, sticky="we")

btn_generar3D.grid(             row=0, column=1, sticky="s")


# endregion

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
btn_guardar_configuracion = Button( lblf_captura_frames, text="Guardar Configuración", command=guardar_configuracion)

txt_medida_patron_velocidad.insert(0, 10)

lblf_Velocidad.grid(                row=13, column=0, sticky="we")
btn_calibrar_velocidad.grid(        row=22, column=0, columnspan=2)
lbl_patron.grid(                    row=23, column=0, sticky="e")
txt_medida_patron_velocidad.grid(   row=23, column=1, sticky="w")
btn_medir_velocidad.grid(           row=24, column=0, columnspan=2)
lbl_velocidad.grid(                 row=25, column=0, sticky="e")
txt_velocidad.grid(                 row=25, column=1)
lbl_tiempo_espera.grid(             row=26, column=0, sticky="e")
txt_tiempo_espera.grid(             row=26, column=1)
btn_guardar_configuracion.grid(     row=27, column=0, columnspan=2)
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
btn_capturar.grid(              row=26, column=0)


# endregion

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

txt_x.insert(0, 0.1518)
txt_y.insert(0, 1)
txt_z.insert(0, 0.1960)
txt_iz.insert(0, 13)
txt_der.insert(0, 625)
txt_base.insert(0, 451)

lblf_generacion3D.grid(         row=30, column=0, sticky="we")
lbl_x.grid(                     row=30, column=0, sticky="we")
txt_x.grid(                     row=30, column=1, sticky="we")
lbl_z.grid(                     row=31, column=0, sticky="we")
txt_z.grid(                     row=31, column=1, sticky="we")
lbl_y.grid(                     row=32, column=0, sticky="we")
txt_y.grid(                     row=32, column=1, sticky="we")
lbl_iz.grid(                    row=33, column=0, sticky="we")
txt_iz.grid(                    row=33, column=1, sticky="we")
lbl_der.grid(                   row=34, column=0, sticky="we")
txt_der.grid(                   row=34, column=1, sticky="we")
lbl_base.grid(                  row=35, column=0, sticky="we")
txt_base.grid(                  row=35, column=1, sticky="we")
btn_buscar_archivo.grid(        row=36, column=0, columnspan=2)
lbl_video.grid(                 row=37, column=0, sticky="we")
txt_video.grid(                 row=37, column=1, sticky="we")
btn_generar3D.grid(             row=38, column=0, columnspan=2)


# endregion
"""
vtnPrincipal.mainloop()
