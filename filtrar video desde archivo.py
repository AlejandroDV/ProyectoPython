import numpy as np
import cv2
import cv2.cv as cv

cap = cv2.VideoCapture('D:/FACULTAD/Tesis/Aplicaciones/ProyectoPython/prueban50.avi')
print cap
f=0
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter("filtrado.avi", fourcc, 20.0, (640, 480))
separador = 2
while(cap.isOpened()):
    ret, frame = cap.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if f % separador == 0:
        print f
        out.write(frame)
    cv2.imshow('frame',frame)
    f+=1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
