# coding=utf-8
__author__ = 'Alejandro'

import cv2
from Tkinter import *
import tkMessageBox
import numpy as np
import tkFileDialog
import cv2.cv as cv
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from ttk import *
from numpy import genfromtxt
import os

imagen_binarizada = cv2.imread('D:\\012-0_binario.png', 0)
cv2.imshow('Imagen', imagen_binarizada)
print imagen_binarizada
cv2.waitKey(0)
alto, largo = imagen_binarizada.shape[:2]
ret, imagen_binarizada_invertida = cv2.threshold(imagen_binarizada, 200, 255, cv2.THRESH_BINARY_INV)
cv2.imshow('Imagen Invertida', imagen_binarizada_invertida)
cv2.waitKey(0)
contours, hierarchy = cv2.findContours(imagen_binarizada_invertida, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print contours, hierarchy
cv2.drawContours(imagen_binarizada_invertida, contours, 1, (255, 255, 255), 1)
cv2.imshow('Imagen Invertida', imagen_binarizada_invertida)
cv2.waitKey(0)

