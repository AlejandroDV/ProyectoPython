# coding=utf-8
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "alejandro"
__date__ = "$26-mar-2015 17:00:12$"

import numpy
import cv2
camara = cv2.VideoCapture(0)

while True:
    #Se captura la señalde la cámara
    ret, frame = camara.read()
    #Se transforma la a tonos de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    umbral=250
    #ret,binario = cv2.threshold(gray,umbral,255,cv2.THRESH_BINARY)
    ret,binario = cv2.threshold(gray,umbral,255,cv2.THRESH_BINARY_INV)
    
    
    Blur3 = cv2.medianBlur(binario,3)
    Blur5 = cv2.medianBlur(binario,5)
    Blur7 = cv2.medianBlur(binario,7)
    Blur9 = cv2.medianBlur(binario,9)
    
    #Histograma
#    h = numpy.zeros((600,256,3))
#    bins = numpy.arange(256).reshape(256,1)
#    hist_item = cv2.calcHist([Blur3],[0],None,[256],[0,256])
#    hist=numpy.int32(numpy.around(hist_item))
#    pts = numpy.column_stack((bins,hist))
#    cv2.polylines(h,[pts],False,(255,255,255))
#    h=numpy.flipud(h)
    
    #Se muestran la imágenes con sus respectivos procesamientos
#    cv2.imshow('Histograma Grises',h)
    #cv2.imshow('Grises',gray)
    cv2.imshow('Binario',binario)
    cv2.imshow('Blur3',Blur3)
    cv2.imshow('Blur5',Blur5)
    cv2.imshow('Blur7',Blur7)
    cv2.imshow('Blur9',Blur9)
    if cv2.waitKey(33) & 0xFF == ord('q'):break
