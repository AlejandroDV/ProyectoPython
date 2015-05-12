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
    v=[]
    contador=[]
    for c in range(1,640,1):
        v=binario[:,c]
        contador.append(480-cv2.countNonZero(v))
        v=[]
    print contador

    cv2.imshow('Binario',binario)
    if cv2.waitKey(33) & 0xFF == ord('q'):break
print "**********************"
media=0.0
varianza=0.0
desviacion=0.0

print "Máximo: ", max(contador)
print "Mínimo: ", min(contador)

#cálculo de media
media=sum(contador)/len(contador)
print "Media: ",media

#cálculo de la varianza
for i in contador:
    dif=(i-media)**2
    varianza=varianza+dif
varianza=varianza/len(contador)

print "Varianza: ",varianza

desviacion=varianza**0.5

print "Desviación: ",desviacion
