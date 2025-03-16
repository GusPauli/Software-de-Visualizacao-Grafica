from math import sqrt
from numpy import matmul
from math import *
from numba import njit
from utils import XYZ, RGB


def print_vet(inp):
    for i, row in enumerate(inp):
        for j, point in enumerate(row):
            if hasattr(point, 'x'):  # Check if the point has the expected attributes
                print(f"inp[{i}][{j}]: x = {point.x}, y = {point.y}, z = {point.z}")
            else:
                print(f"inp[{i}][{j}]: Unexpected data type - {point}")

def Traslacao(x,y,z):
    matrix_trans = [[1,0,0,x],
                    [0,1,0,y],
                    [0,0,1,z],
                    [0,0,0,1]]
    
    return matrix_trans

def Escala(fator):
    matrix_Escala = [[fator,0,0,0],
                     [0,fator,0,0],
                     [0,0,fator,0],
                     [0, 0, 0, 1]]
    
    return matrix_Escala

def Rotacao_em_x(grau):
    matrix_rotacao = [[1,0,0,0],
                      [0,cos(grau),-sin(grau),0],
                      [0,sin(grau),cos(grau),0],
                      [0,0,0,1]]

    return matrix_rotacao

def rotacao_em_y(grau):
    matrix_rotacao = [[cos(grau),0,sin(grau),0],
                      [0,1,0,0],
                      [-sin(grau), 0, cos(grau),0],
                      [0,0,0,1]]
    
    return matrix_rotacao
def rotacao_em_z(grau):
    matrix_rotacao = [[cos(grau),-sin(grau),0,0],
                      [sin(grau),cos(grau),0,0],
                      [0,0,1,0],
                      [0,0,0,1]]
    
    return matrix_rotacao

def normalize(v):
    module = (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5  # Cálculo do módulo
    if module == 0:
        return [0.0, 0.0, 0.0]  # Retorna o vetor nulo se o módulo for zero
    normalized = [v[0]/module, v[1]/module, v[2]/module]  # Normaliza o vetor
    return normalized

def dot(A, B):  #A * B = float
    return A[0]*B[0] + A[1]*B[1] + A[2]*B[2]

def cross(A, B): #A x B = vector
    return [A[1]*B[2] - A[2]*B[1],
            A[2]*B[0] - A[0]*B[2],
            A[0]*B[1] - A[1]*B[0]]    


def camera_transf_mat(vrp, p, Y): #Transformaçao SRU -> SRC
    translation_matrix = [[1, 0, 0, -vrp[0]],
                          [0, 1, 0, -vrp[1]],
                          [0, 0, 1, -vrp[2]],
                          [0, 0, 0,     1  ]]

    # Transformação de camera
    N = [(vrp[0] - p[0]), (vrp[1] - p[1]), (vrp[2] - p[2])] # N = VRP-P
    N = normalize(N)

    Y_x_n = dot(Y, N)
    V = [(Y[0] - (Y_x_n * N[0])),  # V = Y - (Y * N) * N #escrever toda a equação como generica para ser possivel mudar vetor Y
         (Y[1] - (Y_x_n * N[1])),
         (Y[2] - (Y_x_n * N[2]))]
    V = normalize(V)

    U = cross(V, N) # U = V x N (Como V e N são normalizados, U também é normalizado)

    # Verifica se os vetores são nulos antes de normalizar
    if all(component == 0 for component in N):
        N = [0.0001, 0.0001, 0.0001]
    if all(component == 0 for component in V):
        V = [0.0001, 0.0001, 0.0001]
    if all(component == 0 for component in U):
        U = [0.0001, 0.0001, 0.0001]

    # Matriz de transformação de camera
    transf_matrix= [[U[0], U[1], U[2],  0],
                    [V[0], V[1], V[2],  0],
                    [N[0], N[1], N[2],  0],
                    [  0 ,   0 ,   0 ,  1] ]
    return matmul(transf_matrix, translation_matrix)

def camera_viewport_mat(Xmin, Ymin, Xmax, Ymax, umin, vmin, umax, vmax): #Transformaçao SRC -> SRT



    return [[ (umax-umin)/(2*Xmax),   0  ,   0  ,Xmax*((umax-umin)/(2*Xmax))+umin],
            [   0  ,(vmin-vmax)/(Ymax-Ymin),   0  , Ymin*((vmax-vmin)/(Ymax-Ymin))+vmax],
            [   0  ,   0  ,   1  ,       0          ],
            [   0  ,   0  ,   0  ,       1          ] ]
    

def pipeline(projpers, inp, outp, vrp, p, dp, Y, Xmin, Ymin, Xmax, Ymax, umin, vmin, umax, vmax):
    # Calcular a matriz de transformação de câmera
    camera_transf = camera_transf_mat(vrp, p, Y)
    
    # Configurar a matriz de projeção
    if projpers:  # Projeção perspectiva
        camera_pers = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, -1/dp, 0]
        ]
        camera_transf = matmul(camera_pers, camera_transf)
    else:  # Projeção axonométrica
        camera_axo = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        camera_transf = matmul(camera_axo, camera_transf)
    
    # Calcular a matriz final de transformação
    viewport_matrix = camera_viewport_mat(Xmin, Ymin, Xmax, Ymax, umin, vmin, umax, vmax)
    viewp_mat = matmul(viewport_matrix, camera_transf)
    
    # Função para processar uma matriz de objetos XYZ
    def process_matrix(matrix):
        transformed_points = []
        for i, row in enumerate(matrix):
            row_points = []
            for j, point in enumerate(row):
                # Verificar se é um objeto XYZ
                if hasattr(point, 'x') and hasattr(point, 'y') and hasattr(point, 'z'):
                    # Transformar o ponto
                    x = viewp_mat[0][0] * point.x + viewp_mat[0][1] * point.y + viewp_mat[0][2] * point.z + viewp_mat[0][3] * 1
                    y = viewp_mat[1][0] * point.x + viewp_mat[1][1] * point.y + viewp_mat[1][2] * point.z + viewp_mat[1][3] * 1
                    z = viewp_mat[2][0] * point.x + viewp_mat[2][1] * point.y + viewp_mat[2][2] * point.z + viewp_mat[2][3] * 1
                    # Arredondar para valores inteiros
                    row_points.append(XYZ(x, y, z))
                else:
                    print(f"Warning: Point at [{i}][{j}] is not an XYZ object")
            transformed_points.append(row_points)
        return transformed_points
    
    # Processar as matrizes de entrada e saída
    inp_transformed = process_matrix(inp)
    outp_transformed = process_matrix(outp)
    
    return inp_transformed, outp_transformed