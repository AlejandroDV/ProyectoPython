# coding=utf-8
__author__ = "alejandro"
__date__ = "$13-feb-2015 18:46:04$"

import numpy
import cv2
camara = cv2.VideoCapture(0)

while True:   
    img = cv2.imread('D:\lineaLaserInvertida.png',0)
    imgO = img
    cv2.imshow('Linea',imgO)
    
    Blur51 = cv2.medianBlur(img,5)
    Blur52 = cv2.medianBlur(Blur51,5)
    img=Blur52
    
    #Determina el tamaño de la matriz img
    size = numpy.size(img)
    
    #Se crea una nueva matriz con la forma del 1er parámtro lleno de 0
    skelB = numpy.zeros(img.shape,numpy.uint8)
    
    #se crea un kernel de 3x3 con una forma de cruz
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    
    #se utilizará como control de calidad
    done = False

    while( not done):
        #Se erosionará la imágen con el kernel de 3x3 cruz
        erodedB = cv2.erode(img,element)
        cv2.imshow('Erode',erodedB)        
        #Se dilatará la imágen erosionada usando el mismo kernel
        temp = cv2.dilate(erodedB,element)
        cv2.imshow('Dilate',temp)    

        #Se calcula la diferencia entre la imágen original y el resultado de la dilataci'on
        temp2 = cv2.subtract(img,temp)
        cv2.imshow('Subtract',temp2) 

        skelB = cv2.bitwise_or(skelB,temp2)
        cv2.imshow('bitwise_or',skelB) 

        img = erodedB.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros==size:
            done = True        
    if cv2.waitKey(33) & 0xFF == ord('q'):break
    
    

