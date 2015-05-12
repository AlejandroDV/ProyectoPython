# coding=utf-8

__author__ = "alejandro"
__date__ = "$13-feb-2015 18:46:04$"

import numpy
import cv2
from Tkinter import *
import tkMessageBox
from matplotlib import pyplot as plt
vtnPrincipal = Tk()

#Se visualiza la señal de la camara

def enlazar():
#Validación de Datos

    if ValidadorDatos()==0:
        idDispositivo = int(txtIdDispositivo.get())
        valorUmbral = int(txtUmbral.get())
        camara = cv2.VideoCapture(idDispositivo)
        
        while True:
            # Se lee un frame
            ret, frame = camara.read()

            # Se crea el filtro para el video de entrada en tonos de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Se crea la imagen binarizada
            ret,binario = cv2.threshold(gray,valorUmbral,255,cv2.THRESH_BINARY_INV)

            print "Suavizado Binario"
            #https://li8bot.wordpress.com/2014/08/07/opencvpythonpart3-smoothing-images/
            ladoKernel=5         
            blur = cv2.medianBlur(binario,ladoKernel)
            blurO=blur
            
            print "Esqueletizado"
            #http://opencvpython.blogspot.com.ar/2012/05/skeletonization-using-opencv-python.html
            size = numpy.size(binario)
            skelB = numpy.zeros(blur.shape,numpy.uint8)
            element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
            done = False
            
            while( not done):
                print done
                erodedB = cv2.erode(blur,element)
                temp = cv2.dilate(erodedB,element)
                temp = cv2.subtract(blur,temp)
                skelB = cv2.bitwise_or(skelB,temp)
                blur = erodedB.copy()
                zeros = size - cv2.countNonZero(blur)
                if zeros==size:
                    done = True
                     
            #Canny
            #cany = cv2.Canny(skelBB, 0.2, 0.3)         
            
            print "Mostrando Pantallas"
            cv2.imshow('1 Color',frame)
            cv2.imshow('Grises',gray)
            cv2.imshow('2 Binario',binario)
            cv2.imshow("3 Suavizado Binario",blurO)
            cv2.imshow("4 Esqueleto luego de Suavizado",skelB)
            
            if cv2.waitKey(33) & 0xFF == ord('q'):break

#Se cierran las pantallas
def cerrar():
	cv2.destroyWindow('1 Color')
        cv2.destroyWindow('Grises')
	cv2.destroyWindow('2 Binario')
	cv2.destroyWindow('3 Suavizado Binario')
	cv2.destroyWindow('4 Esqueleto luego de Suavizado')
	
#Se validan los datos ingresados
def ValidadorDatos():
	error = 0
	mensaje =""
	#ID Invádido
	try :
		idDispositivo = int(txtIdDispositivo.get())
	except ValueError:
		mensaje = "Valor de ID de Dispositivo Incorrecto"
		error = 1
	
	#Umbral Inválido
	try :	
		valorUmbral = int(txtUmbral.get())
		if (valorUmbral < 0 or valorUmbral > 255):
			error = 3
			mensaje = "0<=Umbral<=255"
	except ValueError:	
		mensaje = "Valor de Umbral Incorrecto"
		error = 2
	
	if (error <> 0):
		tkMessageBox.showerror("Error",mensaje)
	return error
	
	
#Identificador de Dispositivo de Captura
lblIdDispositivo = Label(vtnPrincipal, text="ID Dispositivo: ").grid(row=0, sticky=W)
txtIdDispositivo = Entry(vtnPrincipal)
txtIdDispositivo.insert(0,0)
txtIdDispositivo.grid(row=0, column=1)

# Distancia al cuerpo de calibrado
lblDistancia = Label(vtnPrincipal, text="Distancia Calibrado: ").grid(row=1, sticky=W)
txtDistanciaCalibrado = Entry(vtnPrincipal)
txtDistanciaCalibrado.grid(row=1, column=1)

#Valor de Umbral para el Binarizado
lblUmbral = Label(vtnPrincipal, text="Umbral: ").grid(row=2, sticky=W)
txtUmbral = Entry(vtnPrincipal)
txtUmbral.insert(0,254)
txtUmbral.grid(row=2, column=1)

#Iniciador de Procesamiento
btnAcceder = Button(vtnPrincipal, text="Enlazar",command=enlazar)
btnAcceder.grid(row=3, column=0)

#Finalizador de Procesamiento
btnCerrar = Button(vtnPrincipal, text="Finalizar",command=cerrar)
btnCerrar.grid(row=3, column=1)

lblIdDispositivo = Label(vtnPrincipal, text="Presionar q para detener captura").grid(row=4, sticky=W)

vtnPrincipal.mainloop()

