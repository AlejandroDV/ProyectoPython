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
            ret,binario2 = cv2.threshold(gray,valorUmbral,255,cv2.THRESH_BINARY)
            ret,contorno = cv2.threshold(gray,valorUmbral,255,cv2.THRESH_BINARY)
            #ret,binario3 = cv2.threshold(gray,valorUmbral,255,cv2.THRESH_BINARY)
            ret,binario4 = cv2.threshold(gray,valorUmbral,255,cv2.THRESH_BINARY)

            # Se crea la imagen con la detección de contornos
            contours, hierarchy = cv2.findContours(contorno,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            

            #1- Suavizado Binario
            #https://li8bot.wordpress.com/2014/08/07/opencvpythonpart3-smoothing-images/
            ladoKernel=5
            #blur = cv2.GaussianBlur(binario4,(ladoKernel,ladoKernel),0)
            #blur=cv2.blur(binario4,(ladoKernel,ladoKernel))
            blur = cv2.medianBlur(binario4,ladoKernel)
            blurO=blur
            
            #1- Suavizado Binario; 2- Esqueletizado
            #http://opencvpython.blogspot.com.ar/2012/05/skeletonization-using-opencv-python.html
            size = numpy.size(binario4)
            skelB = numpy.zeros(blur.shape,numpy.uint8)
            element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
            done = False
            
            while( not done):
                erodedB = cv2.erode(blur,element)
                temp = cv2.dilate(erodedB,element)
                temp = cv2.subtract(blur,temp)
                skelB = cv2.bitwise_or(skelB,temp)
                blur = erodedB.copy()
                zeros = size - cv2.countNonZero(blur)
                if zeros==size:
                    done = True
            
            #1- Suavizado Binario; 2- Esqueletizado; 3- Binarizado
            ret,BlurBin = cv2.threshold(blurO,150,255,cv2.THRESH_BINARY)
            BB=BlurBin
            
            #1- Suavizado Binario; 2- Esqueletizado; 3- Binarizado; 4- Esqueletizado
            size = numpy.size(BB)
            skelBB = numpy.zeros(BB.shape,numpy.uint8)
            element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
            done = False
 
            while( not done):
                erodedBB = cv2.erode(BB,element)
                temp = cv2.dilate(erodedBB,element)
                temp = cv2.subtract(BB,temp)
                skelBB = cv2.bitwise_or(skelBB,temp)
                BB = erodedBB.copy()
                zeros = size - cv2.countNonZero(BB)
                if zeros==size:
                    done = True
            
            #Canny
            cany = cv2.Canny(skelBB, 0.2, 0.3)
            
            #Dibujo del histograma color
            img = frame
            h = numpy.zeros((300,256,3))
            bins = numpy.arange(256).reshape(256,1)
            color = [ (255,0,0),(0,255,0),(0,0,255) ]
            for ch, col in enumerate(color):
                hist_item = cv2.calcHist([img],[ch],None,[256],[0,256])
                cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
                hist=numpy.int32(numpy.around(hist_item))
                pts = numpy.column_stack((bins,hist))
                cv2.polylines(h,[pts],False,col)

            h=numpy.flipud(h)

            cv2.imshow('colorhist',h)
            
            #Dibujo del Histograma en grises ***********************************
            
            img = gray
            #Se creará una matriz con 0 (Filas, Columnas, Profundidad)
            h = numpy.zeros((300,256,3))
            #Arange retorna un array con todos los numeros entre 0 y (256-1)
            #reshape cambia la forma que tiene un array a 256 filas x 1 columna
            bins = numpy.arange(256).reshape(256,1)
            #Se calcula el histograma(imagen original,canal(0 gris),mascara,
            #tamaño array resultante,rango)
            hist_item = cv2.calcHist([img],[0],None,[256],[0,256])
            #Se normaliza los valores del histograma para adecuarlos a 0-255
            cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
            #redondeo, se corre la coma y se descarta la parte decimal
            hist=numpy.int32(numpy.around(hist_item))
            #Se crea una matriz con estas columnas:Indices (0-255)| conteo
            pts = numpy.column_stack((bins,hist))
            #Se dibujan los segmentos de un poligono con los sig. parámetros:
            #   1- matriz de ceros
            #   2- matriz con los índices y conteos
            #   3- False => Forma como se unirán los extremos de la polilinea.
            #   4- Color
            cv2.polylines(h,[pts],False,(0,0,255))
            #Se da la vuelta a la matriz de ceros para que el gráfico 
            #tenga una base en x y se desarrolle hacia arriba
            h=numpy.flipud(h)
            #Se muestra el gráfico
            cv2.imshow('Grey',h)
            
            
            #Dibujo colores con matplotlib 
            #hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            #plt.figure()
            #plt.title("Grayscale Histogram")
            #plt.xlabel("Bins")
            #plt.ylabel("# of Pixels")
            #plt.plot(hist)
            #plt.xlim([0, 256])
            
            
            cv2.imshow('1 Color',frame)
            cv2.imshow('Grises',gray)
            cv2.imshow('2 Binario',binario)
            cv2.imshow("3 Suavizado Binario",blurO)
            cv2.imshow("5 Esqueleto luego de Suavizado",skelB)
            cv2.imshow("4 Binario Suavizado Binarizado",BlurBin)
            cv2.imshow("6 Esqueleto Binario Suavizado Binarizado",skelBB)
            cv2.imshow("Cany",cany)
            
            
            
            if cv2.waitKey(33) & 0xFF == ord('q'):break

#Se cierran las pantallas
def cerrar():
	cv2.destroyWindow('1 Color')
        cv2.destroyWindow('Grises')
	cv2.destroyWindow('2 Binario')
	cv2.destroyWindow('3 Suavizado Binario')
	cv2.destroyWindow('4 Binario Suavizado Binarizado')
	cv2.destroyWindow('5 Esqueleto luego de Suavizado')
	cv2.destroyWindow('6 Esqueleto Binario Suavizado Binarizado')
	
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

