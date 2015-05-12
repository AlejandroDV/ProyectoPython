# coding=utf-8
#Algoritmo para graficar una mira sobre la imagen capturada de una camara
#Se dibuja una mira de color sobre la imagen a fin de poder calibrar:
# 1- La cámara
# 2- La proyección láser
 
import cv2
import numpy as np
 
#Iniciamos la camara
captura = cv2.VideoCapture(0)
 
while(1):
     
    #Capturamos una imagen
    _, imagen = captura.read()
    
    #Se Dibujará una linea vertical centrada en el frame de la camara
    #Linea Vertical
    cv2.line(imagen, (imagen.shape[1]/2,0) , (imagen.shape[1]/2,imagen.shape[0]) , (255,0,0) , 0)
    #Kinea Horizontal
    cv2.line(imagen, (0,imagen.shape[0]/2) , (imagen.shape[1],imagen.shape[0]/2) , (255,0,0) , 0)
    
    #Mostramos la imagen original con la marca del centro
    cv2.imshow('Camara', imagen)
    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27:
        break
 
cv2.destroyAllWindows()
