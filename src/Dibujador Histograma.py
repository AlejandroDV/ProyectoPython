# coding=utf-8
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "alejandro"
__date__ = "$23-mar-2015 14:21:14$"

import numpy
import cv2
camara = cv2.VideoCapture(0)

while True:
    #Se captura la señalde la cámara
    ret, frame = camara.read()
    #Se transforma la a tonos de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #print 'Tamaño Frame Color: ',str(frame.size)
    #print 'Tamaño Frame Tonos de Grises: ',str(gray.size), '.Filas x Columnas: ',gray.shape
    #Se creará una matriz con 0 (Filas, Columnas, Profundidad)
    h = numpy.zeros((600,256,3))
    #Arange retorna un array con todos los numeros entre 0 y (256-1)
    #reshape cambia la forma que tiene un array a 256 filas x 1 columna
    bins = numpy.arange(256).reshape(256,1)
    #Se calcula el histograma(imagen original,canal(0 gris),mascara,
    #tamaño array resultante,rango)
    hist_item = cv2.calcHist([gray],[0],None,[256],[0,256])
    #print hist_item, numpy.sum(hist_item)
    #redondeo, se corre la coma y se descarta la parte decimal
    hist=numpy.int32(numpy.around(hist_item))
    #print hist
    #Se crea una matriz con estas columnas:Indices (0-255)| conteo
    pts = numpy.column_stack((bins,hist))
    #Se dibujan los segmentos de un poligono con los sig. parámetros:
    #   1- matriz de ceros
    #   2- matriz con los índices y conteos
    #   3- False => Forma como se unirán los extremos de la polilinea.
    #   4- Color
    cv2.polylines(h,[pts],False,(255,255,255))
    #Se da la vuelta a la matriz de ceros para que el gráfico 
    #tenga una base en x y se desarrolle hacia arriba
    h=numpy.flipud(h)
    #Se muestra el gráfico
    cv2.imshow('Histograma Grises',h)

    
    cv2.imshow('1 Color',frame)
    cv2.imshow('Grises',gray)
    if cv2.waitKey(33) & 0xFF == ord('q'):break

