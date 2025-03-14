import random
import dearpygui.dearpygui as dpg
from pipeline import pipeline
from config import *
from typing import List, Tuple
from visibilidade import *

# Definição da estrutura XYZ (equivalente à struct XYZ em C)
class XYZ:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

def desenha_pontos(matriz_pontos, matriz_pontos_originais=None, pontos_visiveis=None, raio = None,cor_pontos=(255, 255, 255), mostrar_indices=False):
    for i, linha in enumerate(matriz_pontos):
        for j, ponto in enumerate(linha):
            x, y, z = ponto  # Assumindo que cada ponto é [x, y, z]
            
            # Verificar se o ponto é visível (caso fornecido)
            visivel = True
            if matriz_pontos_originais is not None and pontos_visiveis is not None:
                ponto_original = matriz_pontos_originais[i][j]
                if ponto_original not in pontos_visiveis:
                    visivel = False
                    continue  # Pular este ponto se não estiver na lista de visíveis
        
            dpg.draw_circle([x, y], radius=3, color=cor_pontos, fill=cor_pontos, parent="main_drawlist")
            
            # Mostrar índice do ponto se necessário
            if mostrar_indices and visivel:
                # Encontrar o índice na lista de pontos visíveis
                if matriz_pontos_originais is not None and pontos_visiveis is not None:
                    ponto_original = matriz_pontos_originais[i][j]
                    try:
                        idx = pontos_visiveis.index(ponto_original)
                        dpg.draw_text([x+2, y+2], f"VP:{idx}", color=cor_pontos, parent="main_drawlist")
                    except ValueError:
                        pass  # Se não encontrado em visible_points, não faz nada

def desenha_malha(matriz_pontos, matriz_pontos_originais=None, pontos_visiveis=None, cor_linha_visivel=(0, 0, 255), cor_linha_invisivel=(255, 0, 0)):
    num_linhas = len(matriz_pontos)
    if num_linhas == 0:
        return
    num_colunas = len(matriz_pontos[0])
    
    # Desenhar linhas horizontais
    for i in range(num_linhas):
        for j in range(num_colunas - 1):
            x1, y1, _ = matriz_pontos[i][j]
            x2, y2, _ = matriz_pontos[i][j + 1]
            
            # Definir a cor da linha com base na visibilidade dos pontos
            cor_linha = cor_linha_visivel  # Assume que é visível por padrão
            
            if matriz_pontos_originais is not None and pontos_visiveis is not None:
                ponto1_original = matriz_pontos_originais[i][j]
                ponto2_original = matriz_pontos_originais[i][j+1]
                
                # Verificar se ambos os pontos são visíveis
                if ponto1_original not in pontos_visiveis or ponto2_original not in pontos_visiveis:
                    cor_linha = cor_linha_invisivel  # Pelo menos um ponto não é visível
            
            # Desenhar a linha com a cor apropriada
            dpg.draw_line([x1, y1], [x2, y2], color=cor_linha, thickness=1, parent="main_drawlist")
    
    # Desenhar linhas verticais
    for j in range(num_colunas):
        for i in range(num_linhas - 1):
            x1, y1, _ = matriz_pontos[i][j]
            x2, y2, _ = matriz_pontos[i + 1][j]
            
            # Definir a cor da linha com base na visibilidade dos pontos
            cor_linha = cor_linha_visivel  # Assume que é visível por padrão
            
            if matriz_pontos_originais is not None and pontos_visiveis is not None:
                ponto1_original = matriz_pontos_originais[i][j]
                ponto2_original = matriz_pontos_originais[i+1][j]
                
                # Verificar se ambos os pontos são visíveis
                if ponto1_original not in pontos_visiveis or ponto2_original not in pontos_visiveis:
                    cor_linha = cor_linha_invisivel  # Pelo menos um ponto não é visível
            
            # Desenhar a linha com a cor apropriada
            dpg.draw_line([x1, y1], [x2, y2], color=cor_linha, thickness=1, parent="main_drawlist")

class spline_surface:
    def __init__(self, NI: int, NJ: int, TI: int, TJ: int, RESOLUTIONI: int, RESOLUTIONJ: int, seed: int = 1111, inp: List[List[XYZ]] = None):
        # Função para calcular os nós da spline
        def spline_knots(knots: List[int], n: int, t: int):
            """
            Calcula os nós (knots) da spline.

            Parâmetros:
                knots: Lista para armazenar os nós.
                n: Número de pontos de controle.
                t: Grau da spline.
            """
            for i in range(n + t + 1):
                if i < t:
                    knots[i] = 0
                elif i <= n:
                    knots[i] = i - t + 1
                else:
                    knots[i] = n - t + 2

        # Função para calcular o blend da spline
        def spline_blend(k: int, t: int, knots: List[int], interval: float) -> float:
            """
            Calcula o blend da spline.

            Parâmetros:
                k: Índice do nó.
                t: Grau da spline.
                knots: Lista de nós.
                interval: Intervalo atual.

            Retorna:
                O valor do blend no intervalo especificado.
            """
            if t == 1:
                return 1.0 if knots[k] <= interval < knots[k + 1] else 0.0
            else:
                value = 0.0
                if knots[k + t - 1] != knots[k]:
                    value += (interval - knots[k]) / (knots[k + t - 1] - knots[k]) * spline_blend(k, t - 1, knots, interval)
                if knots[k + t] != knots[k + 1]:
                    value += (knots[k + t] - interval) / (knots[k + t] - knots[k + 1]) * spline_blend(k + 1, t - 1, knots, interval)
                return value
        
        """
        Gera uma superfície de spline com base nos parâmetros fornecidos.

        Parâmetros:
            NI, NJ: Número de pontos de controle nas direções I e J.
            TI, TJ: Grau da spline nas direções I e J.
            RESOLUTIONI, RESOLUTIONJ: Resolução da superfície nas direções I e J.
            seed: Semente para a geração de números aleatórios.
            inp: Pontos de controle fornecidos (opcional). Se None, os pontos serão gerados.

        Retorna:
            Uma tupla contendo:
            - inp: Pontos de controle (lista de listas de XYZ).
            - outp: Superfície gerada (lista de listas de XYZ).
        """
        # Verifica se os parâmetros são válidos
        # Garantir que nenhum parâmetro seja None
        NI = 3 if NI is None else NI
        NJ = 3 if NJ is None else NJ
        TI = 3 if TI is None else TI
        TJ = 3 if TJ is None else TJ
        RESOLUTIONI = 10 if RESOLUTIONI is None else RESOLUTIONI
        RESOLUTIONJ = 10 if RESOLUTIONJ is None else RESOLUTIONJ

        # Se inp não for fornecido, criar os pontos de controle
        if inp is None:
            inp = [[XYZ(0, 0, 0) for _ in range(NJ + 1)] for _ in range(NI + 1)]
            random.seed(seed)
            for i in range(NI + 1):
                for j in range(NJ + 1):
                    inp[i][j].x = i * 100
                    inp[i][j].y = j * 100
                    inp[i][j].z = random.randint(0, 400)

        # Arrays para armazenar a superfície gerada
        outp: List[List[XYZ]] = [[XYZ(0, 0, 0) for _ in range(RESOLUTIONJ)] for _ in range(RESOLUTIONI)]

        # Arrays para armazenar os nós (knots) da spline
        knotsI: List[int] = [0] * (NI + TI + 1)
        knotsJ: List[int] = [0] * (NJ + TJ + 1)

        # Tamanho do passo ao longo da curva
        incrementI = (NI - TI + 2) / (RESOLUTIONI - 1)
        incrementJ = (NJ - TJ + 2) / (RESOLUTIONJ - 1)

        # Calcula os nós da spline
        spline_knots(knotsI, NI, TI)
        spline_knots(knotsJ, NJ, TJ)

        # Calcula a superfície de spline
        intervalI = 0.0
        for i in range(RESOLUTIONI - 1):
            intervalJ = 0.0
            for j in range(RESOLUTIONJ - 1):
                outp[i][j].x = 0.0
                outp[i][j].y = 0.0
                outp[i][j].z = 0.0
                for ki in range(NI + 1):
                    for kj in range(NJ + 1):
                        bi = spline_blend(ki, TI, knotsI, intervalI)
                        bj = spline_blend(kj, TJ, knotsJ, intervalJ)
                        outp[i][j].x += inp[ki][kj].x * bi * bj
                        outp[i][j].y += inp[ki][kj].y * bi * bj
                        outp[i][j].z += inp[ki][kj].z * bi * bj
                intervalJ += incrementJ
            intervalI += incrementI

        # Preenche os pontos finais
        intervalI = 0.0
        for i in range(RESOLUTIONI - 1):
            outp[i][RESOLUTIONJ - 1].x = 0.0
            outp[i][RESOLUTIONJ - 1].y = 0.0
            outp[i][RESOLUTIONJ - 1].z = 0.0
            for ki in range(NI + 1):
                bi = spline_blend(ki, TI, knotsI, intervalI)
                outp[i][RESOLUTIONJ - 1].x += inp[ki][NJ].x * bi
                outp[i][RESOLUTIONJ - 1].y += inp[ki][NJ].y * bi
                outp[i][RESOLUTIONJ - 1].z += inp[ki][NJ].z * bi
            intervalI += incrementI
        outp[RESOLUTIONI - 1][RESOLUTIONJ - 1] = inp[NI][NJ]

        intervalJ = 0.0
        for j in range(RESOLUTIONJ - 1):
            outp[RESOLUTIONI - 1][j].x = 0.0
            outp[RESOLUTIONI - 1][j].y = 0.0
            outp[RESOLUTIONI - 1][j].z = 0.0
            for kj in range(NJ + 1):
                bj = spline_blend(kj, TJ, knotsJ, intervalJ)
                outp[RESOLUTIONI - 1][j].x += inp[NI][kj].x * bj
                outp[RESOLUTIONI - 1][j].y += inp[NI][kj].y * bj
                outp[RESOLUTIONI - 1][j].z += inp[NI][kj].z * bj
            intervalJ += incrementJ
        outp[RESOLUTIONI - 1][RESOLUTIONJ - 1] = inp[NI][NJ]

        # Pontos de controle e malha em SRU
        self.control_points = inp
        self.surface_points = outp

        # Pontos de controle e malha em SRC
        self.control_points_tela, self.surface_points_tela = pipeline(DESENHO.PERS, inp, outp, CAMERA.VRP, CAMERA.p, CAMERA.dp, CAMERA.Y, 0, -WINDOW.HEIGHT,
                                WINDOW.WIDTH, WINDOW.HEIGHT, DESENHO.VP_min[0], DESENHO.VP_min[1], DESENHO.VP_max[0], DESENHO.VP_max[1])

        self.visible_points, self.visible_faces, self.faces = visibility(self.surface_points, CAMERA.VRP)


    def desenha_wireframe(self):
        desenha_pontos(self.control_points_tela,cor_pontos=(255, 0, 0))  # Desenha pontos de controle em vermelho

        desenha_malha(self.surface_points_tela, matriz_pontos_originais=self.surface_points, 
                      pontos_visiveis=self.visible_points, cor_linha_visivel=(0, 0, 255), cor_linha_invisivel=(255, 0, 0) 
                                                                                           # Azul para arestas visíveis 
                                                                                           # Vermelho para arestas não visíveis
        )
        # Desenha apenas os pontos visíveis da superfície em verde
        desenha_pontos(self.surface_points_tela, matriz_pontos_originais=self.surface_points, 
                        pontos_visiveis=self.visible_points, cor_pontos=(0, 255, 0)) #desenha pontos da malha de verde