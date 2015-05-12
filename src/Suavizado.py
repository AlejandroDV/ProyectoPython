# coding=utf-8
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
    
    
    ladoKernel=5
    GBlur  = cv2.GaussianBlur(binario,(ladoKernel,ladoKernel),0)
    Blur = cv2.blur(binario,(ladoKernel,ladoKernel))
    MBlur = cv2.medianBlur(binario,ladoKernel)
    
    #Histograma
    h = numpy.zeros((600,256,3))
    bins = numpy.arange(256).reshape(256,1)
    hist_item = cv2.calcHist([Blur],[0],None,[256],[0,256])
    hist=numpy.int32(numpy.around(hist_item))
    pts = numpy.column_stack((bins,hist))
    cv2.polylines(h,[pts],False,(255,255,255))
    h=numpy.flipud(h)
    
    ret,bGBlur = cv2.threshold(GBlur,umbral,255,cv2.THRESH_BINARY)
    ret,bBlur = cv2.threshold(Blur,umbral,255,cv2.THRESH_BINARY)
    
    #Se muestran la imágenes con sus respectivos procesamientos
    cv2.imshow('Histograma Grises',h)
    cv2.imshow('Grises',gray)
    cv2.imshow('Binario',binario)
    cv2.imshow('GBlur',GBlur)
    cv2.imshow('blur',Blur)
    cv2.imshow('MBlur',MBlur)
    cv2.imshow('bGBlur',bGBlur)
    cv2.imshow('bBlur',bBlur)
    if cv2.waitKey(33) & 0xFF == ord('q'):break
