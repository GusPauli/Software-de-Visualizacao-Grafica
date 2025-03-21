import dearpygui.dearpygui as dpg
from superfice import *
from shading import *
from pipeline import *
from config import *
from numpy import matmul
from buffer import *

# Vetor para armazenar superfícies
superficies = []
index, px,py = 0,0,0
ponto_atual = []
NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ, grau= None, None, None, None, None, None, None

def salvar_arquivo():
    # Abre o diálogo de salvar arquivo
    dpg.add_file_dialog(
        label="Salvar Configuração",
        default_filename="configuracao.txt",
        callback=callback_salvar_arquivo,
        show=True,
        modal=True,
        width=500,
        height=400
    )

def carregar_arquivo():
    # Abre o diálogo de abrir arquivo
    dpg.add_file_dialog(
        label="Abrir Configuração",
        callback=callback_carregar_arquivo,
        show=True,
        modal=True,
        width=500,
        height=400,
        directory_selector=False,
        file_extensions="*.txt"     # Mostra apenas arquivos com a extensão .txt
    )

def callback_salvar_arquivo(sender, app_data):
    # Obtém o caminho do arquivo selecionado
    caminho_arquivo = app_data["file_path_name"]
    
    # Salva as configurações no arquivo
    with open(caminho_arquivo, "w") as arquivo:
        # Salvar configurações da câmera
        arquivo.write(f"VRP: {CAMERA.VRP}\n")
        arquivo.write(f"p: {CAMERA.p}\n")
        arquivo.write(f"dp: {CAMERA.dp}\n")
        arquivo.write(f"Y: {CAMERA.Y}\n")
        
        # Salvar configurações da janela
        arquivo.write(f"WINDOW_WIDTH: {WINDOW.WIDTH}\n")
        arquivo.write(f"WINDOW_HEIGHT: {WINDOW.HEIGHT}\n")
        
        # Salvar configurações do viewport
        arquivo.write(f"VP_MIN: {DESENHO.VP_min}\n")
        arquivo.write(f"VP_MAX: {DESENHO.VP_max}\n")
        
        # Salvar configurações das superfícies
        for i, superficie in enumerate(superficies):
            arquivo.write(f"Superficie_{i}_NI: {NI}\n")
            arquivo.write(f"Superficie_{i}_NJ: {NJ}\n")
            arquivo.write(f"Superficie_{i}_TI: {TI}\n")
            arquivo.write(f"Superficie_{i}_TJ: {TJ}\n")
            arquivo.write(f"Superficie_{i}_RESOLUTIONI: {RESOLUTIONI}\n")
            arquivo.write(f"Superficie_{i}_RESOLUTIONJ: {RESOLUTIONJ}\n")
            # Salvar pontos de controle como listas [x, y, z]
            control_points_serializados = []
            for linha in superficie.control_points:
                pontos_linha = []
                for ponto in linha:
                    pontos_linha.append([ponto.x, ponto.y, ponto.z])
                control_points_serializados.append(pontos_linha)
            arquivo.write(f"Superficie_{i}_CONTROL-POINTS: {control_points_serializados}\n")
        
        arquivo.write("FIM\n")
    
    print(f"Configurações salvas em: {caminho_arquivo}")

def callback_carregar_arquivo(sender, app_data):
    global NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ
    
    # Obtém o caminho do arquivo selecionado
    caminho_arquivo = app_data["file_path_name"]
    
    # Limpa a tela antes de carregar o novo arquivo
    limpa_tela()
    
    # Carrega as configurações do arquivo
    with open(caminho_arquivo, "r") as arquivo:
        lines = arquivo.readlines()
        for line in lines:
            line = line.strip()  # Remove espaços em branco no início e no final
            if line.startswith("VRP:"):
                CAMERA.VRP = eval(line.split(": ")[1])
            elif line.startswith("p:"):
                CAMERA.p = eval(line.split(": ")[1])
            elif line.startswith("dp:"):
                CAMERA.dp = eval(line.split(": ")[1])
            elif line.startswith("Y:"):
                CAMERA.Y = eval(line.split(": ")[1])
            elif line.startswith("WINDOW_WIDTH:"):
                WINDOW.WIDTH = int(line.split(": ")[1])
            elif line.startswith("WINDOW_HEIGHT:"):
                WINDOW.HEIGHT = int(line.split(": ")[1])
            elif line.startswith("VP_MIN:"):
                DESENHO.VP_min = eval(line.split(": ")[1])
            elif line.startswith("VP_MAX:"):
                DESENHO.VP_max = eval(line.split(": ")[1])
            elif line.startswith("Superficie_"):
                parts = line.split("_")
                if len(parts) >= 3:  # Verifica se há pelo menos três partes
                    index = int(parts[1])  # Índice da superfície
                    attribute_value = parts[2].split(": ")
                    if len(attribute_value) == 2:  # Verifica se há ": " na parte 2
                        attribute = attribute_value[0]  # Atributo (NI, NJ, TI, etc.)
                        value = attribute_value[1]  # Valor do atributo
                        # Atualiza os atributos da superfície
                        if attribute == "NI":
                            NI = int(value)
                        elif attribute == "NJ":
                            NJ = int(value)
                        elif attribute == "TI":
                            TI = int(value)
                        elif attribute == "TJ":
                            TJ = int(value)
                        elif attribute == "RESOLUTIONI":
                            RESOLUTIONI = int(value)
                        elif attribute == "RESOLUTIONJ":
                            RESOLUTIONJ = int(value)
                        elif attribute == "CONTROL-POINTS":
                            # Reconstruir os pontos de controle
                            control_points_serializados = eval(value)
                            control_points = []
                            for linha in control_points_serializados:
                                pontos_linha = []
                                for ponto in linha:
                                    # Criar objetos XYZ a partir das listas [x, y, z]
                                    pontos_linha.append(XYZ(ponto[0], ponto[1], ponto[2]))
                                control_points.append(pontos_linha)
                            nova_superficie = spline_surface(NI, NJ, TI, TJ, RESOLUTIONI, 
                                                             RESOLUTIONJ, 1111, control_points)
                            superficies.append(nova_superficie)
                    else:
                        print(f"Linha mal formatada: {line}")
                else:
                    print(f"Linha mal formatada: {line}")

        recalc()   
        desenha(superficies)
    
    print(f"Configurações carregadas de: {caminho_arquivo}")
#=======================================RECALCULA PONTOS NA TELA====================================================================
def recalc():
    # Recalcula os pontos da malha com base no novo VRP
    for superficie in superficies:
        superficie.control_points_tela, superficie.surface_points_tela = pipeline(
            DESENHO.PERS, superficie.control_points, superficie.surface_points, 
            CAMERA.VRP, CAMERA.p, CAMERA.dp, CAMERA.Y, 0, -WINDOW.HEIGHT,
            WINDOW.WIDTH, WINDOW.HEIGHT, DESENHO.VP_min[0], DESENHO.VP_min[1], 
            DESENHO.VP_max[0], DESENHO.VP_max[1]
        )
#=======================================ATUALIZA PONTOS DE CONTROLE E ====================================================================
#==============================================RECALCULA TUDO ====================================================================
def att_inp(mat, index):
    """
    Aplica uma transformação (mat) à superfície no índice especificado.

    Parâmetros:
        mat (list): Matriz de transformação 4x4.
        index (int): Índice da superfície a ser transformada.
    """
    # Verifica se o índice é válido
    if index < 0 or index >= len(superficies):
        print(f"Erro: Índice {index} fora dos limites da lista de superfícies.")
        return

    # Obtém a superfície no índice especificado
    superficie = superficies[index]
    # Converte os pontos de controle para coordenadas homogêneas
    pontos_homogeneos = []
    for linha in superficie.control_points:
        pontos_linha = []
        for ponto in linha:
            # Adiciona a coordenada homogênea (1)
            pontos_linha.append([ponto.x, ponto.y, ponto.z, 1])
        pontos_homogeneos.append(pontos_linha)
    
    # Aplica a transformação a cada ponto
    pontos_transformados = []
    for linha in pontos_homogeneos:
        pontos_linha = []
        for ponto in linha:
            ponto_transformado = matmul(mat, ponto)
            # Remove a coordenada homogênea e converte de volta para XYZ
            pontos_linha.append(XYZ(ponto_transformado[0], ponto_transformado[1], ponto_transformado[2]))
        pontos_transformados.append(pontos_linha)
    
    # Atualiza os pontos de controle da superfície
    superficies[index].control_points = pontos_transformados

    # Recalcula o centroide da superfície
    superficies[index].centroide = superficie.calcular_centroide()

    # Cria uma nova superfície com os pontos de controle atualizados
    nova_superficie = spline_surface(NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ, 1111, superficies[index].control_points)

    superficies[index].surface_points = nova_superficie.surface_points

    superficies[index].lista_faces = processa_malha(superficies[index].surface_points)

    # Recalcula a visibilidade das faces
    superficies[index].visible_points, superficies[index].visible_faces, superficies[index].faces = visibility(superficies[index], CAMERA.VRP)

    # Recalcula os pontos da malha com base nos novos pontos de controle
    recalc()
#====================================ATUALIZA PARAMETROS DA CAMERA E TELA=======================================================================
def att_tela(sender, app_data, user_data):
    if user_data == "vrp":
        # Atualiza o VRP da câmera
        CAMERA.VRP[0] = dpg.get_value("vrp_x")
        CAMERA.VRP[1] = dpg.get_value("vrp_y")
        CAMERA.VRP[2] = dpg.get_value("vrp_z")
        
        recalc()
        desenha(superficies)

    elif user_data == "window":
        WINDOW.WIDTH = dpg.get_value("width")
        WINDOW.HEIGHT = dpg.get_value("height")
        dpg.configure_item("desenho", width=WINDOW.WIDTH, height=WINDOW.HEIGHT)
        dpg.configure_viewport("primary",width=WINDOW.WIDTH, height=WINDOW.HEIGHT)
        recalc()
        desenha(superficies)

    elif user_data == "vp":
        DESENHO.VP_min = [dpg.get_value("umin"),dpg.get_value("vmin")]
        DESENHO.VP_max = [dpg.get_value("umax"),dpg.get_value("vmax")]
        dpg.configure_item("main_drawlist", width=DESENHO.VP_max[0], height=DESENHO.VP_max[1])
        recalc()
        desenha(superficies)
#========================================ATUALIZA PARAMETROS DA LUZ E PINTA===================================================================
def att_fonte_luz(sender, app_data, user_data):
    # Verifica se user_data é "C", "G" ou "P"
    if user_data in ("C", "G", "P"):
        # Atualiza os atributos de Fonte_Luz
        Fonte_Luz.pos = XYZ(float(dpg.get_value("pos_x")), float(dpg.get_value("pos_y")), float(dpg.get_value("pos_z")))
        Fonte_Luz.ila = RGB(float(dpg.get_value("la_x")), float(dpg.get_value("la_y")), float(dpg.get_value("la_z")))
        Fonte_Luz.il = RGB(float(dpg.get_value("il_x")), float(dpg.get_value("il_y")), float(dpg.get_value("il_z")))
        Fonte_Luz.Ka = [dpg.get_value("ka_x"), dpg.get_value("ka_y"), dpg.get_value("ka_z")]
        Fonte_Luz.Kd = [dpg.get_value("kd_x"), dpg.get_value("kd_y"), dpg.get_value("kd_z")]
        Fonte_Luz.Ks = [dpg.get_value("ks_x"), dpg.get_value("ks_y"), dpg.get_value("ks_z")]
        Fonte_Luz.n = int(dpg.get_value("n"))

        # Implementa a lógica específica para cada valor de user_data
        if user_data == "C":
            superficies[index].pinta_constante()
        elif user_data == "G":
            print("Modo Gouraud selecionado.")
            superficies[index].pinta_gouraud()
        elif user_data == "P":
            print("Modo Phong selecionado.")
    else:
        print("Erro: user_data inválido.")
#========================================================================================================================
#===============================================FUNÇÃO AUXILIAR============================================================
#========================================================================================================================
def print_vet(inp):
    for i, row in enumerate(inp):
        for j, point in enumerate(row):
            if hasattr(point, 'x'):  # Verifica se o ponto tem os atributos esperados
                print(f"inp[{i}][{j}]: x = {point.x}, y = {point.y}, z = {point.z}")
            else:
                print(f"inp[{i}][{j}]: Tipo de dado inesperado - {point}")
#========================================================================================================================               
#=======================================CALLBACK DE TRANSLAÇÃO====================================================================
#========================================================================================================================
def translada():
    # Obtém os valores de translação dos inputs
    x = dpg.get_value("translada_x")
    y = dpg.get_value("translada_y")
    z = dpg.get_value("translada_z")
    
    # Cria a matriz de translação
    trans = Traslacao(x, y, z)
    
    att_inp(trans, index)
    # Redesenha a malha
    desenha(superficies)
#========================================================================================================================
#========================================CALLBACK PARA ROTACIONAR E ESCALAR===================================================================
#========================================================================================================================
def rotaciona(sender, app_data, user_data):
    global grau, index

    type = user_data
    
    grau = dpg.get_value("grau")
    if type == "X":
        mat = Rotacao_em_x(grau)
    elif type == "Y":
        mat = rotacao_em_y(grau)
    elif type == "Z":
        mat = rotacao_em_z(grau)
    elif type == "E":
        if grau != 0.0:
            mat = Escala(grau)

    x,y,z = superficies[index].centroide
    trans = Traslacao(-x,-y,-z)
    att_inp(trans, index)
    att_inp(mat, index)
    trans=Traslacao(x,y,z)
    att_inp(trans, index)
    # Redesenha a malha
    # Mantém o estado de pintura
    desenha(superficies)
#========================================================================================================================
#========================================CALLBACK PARA CRIAR SUPERFICIES===================================================================
#========================================================================================================================
def surface_callback():
    global NI, NJ, TI,TJ, RESOLUTIONI, RESOLUTIONJ
    NI = dpg.get_value("input_NI")
    NJ = dpg.get_value("input_NJ")
    TI = dpg.get_value("input_TI")
    TJ = dpg.get_value("input_TJ")
    RESOLUTIONI = dpg.get_value("input_ResolutionI")
    RESOLUTIONJ = dpg.get_value("input_ResolutionJ")

    superficies.append(spline_surface(NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ))

    desenha(superficies)  # Renderiza a superfície na tela
#========================================================================================================================
#========================================================================================================================
def limpa_tela():
    global superficies
    dpg.delete_item("main_drawlist", children_only=True)
    superficies.clear()
#========================================================================================================================
#========================================================================================================================  
def desenha(listas):
    dpg.delete_item("main_drawlist", children_only=True)
    for superficie in listas:
        superficie.desenha_wireframe()
        if superficie.PINTADO:
            #superficie.pinta_constante()
            superficie.pinta_gouraud()
            #pintar_constante(superficie.lista_faces_tela,superficie.lista_faces,"main_drawlist")
#========================================================================================================================
#========================================================================================================================
def reabrir_janela(user_data):
    if user_data == "menu":
        dpg.show_item("janela_com_abas")
    else:
        dpg.show_item("desenho")
#========================================================================================================================
#================================CALLBACKS PARA SELEÇÃO DE OBJETO===============================================================
#========================================================================================================================
def callback_select(sender, app_data):
    global index
    
    # Obtém as coordenadas do clique
    mouse_pos= dpg.get_mouse_pos()

    # Verifica se o clique está dentro de alguma superfície
    for i, superficie in enumerate(superficies):
        box = calcular_bounding_box(superficie.control_points_tela)
        if ponto_dentro_bounding_box(mouse_pos, box, limiar=5):
            index = i

def calcular_bounding_box(malha):
    """
    Calcula a bounding box da malha.
    
    Parâmetros:
        malha (list): Lista de linhas, onde cada linha é uma lista de pontos.
    
    Retorna:
        tuple: (x_min, y_min, x_max, y_max)
    """
    # Inicializa com valores extremos
    x_min = float('inf')
    y_min = float('inf')
    x_max = float('-inf')
    y_max = float('-inf')

    # Itera sobre todas as linhas e pontos da malha
    for linha in malha:
        for ponto in linha:
            x = ponto.x
            y = ponto.y
            if x < x_min:
                x_min = x
            if y < y_min:
                y_min = y
            if x > x_max:
                x_max = x
            if y > y_max:
                y_max = y

    return (x_min, y_min, x_max, y_max)

def ponto_dentro_bounding_box(ponto, bounding_box, limiar=0):
    """
    Verifica se um ponto está dentro da bounding box.
    
    Parâmetros:
        ponto (tuple): Coordenadas (x, y) do ponto.
        bounding_box (tuple): (x_min, y_min, x_max, y_max).
        limiar (float): Margem de tolerância para considerar pontos próximos à borda.
    
    Retorna:
        bool: True se o ponto está dentro da bounding box, False caso contrário.
    """
    x = ponto[0]
    y = ponto[1]
    x_min, y_min, x_max, y_max = bounding_box

    # Expande a bounding box com o limiar
    x_min -= limiar
    y_min -= limiar
    x_max += limiar
    y_max += limiar

    return (x_min <= x <= x_max) and (y_min <= y <= y_max)

#========================================================================================================================
#================================CALLBACKS PARA SELEÇÃO DE PONTOS===============================================================
#========================================================================================================================
def callback_select_ponto(sender, app_data):
    global px, py, index
    
    mouse_pos = dpg.get_mouse_pos()

    if not superficies:
        return

    # Verifica se o clique está dentro de algum ponto de controle
    if index is not None:
        malha = superficies[index]
        for i, pontos in enumerate(malha.control_points_tela):
            for j, ponto in enumerate(pontos):
                x = ponto.x
                y = ponto.y
                    
                # Calcula a distância entre o ponto de controle e o clique
                distancia = ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) ** 0.5
                    
                # Se a distância for menor que um limiar, considera que o ponto foi clicado
                if distancia < 20:
                    index = index
                    px = i
                    py = j

                    # Atualiza os sliders com as coordenadas do ponto selecionado
                    dpg.set_value("xslider", int(x))
                    dpg.set_value("yslider", int(y))
                    dpg.set_value("zslider", int(x))
                    return
#========================================================================================================================
#================================CALLBACKS SLIDERS===============================================================
#========================================================================================================================
def slider_callback(sender,app_data, user_data):
    pass           