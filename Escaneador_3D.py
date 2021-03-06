# coding=utf-8
import os

__author__ = 'Alejandro'
from ttk import Notebook
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
from numpy import genfromtxt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

vtnPrincipal = Tk()

umbral = 245
calibracion_base = 0
px_mm_z = 0.0
px_mm_x = 0.0
px_mm_y = 0.0
id_dispositivo = 0
extremo_izquierdo = 0
extremo_derecho = 0

medidas = []
camara = None

velocidad = 0.0
video = ""
nombre_video = ""
tiempo_espera = 0.0
inf_velocidad = 0

matrizMedidas3D = None


def calibrar_camara_laser():
    """
    Calibración de cámara y detección de Láser
    :return:
    """
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
        btn_calibrar_patron.config(state=NORMAL)
        btn_calibrar_extremos.config(state=NORMAL)
        btn_calibrar_velocidad.config(state=NORMAL)


def calibrar_patron():
    """
    Calibración Vertical y Horizontal del patron
    :return:
    """
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
    """
    Medición de prueba en Vertical y Horizontal
    :return:
    """
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

                # txt_medidaV.delete(0, END)
                # txt_medidaV.insert(0, medida_v)
                # txt_medidaH.delete(0, END)
                # txt_medidaH.insert(0, medida_h)
                vtnPrincipal.update()
                cv2.imshow('Esqueleto', flaco)
            else:
                tkMessageBox.showerror("Error", "Verifique linea láser")
            frames += 1
        camara.release()


def calibrar_extremos():
    """
    Delimita la región a escanear en Horizontal al definir las columnas Izquierda y Derecha
    :return:
    """
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
                # print extremos
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
            if extremo_izquierdo != 0 and extremo_derecho != 0:
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
        Se realiza la calibración de las líneas de velocidad
    :return:
    """
    global inf_velocidad
    global camara
    global id_dispositivo

    id_dispositivo = int(txt_id_dispositivo.get())
    if not cv2.VideoCapture(id_dispositivo).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        frames = 0
        while frames < 200:
            ret, frame = camara.read()
            inf_velocidad = detector_lineas_velocidad(frame)[1]
            frames += 1
            cv2.waitKey(1)
            frames += 1
        cv2.destroyWindow("Color")
        cv2.destroyWindow("subcolor")
        cv2.destroyWindow("Binario")
        camara.release()
        btn_medir_velocidad.config(state=NORMAL)


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
    if not cv2.VideoCapture(id_dispositivo).read()[0]:
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
        # print t_trancurrido
        velocidad = patron / t_trancurrido
        # tiempo_espera = t_trancurrido / 10

        txt_velocidad.delete(0, END)
        txt_velocidad.insert(0, str('{0:.3g}'.format(velocidad)) + " mm/seg")
        # txt_tiempo_espera.delete(0, END)
        # txt_tiempo_espera.insert(0, str(tiempo_espera) + " seg")
        # txt_tiempo_espera.delete(0, END)
        # txt_tiempo_espera.insert(0,tiempo_espera)

    camara.release()
    btn_calcular_tiempo_espera.config(state=NORMAL)


def detector_lineas_velocidad(color):
    """
    Identifica las filas de 2 líneas usadas como patrón de calibración de velocidad.
    :return: [Fila Superior, Fila Inferior)
    """
    # global camara
    # global id_dispositivo
    # if camara is None:
    #    camara = cv2.VideoCapture(int(txt_id_dispositivo.get()))
    # ret, color = camara.read()
    # supinf = [0, 0]
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
    Crea un video capturando frames, tomando como referencia la velocidad medida en el etapa anterior
    :return:
    """
    global camara
    global id_dispositivo
    global tiempo_espera
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        if len(txt_nombre_video.get()) == 0:
            nombre = "prueba.avi"
        else:
            nombre = txt_nombre_video.get() + '.avi'

        if tiempo_espera == 0:
            tiempo_espera = 1.0
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter(nombre, fourcc, 20.0, (640, 480))
        while True:
            time.sleep(tiempo_espera)
            ret, color = camara.read()
            out.write(color)
            cv2.imshow('Color', color)
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
        camara.release()


def filtrar_video():
    cap = cv.CaptureFromFile(normal)
    separador = int(txt_separacion_perfiles.get())
    nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
    nombre = "filtrado.avi"
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    out = cv2.VideoWriter(nombre, fourcc, 20.0, (640, 480))
    for f in xrange(nframes):
        frameimg = cv.QueryFrame(cap)
        if f % separador == 0:
            tmp = cv.CreateImage(cv.GetSize(frameimg), 8, 3)
            # cv.CvtColor(frameimg, tmp, cv.CV_BGR2RGB)
            cv.CvtColor(frameimg, tmp, cv.CV_RGB2GRAY)
            cv.ShowImage("CreateImage", tmp)
            array = np.asarray(cv.GetMat(tmp))
            out.write(array)
            cv.ShowImage("hcq", frameimg)
            cv.WaitKey(1)


def buscar_video():
    """
    Se solicita la selección de un archivo de video al usuario
    :return:
    """
    global video
    global nombre_video
    global matrizMedidas3D
    try:
        file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
        if file:
            cap = cv.CaptureFromFile(file.name)
            nombre_video = file.name
            nframes = str(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
            fps = str(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
            # txt_video.insert(0, file.name)
            video = file.name
            mensaje = file.name + "\n" + "Frames: " + nframes + "\n" + "FPS: " + fps
            txt_datos_video.delete(1.0, END)
            txt_datos_video.insert(END, mensaje)
            matrizMedidas3D = None
    except:
        error = str(sys.exc_info()[0]) + str(sys.exc_info()[1])
        tkMessageBox.showerror("Error", error)


def reproducir_video():
    """
    Se realiza la reproducción del video seleccionado
    :return:
    """
    global video
    if video is None:
        tkMessageBox.showerror("Error", "No se seleccionó el video")
    else:
        nframes = int(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_COUNT))
        for f in xrange(nframes):
            frameimg = cv.QueryFrame(video)
            cv.ShowImage("hcq", frameimg)
            cv.WaitKey(1)


def calcular_medidas_3d():
    """
    Generación de la matriz de alturas.
    :return: Matriz de alturas
    """
    global video
    global nombre_video
    global px_mm_x
    global px_mm_y
    global px_mm_z
    global extremo_izquierdo
    global extremo_derecho
    global calibracion_base
    global matrizMedidas3D

    if validar_datos_generar_3d():
        # print video, px_mm_x, px_mm_y, px_mm_z, extremo_izquierdo, extremo_derecho, calibracion_base
        columnas = ((extremo_derecho - extremo_izquierdo) + 1)
        matrizMedidas3D = np.zeros((1, columnas))
        video = cv2.VideoCapture(nombre_video)
        while video.isOpened():
            ret, frame = video.read()
            if frame is not None:
                flaco = esqueletizador(frame, False)
                cv2.imshow('Flaco', flaco)
                vector = medicion_perfil(flaco, columnas)
                # transforma el vector a una matriz
                matriz_parciales = np.asmatrix(vector)
                # inserta la nueva matriz en una nueva fila de la matriz de mediciones
                matrizMedidas3D = np.r_[matrizMedidas3D, matriz_parciales]
            else:
                video.release()

        try:
            archivo_medidas = nombre_video + " - medidas3D.txt"
            np.savetxt(archivo_medidas, matrizMedidas3D, fmt='%1.2f', delimiter=';')
            print "La matriz de medidas fue almacenada con el nombre: " + archivo_medidas
            tkMessageBox.showinfo("Almacenamiento de Medidas",
                                  "La matriz de medidas fue almacenada con el nombre: " + archivo_medidas)
            txt_matriz_cargada.insert(0, archivo_medidas)

        except:
            error = str(sys.exc_info()[0]) + str(sys.exc_info()[1])
            tkMessageBox.showerror("Error Generando 3D", error)
            # dibujar_3d(matriz)


def medicion_perfil(imagen, columnas):
    """
    Medición 1 perfil completo
    :param imagen: La imagen a analizar
    :param columnas: cantidad de columnas a analizar
    :return:
    """
    global video
    global extremo_izquierdo
    global extremo_derecho
    global calibracion_base
    global px_mm_z

    medidas = np.zeros(columnas)

    superior = detectar_extremos(imagen, "n")[0]
    # print superior, calibracion_base
    # alto, largo = imagen.shape[:2]
    print extremo_izquierdo, int(extremo_izquierdo), extremo_derecho, int(extremo_derecho)
    for c in range(int(extremo_izquierdo), int(extremo_derecho) + 1, 1):
        for f in range(int(superior), int(calibracion_base), 1):
            if imagen[f, c] == 0:
                altura_mm = round(((calibracion_base - f) * px_mm_z), 2)
                medidas[c - extremo_izquierdo] = altura_mm
                break
    return medidas


def validar_datos_generar_3d():
    """
    Validación de los datos para la medición 3D
    :return:
    """

    global px_mm_x
    global px_mm_z
    global px_mm_y
    global calibracion_base
    global video
    global velocidad
    global extremo_derecho
    global extremo_izquierdo

    parametros = {"Patron X": px_mm_x,
                  "Patron Y": px_mm_y,
                  "Patron Z": px_mm_y,
                  "Calibracion Base": calibracion_base,
                  "Extremo Derecho": extremo_derecho,
                  "Extremo Izquierdo": extremo_izquierdo}

    resultado = True
    mensaje = ""

    for i in parametros:
        if not(isinstance(parametros[i], float)) or parametros[i] <= 0:
            mensaje += "El parametro: " + str(i) + " debe se un numero entero > 0\n"
            resultado = False

    if len(video) == 0:
        mensaje += "No se cargó el video\n"
        resultado = False

    if not resultado:
        tkMessageBox.showerror("Error", mensaje)

    return resultado


def generar_imagen_3d():
    """
    Trazado del gráfico 3D
    :return:
    """
    global px_mm_x
    global px_mm_y
    global nombre_video
    global matrizMedidas3D

    z = []
    if matrizMedidas3D is None:
        try:
            archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar el archivo con la Matriz de Medidas')
            if archivo:
                matrizMedidas3D = genfromtxt(archivo.name, delimiter=';')
                nombre = os.path.split(archivo.name)[1]
                nombre_archivo = ""
                for i in nombre:
                    if i != ".":
                        nombre_archivo += i
                    else:
                        break
                txt_matriz_cargada.delete(0, END)
                txt_matriz_cargada.insert(0, nombre_archivo)
                z = matrizMedidas3D
        except ValueError:
            tkMessageBox.showerror("Error", "Verifique el archivo seleccionado")
        except:
            tkMessageBox.showerror("Error", "Error Inesperado")
    else:
        z = matrizMedidas3D

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
        tkMessageBox.showerror("Error", "Falta Buscar Datos")

    """if matrizMedidas3D is None:
        tkMessageBox.showerror("Medidas 3D No Calculadas", "Las Medidas 3D No Fueron Realizadas")
    else:
        alto, largo = matrizMedidas3D.shape[:2]
        x = np.zeros(largo)
        y = np.zeros(alto)

        for c in range(len(X)):
            x[c] = px_mm_x * c

        for c in range(len(Y)):
            y[c] = px_mm_y * c

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x, y = np.meshgrid(x, y)

        print x, y, matrizMedidas3D

        # Tipo de gráfico
        surf = ax.plot_surface(x, y, matrizMedidas3D, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

        # configuraciones del eje z
        ax.set_zlim(-1.01, 15)
        ax.zaxis.set_major_locator(LinearLocator(10))
        ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        fig.colorbar(surf, shrink=0.5, aspect=5)

        plt.show()
"""

def guardar_configuracion():
    """
    Se guardan los datos de configuración del escaneo
    :return:
    """
    global px_mm_x
    global px_mm_y
    global px_mm_z
    global calibracion_base
    global extremo_izquierdo
    global extremo_derecho
    try:
        if px_mm_y == 0.0:
            px_mm_y = px_mm_x
        datos = [px_mm_x, px_mm_y, px_mm_z, calibracion_base, extremo_izquierdo, extremo_derecho]
        np.savetxt("Configuracion.txt", datos, fmt='%1.3f', delimiter=';')
        tkMessageBox.showinfo("Atención", "Se guardo el archivo de configuración de escaneo")
    except:
        tkMessageBox.showerror("Error", "Error al escribir el archivo de configuración de escaneo")


def ver_camara():
    """
    Visualización de la señal de video sin procesamiento
    :return:
    """
    try:
        id_disp = int(txt_id_dispositivo.get())
        if not cv2.VideoCapture(id_disp).read()[0]:
            tkMessageBox.showerror("Error", "No se detectó la Cámara")
        else:
            camara = cv2.VideoCapture(id_disp)
            for i in range(200):
                ret, frame = camara.read()
                cv2.imshow('Camara', frame)
                cv2.waitKey(1)
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    cv2.destroyWindow('Camara')
                    break
            cv2.destroyWindow('Camara')
            camara.release()
    except (ValueError, TypeError):
        tkMessageBox.showerror("Error", "Verificar el ID de la Cámara")


def calcular_tiempo_espera():
    """
    Se calcula el tiempo de espera en función de la separación entre perfiles de escaneo
    :return:
    """
    global tiempo_espera
    global velocidad
    global px_mm_y
    global nombre_video

    if velocidad != 0.0 and len(nombre_video) > 0:
        """separacion = float(txt_separacion_perfiles.get())
        px_mm_y = separacion
        tiempo_espera = '%.3f' % (separacion / velocidad)
        txt_tiempo_espera.delete(0, END)
        txt_tiempo_espera.insert(0, tiempo_espera)
        btn_capturar_video.config(state=NORMAL)"""
        frames = int(txt_separacion_perfiles.get())
        cap = cv.CaptureFromFile(nombre_video)
        fps = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
        mmxf = velocidad / fps
        px_mm_y = mmxf * frames
        txt_tiempo_espera.delete(0, END)
        txt_tiempo_espera.insert(0, px_mm_y)
        btn_filtrar_video.config(state=NORMAL)

    elif velocidad == 0.0:
        tkMessageBox.showwarning('Atención', "La velocidad no fué determinada")

    elif len(nombre_video) == 0:
        tkMessageBox.showwarning('Atención', "La velocidad no fué determinada")


def cargar_configuracion():
    """
    Solicitud al usuario para cargar los datos de configuración
    :return:
    """
    global px_mm_x
    global px_mm_y
    global px_mm_z
    global calibracion_base
    global extremo_izquierdo
    global extremo_derecho
    global medidas
    try:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal,
                                           title='Seleccionar el archivo con los Datos de Configuracion')
        if archivo:
            with open(archivo.name, "r") as ins:
                array = []
                for line in ins:
                    array.append(float(line))

            px_mm_x = array[0]
            px_mm_y = array[1]
            px_mm_z = array[2]
            calibracion_base = array[3]
            extremo_izquierdo = array[4]
            extremo_derecho = array[5]

            txt_x.delete(0, END)
            txt_x.insert(0, px_mm_x)
            txt_y.delete(0, END)
            txt_y.insert(0, px_mm_y)
            txt_z.delete(0, END)
            txt_z.insert(0, px_mm_z)
            txt_base.delete(0, END)
            txt_base.insert(0, calibracion_base)
            txt_iz.delete(0, END)
            txt_iz.insert(0, extremo_izquierdo)
            txt_der.delete(0, END)
            txt_der.insert(0, extremo_derecho)

    except ValueError:
        tkMessageBox.showerror("Error", "Verifique el archivo seleccionado")
    except:
        tkMessageBox.showerror("Error", "Error Inesperado")


def capturar_normal():
    """
    Crea un video capturando frames, tomando como referencia la velocidad medida en el etapa anterior
    :return:
    """
    global camara
    global id_dispositivo
    global tiempo_espera
    if not cv2.VideoCapture(int(txt_id_dispositivo.get())).read()[0]:
        tkMessageBox.showerror("Error", "No se detectó la Cámara")
    else:
        camara = cv2.VideoCapture(id_dispositivo)
        if len(txt_nombre_normal.get()) == 0:
            nombre = "normal.avi"
        else:
            nombre = txt_nombre_normal.get() + '.avi'
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter(nombre, fourcc, 20.0, (640, 480))
        try:
            while True:
                ret, color = camara.read()
                out.write(color)
                cv2.imshow('Camara', color)
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    tkMessageBox.showinfo("Captura de Video",
                                          "Una nueva captura fué realizada con el Nombre: " + nombre)
                    txt_nombre_normal.delete(0, END)
                    break
        except:
            tkMessageBox.showerror("Error", "Error Inesperado")
        cv2.destroyWindow('Camara')
        camara.release()


def cargar_normal():
    global normal
    """try:
        archivo = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar el video Normal')
        if archivo:
            normal = archivo
            nombre = os.path.split(archivo.name)[1]
            txt_nombre_normal.delete(0, END)
            txt_nombre_normal.insert(0, nombre)
            cap = cv.CaptureFromFile(file.name)
            nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
            fps = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
            print nframes, fps
    except:
        tkMessageBox.showerror("Error", "Error Inesperado")
    """
    try:
        file = tkFileDialog.askopenfile(parent=vtnPrincipal, title='Seleccionar un Archivo')
        if file is not None:
            normal = file.name
            cap = cv.CaptureFromFile(file.name)
            nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT))
            fps = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS))
            datos = "Total frames: " + str(nframes) + ", fps: " + str(fps)
            # txt_datos_normal.delete(0, END)
            # txt_datos_normal.insert(0, datos)
            # print "total frame", nframes
            # print "fps", fps
            print " currpos of videofile", cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_POS_MSEC)
            print cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FOURCC)
    except:
        tkMessageBox.showerror("Error", sys.exc_info()[0])


# ----------------------------------------------------------------------------
# Definición de GUI
contenedor_pestanas = Notebook(vtnPrincipal)
pestana_calibracion_camara = Frame(contenedor_pestanas)
pestana_calibracion_velocidad = Frame(contenedor_pestanas)
pestana_generacion_3d = Frame(contenedor_pestanas)

contenedor_pestanas.add(pestana_calibracion_camara, text="Cámara")
contenedor_pestanas.add(pestana_calibracion_velocidad, text="Velocidad")
contenedor_pestanas.add(pestana_generacion_3d, text="3D")

contenedor_pestanas.pack()

# region Cámara
# region 1 - Calibración de Cámara

btn_ver_camara = Button(pestana_calibracion_camara, text="Ver Camara", command=ver_camara)
# btn_carga_normal           = Button(pestana_calibracion_camara, text="Cargar Normal", command=cargar_normal)
# txt_datos_normal           = Entry(pestana_calibracion_camara, width=45)
btn_guardar_configuracion = Button(pestana_calibracion_camara, text="Guardar Configuración",
                                   command=guardar_configuracion)

btn_ver_camara.grid(row=1, column=0)
# btn_carga_normal           .grid(row=2, column=0)
# txt_datos_normal           .grid(row=3, column=0, columnspan=2)
btn_guardar_configuracion.grid(row=1, column=1, columnspan=2)

lblf_enlace_camara = LabelFrame(pestana_calibracion_camara, text="1 - Calibración de Cámara")
lblf_patron = LabelFrame(pestana_calibracion_camara, text="2 - Calibración Eje Z y X")
lblf_extremos = LabelFrame(pestana_calibracion_camara, text="3 - Calibración de Extremos")
lblf_CapturaNormal = LabelFrame(pestana_calibracion_camara, text="4 - Captura de Video")

lbl_id_dispositivo = Label(lblf_enlace_camara, text="ID Dispositivo: ")
txt_id_dispositivo = Entry(lblf_enlace_camara, width=5)
lbl_umbral = Label(lblf_enlace_camara, text="Umbral: ")
txt_umbral = Entry(lblf_enlace_camara, width=5)
btn_acceder = Button(lblf_enlace_camara, text="Calibrar", command=calibrar_camara_laser)
lbl_conteo = Label(lblf_enlace_camara, text="Conteo Px:")
txt_conteo = Entry(lblf_enlace_camara, width=5)
lbl_superior = Label(lblf_enlace_camara, text="Fila:")
txt_superior = Entry(lblf_enlace_camara, width=5)

txt_id_dispositivo.insert(0, 0)
txt_umbral.insert(0, 254)
txt_conteo.insert(0, 0)
txt_superior.insert(0, 0)

lblf_enlace_camara.grid(row=0, column=0)
lbl_id_dispositivo.grid(row=0, column=0, sticky="e")
txt_id_dispositivo.grid(row=0, column=1, sticky="w")
lbl_umbral.grid(row=1, column=0, sticky="e")
txt_umbral.grid(row=1, column=1, sticky="w")
btn_acceder.grid(row=2, column=0, columnspan=2)
lbl_conteo.grid(row=3, column=0, sticky="e")
txt_conteo.grid(row=3, column=1, sticky="w")
lbl_superior.grid(row=4, column=0, sticky="e")
txt_superior.grid(row=4, column=1, sticky="w")

# endregion

# region 2 - Calibración con Patrón Eje Z y X
# lbl_valor          = Label( lblf_patron, text="Valor")
# lbl_PixelMM        = Label( lblf_patron, text="Px-MM")
lbl_valor_muestraV = Label(lblf_patron, text="Z:")
txt_valor_muestraV = Entry(lblf_patron, width=7)
lbl_valor_muestraH = Label(lblf_patron, text="X:")
txt_valor_muestraH = Entry(lblf_patron, width=7)
txt_pixelmmV = Entry(lblf_patron, width=7)
txt_pixelmmH = Entry(lblf_patron, width=7)
btn_calibrar_patron = Button(lblf_patron, text="Calibrar", command=calibrar_patron, state=DISABLED)

txt_valor_muestraV.insert(0, 10)
txt_valor_muestraH.insert(0, 12)
txt_pixelmmV.insert(0, 0)
txt_pixelmmH.insert(0, 0)

lblf_patron.grid(row=0, column=1, sticky="n")
# lbl_valor              .grid(row=0, column=1)
# lbl_PixelMM            .grid(row=0, column=3)
lbl_valor_muestraV.grid(row=1, column=0, sticky="e")
txt_valor_muestraV.grid(row=1, column=1, sticky="w")
lbl_valor_muestraH.grid(row=2, column=0, sticky="e")
txt_valor_muestraH.grid(row=2, column=1, sticky="w")
txt_pixelmmV.grid(row=1, column=3, sticky="w")
txt_pixelmmH.grid(row=2, column=3, sticky="w")
btn_calibrar_patron.grid(row=1, column=2, rowspan=2)

# endregion

# region 3 - Calibracion de extremos Izquierdo y Derecho

btn_calibrar_extremos = Button(lblf_extremos, text="Calibrar", command=calibrar_extremos, state=DISABLED)
lbl_izquierdo = Label(lblf_extremos, text="Izquierdo:")
txt_izquierdo = Entry(lblf_extremos, width=7)
lbl_derecho = Label(lblf_extremos, text="Derecho:")
txt_derecho = Entry(lblf_extremos, width=7)

lblf_extremos.grid(row=0, column=1, sticky="sw")
btn_calibrar_extremos.grid(row=0, column=0, sticky="w", rowspan=2)
lbl_izquierdo.grid(row=0, column=1, sticky="w")
txt_izquierdo.grid(row=0, column=2, sticky="w")
lbl_derecho.grid(row=1, column=1, sticky="w")
txt_derecho.grid(row=1, column=2, sticky="w")

# endregion

# region 4 - Captura de Video

btn_captura_normal = Button(lblf_CapturaNormal, text="Capturar Normmal", command=capturar_normal)
lnl_nombre_normal = Label(lblf_CapturaNormal, text="Nombre del Video")
txt_nombre_normal = Entry(lblf_CapturaNormal)

lblf_CapturaNormal.grid(row=2, column=0, columnspan=2)
lnl_nombre_normal.grid(row=0, column=0)
txt_nombre_normal.grid(row=0, column=1)
btn_captura_normal.grid(row=1, column=0, columnspan=2)

# endregion

# endregion

# region Velocidad

lblf_calibrar_patron_velocidad = LabelFrame(pestana_calibracion_velocidad, text="1- Calibración de Patrón")
btn_calibrar_velocidad = Button(lblf_calibrar_patron_velocidad, text="Calibrar Patron Velocidad",
                                command=calibrar_velocidad, state=DISABLED)
lbl_patron = Label(lblf_calibrar_patron_velocidad, text="Medida Patron:")
txt_medida_patron_velocidad = Entry(lblf_calibrar_patron_velocidad, width=5)

lblf_medir_velocidad = LabelFrame(pestana_calibracion_velocidad, text="2- Medir Velocidad")
btn_medir_velocidad = Button(lblf_medir_velocidad, text="Medir Velocidad", command=medir_velocidad, state=DISABLED)
lbl_velocidad = Label(lblf_medir_velocidad, text="velocidad:")
txt_velocidad = Entry(lblf_medir_velocidad, width=10)

lblf_calcular_tiempo_espera = LabelFrame(pestana_calibracion_velocidad, text="3- Calcular Tiempo de Espera")
lbl_separacion_perfiles = Label(lblf_calcular_tiempo_espera, text="Frames")
txt_separacion_perfiles = Entry(lblf_calcular_tiempo_espera, width=5)
btn_calcular_tiempo_espera = Button(lblf_calcular_tiempo_espera, text="Medir Separacion",
                                    command=calcular_tiempo_espera, state=DISABLED)
lbl_tiempo_espera = Label(lblf_calcular_tiempo_espera, text="mm X perfil:")
txt_tiempo_espera = Entry(lblf_calcular_tiempo_espera, width=10)

lblf_captura_video = LabelFrame(pestana_calibracion_velocidad, text="4- Filtrar Video")
lbl_nombre_video = Label(lblf_captura_video, text="Nombre Video:")
txt_nombre_video = Entry(lblf_captura_video, width=10)
# btn_capturar_video             = Button(lblf_captura_video, text="Capturar Video", command=capturar_video, state=DISABLED)
btn_filtrar_video = Button(lblf_captura_video, text="Filtrar Video", command=filtrar_video)

txt_nombre_video.insert(0, "")
txt_medida_patron_velocidad.insert(0, 10)

lblf_calibrar_patron_velocidad.grid(row=0, column=0, sticky="n")
btn_calibrar_velocidad.grid(row=0, column=0, columnspan=2)
lbl_patron.grid(row=1, column=0, sticky="e")
txt_medida_patron_velocidad.grid(row=1, column=1, sticky="w")

lblf_medir_velocidad.grid(row=1, column=0, sticky="s")
btn_medir_velocidad.grid(row=2, column=0, columnspan=2)
lbl_velocidad.grid(row=3, column=0, sticky="e")
txt_velocidad.grid(row=3, column=1)

lblf_calcular_tiempo_espera.grid(row=0, column=1, sticky="nw")
lbl_separacion_perfiles.grid(row=0, column=0)
txt_separacion_perfiles.grid(row=0, column=1)
btn_calcular_tiempo_espera.grid(row=1, column=0, columnspan=2)
lbl_tiempo_espera.grid(row=2, column=0, sticky="e")
txt_tiempo_espera.grid(row=2, column=1)

lblf_captura_video.grid(row=1, column=1, sticky="e")
lbl_nombre_video.grid(row=1, column=0, sticky="e")
txt_nombre_video.grid(row=1, column=1, sticky="w")
# btn_capturar_video             .grid(row=2, column=0)
btn_filtrar_video.grid(row=2, column=0)

# endregion+

# region 3D
lblf_buscar_configuracion = LabelFrame(pestana_generacion_3d, text="1 - Cargar Configuración")
btn_buscar_configuracion = Button(lblf_buscar_configuracion, text="Cargar Configuración", command=cargar_configuracion)
lbl_x = Label(lblf_buscar_configuracion, text="X")
lbl_z = Label(lblf_buscar_configuracion, text="Z")
lbl_y = Label(lblf_buscar_configuracion, text="Y")
lbl_iz = Label(lblf_buscar_configuracion, text="Izquierdo")
lbl_der = Label(lblf_buscar_configuracion, text="Derecho")
lbl_base = Label(lblf_buscar_configuracion, text="Base")
txt_x = Entry(lblf_buscar_configuracion, width=10)
txt_z = Entry(lblf_buscar_configuracion, width=10)
txt_y = Entry(lblf_buscar_configuracion, width=10)
txt_iz = Entry(lblf_buscar_configuracion, width=10)
txt_der = Entry(lblf_buscar_configuracion, width=10)
txt_base = Entry(lblf_buscar_configuracion, width=10)

lblf_buscar_video = LabelFrame(pestana_generacion_3d, text="2 - Cargar Video")
btn_buscar_video = Button(lblf_buscar_video, text='Cargar Video', command=buscar_video)
# lbl_video                      = Label(lblf_buscar_video, text="Video")
txt_datos_video = Text(lblf_buscar_video, width=15, height=4)
# txt_video                      = Entry(lblf_buscar_video, width=10)

btn_calcularMedidas3D = Button(pestana_generacion_3d, text="Calcular Medidas 3D", command=calcular_medidas_3d)
btn_generarImagen3D = Button(pestana_generacion_3d, text="Generar Imagen 3D", command=generar_imagen_3d)

lbl_matriz_cargada =            Label(pestana_generacion_3d, text="Matriz de Medidas 3D:")
txt_matriz_cargada =            Entry(pestana_generacion_3d, width=20)

txt_x.insert(0, 0)
txt_y.insert(0, 0)
txt_z.insert(0, 0)
txt_iz.insert(0, 0)
txt_der.insert(0, 0)
txt_base.insert(0, 0)

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
btn_buscar_video.grid(          row=1, column=0, columnspan=2)
# lbl_video                       .grid(row=2, column=0, sticky="we")
txt_datos_video.grid(           row=2, column=1, sticky="we")
# txt_video                       .grid(row=2, column=1, sticky="we")

btn_calcularMedidas3D.grid(     row=1, column=0, columnspan=2)
btn_generarImagen3D.grid(       row=3, column=0, columnspan=2)

lbl_matriz_cargada.grid(        row=2, column=0, sticky="e")
txt_matriz_cargada.grid(        row=2, column=1, sticky="w")

# endregion

vtnPrincipal.mainloop()
