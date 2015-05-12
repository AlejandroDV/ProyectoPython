# coding=utf-8
__author__ = "alejandro"
__date__ = "$13-feb-2015 18:46:04$"

import numpy
import cv2
from Tkinter import *
import copy

import tkMessageBox
from matplotlib import pyplot as plt


img = cv2.imread('lineaLaserFallas.png',0)
imgO = img


Blur51 = cv2.medianBlur(img,5)
img=Blur51  
Blur52 = cv2.medianBlur(Blur51,5)

alto, largo = img.shape[:2]
sup,inf,der,iz = 0,0,0,0
v=[]

#Buscar la primera columna
for c in range(largo):
    if cv2.countNonZero(img[:,c])!=alto:
        iz=c
        break
#Buscar la última columna
for c in reversed(range(largo)):
    if cv2.countNonZero(img[:,c])!=alto:
        der=c
        break

#Buscar la primera fila
for f in range(alto):
    if cv2.countNonZero(img[f,:])!=largo:
        sup=f
        break
#Buscar la ultima fila
for f in reversed(range(alto)):
    if cv2.countNonZero(img[f,:])!=largo:
        inf=f
        break

print "Izquierdo = ", iz
print "Derecho = ", der
print "Superior = ", sup
print "Inferior = ", inf

imagen=copy.copy(img[sup:inf,iz:der])
flaco=copy.copy(imagen)
alto, largo = imagen.shape[:2]
print alto
for c in range(largo):
    blancos = cv2.countNonZero(imagen[:,c])
    negros = alto-blancos
    inicial = 0
    for f in range(alto):
        if imagen[f,c]==0:
            inicial=f
        if inicial!=0: break
    print c, negros, "Inicial: ",inicial
    if inicial==0:
        flaco[alto-2,c]=0
    else:
        for i in range(inicial+1,alto,1):
            flaco[i,c]=255
while True:
    
    cv2.imshow('Linea',imgO)
    cv2.imshow('Filtrada',imagen)
    cv2.imshow('Flaco',flaco)
    if cv2.waitKey(33) & 0xFF == ord('q'):break    
