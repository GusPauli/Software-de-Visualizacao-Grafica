import pygame
from utils import XYZ, RGB

class WINDOW: # Definições da janela
    WIDTH = 800
    HEIGHT = 600
    BACKGROUND = (255, 255, 255)

# Definições do desenho
class DESENHO:
    VP_min = [0, 0]
    VP_max = [WINDOW.WIDTH-1, WINDOW.HEIGHT-1]

    PERS = False  #Projeção perspectiva?
    HIDE_FACES = False #Esconder faces?
    SOMBREAMENTO = 0 #0 = SEM SOMBREAMENTO, 1 = CONSTANTE, 2 = GOURAUD
    WIREFRAME = 1

# Definições do botão
class BUTTON:
    WIDTH = 100
    HEIGHT = 30
    MARGIN = 10
    COLLOR = (200, 200, 200)

class TEXT:
    COLLOR = (0, 0, 0)

class TEXT_BOX:
    color = ('lightskyblue3')


class CAMERA:
    VRP = [0,0, 100]
    p = [0,0,0]
    dp = 1000
    Y = [0, 1, 0]


class Fonte_Luz:
    pos = XYZ(300, 300, 1200) #posicao da fonte de luz
    ila = RGB(60, 40, 50) #luz ambiente
    il = RGB(200, 200, 210) #intensidade da fonte de luz
    #material
    Ka = [0.3, 0.6, 0.4]
    Kd = [0.3, 0.6, 0.8] #fator luz difusa
    Ks = [0.3, 0.6, 0.8] #fator luz especular
    n = 3