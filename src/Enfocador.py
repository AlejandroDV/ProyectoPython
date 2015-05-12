# coding=utf-8
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "alejandro"
__date__ = "$07-mar-2015 12:37:38$"
#AA
import numpy
import cv2
from Tkinter import *
import tkMessageBox



camara = cv2.VideoCapture(0)
    
def getUmbral():
    return sliderUmbral.get()
    
def setLblBlancos():
    lblBlancos.config(text = str(sliderUmbral.get()))

def lblText():
    respuesta=5
    
    return str(respuesta)

def enlazar():
    while True:
        ret,frame = camara.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret,binario = cv2.threshold(gray,getUmbral(),255,cv2.THRESH_BINARY)
        cv2.imshow('1 Color',frame)
        cv2.imshow('2 ByN',gray)
        cv2.imshow('3 Binario',binario)
        if cv2.waitKey(33) & 0xFF == ord('q'):break

vtnPrincipal = Tk()

#Valor a mostrar
lblBlancos = Label(vtnPrincipal)
lblBlancos.pack()

#Slider de Umbral
sliderUmbral = Scale(vtnPrincipal, from_=0, to=255,label="Umbral", orient=HORIZONTAL)
sliderUmbral.set(250)
sliderUmbral.pack()
#sliderUmbral.config(command=getUmbral())
    
btnEnlazar = Button(vtnPrincipal, text="Enlazar",command=enlazar)
btnEnlazar.pack()
vtnPrincipal.mainloop()



