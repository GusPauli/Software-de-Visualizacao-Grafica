import dearpygui.dearpygui as dpg
from superfice import *
from shading import *
from pipeline import *
from config import *
from numpy import matmul

# Vetor para armazenar superfícies
superficies = []
index = 0
NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ, grau= None, None, None, None, None, None, None

def recalc():
    # Recalcula os pontos da malha com base no novo VRP
    for superficie in superficies:
        superficie.control_points_tela, superficie.surface_points_tela = pipeline(
            DESENHO.PERS, superficie.control_points, superficie.surface_points, 
            CAMERA.VRP, CAMERA.p, CAMERA.dp, CAMERA.Y, 0, -WINDOW.HEIGHT,
            WINDOW.WIDTH, WINDOW.HEIGHT, DESENHO.VP_min[0], DESENHO.VP_min[1], 
            DESENHO.VP_max[0], DESENHO.VP_max[1]
        )

def att_inp(mat):
    # Aplica a translação a cada superfície
    for superficie in superficies:
        # Converte os pontos de controle para coordenadas homogêneas
        pontos_homogeneos = []
        for linha in superficie.control_points:
            pontos_linha = []
            for ponto in linha:
                # Adiciona a coordenada homogênea (1)
                pontos_linha.append([ponto.x, ponto.y, ponto.z, 1])
            pontos_homogeneos.append(pontos_linha)
        
        # Aplica a translação a cada ponto
        pontos_transformados = []
        for linha in pontos_homogeneos:
            pontos_linha = []
            for ponto in linha:
                #print(ponto)
                ponto_transformado = matmul(mat, ponto)
                # Remove a coordenada homogênea e converte de volta para XYZ
                pontos_linha.append(XYZ(ponto_transformado[0], ponto_transformado[1], ponto_transformado[2]))
            pontos_transformados.append(pontos_linha)
        
        # Atualiza os pontos de controle da superfície
        inp = pontos_transformados

        # Cria uma nova superfície com os pontos de controle atualizados
        nova_superficie = spline_surface(NI, NJ, TI,TJ, RESOLUTIONI, RESOLUTIONJ,1111,inp)

        # Remove a superfície antiga da lista (se necessário)
        if superficies:
            superficies.pop()

        # Adiciona a nova superfície à lista
        superficies.append(nova_superficie)
        
        recalc()


def att_vrp():
    # Atualiza o VRP da câmera
    CAMERA.VRP[0] = dpg.get_value("vrp_x")
    CAMERA.VRP[1] = dpg.get_value("vrp_y")
    CAMERA.VRP[2] = dpg.get_value("vrp_z")
    
    # Recalcula os pontos da malha com base no novo VRP
    recalc()    
    # Redesenha a malha
    desenha(superficies)

def att_fonte_luz():
    pass  # Implemente conforme necessário

def print_vet(inp):
    for i, row in enumerate(inp):
        for j, point in enumerate(row):
            if hasattr(point, 'x'):  # Verifica se o ponto tem os atributos esperados
                print(f"inp[{i}][{j}]: x = {point.x}, y = {point.y}, z = {point.z}")
            else:
                print(f"inp[{i}][{j}]: Tipo de dado inesperado - {point}")

def translada():
    # Obtém os valores de translação dos inputs
    x = dpg.get_value("translada_x")
    y = dpg.get_value("translada_y")
    z = dpg.get_value("translada_z")
    
    # Cria a matriz de translação
    trans = Traslacao(x, y, z)
    
    att_inp(trans)

    # Redesenha a malha
    desenha(superficies)

def rotaciona(sender, app_data, user_data):
    global grau
    
    grau = dpg.get_value("grau")
    print(grau)
    if user_data == "X":
        mat = Rotacao_em_x(grau)
    elif user_data == "Y":
        mat = rotacao_em_y(grau)
    elif user_data == "Z":
        mat = rotacao_em_z(grau)
    elif user_data == "E":
        mat = Escala(grau)

    for superficie in superficies:
        x,y,z = superficie.centroide
        print(mat)
        trans = Traslacao(-x,-y,-z)
        att_inp(trans)
        att_inp(mat)
        trans=Traslacao(x,y,z)
        att_inp(trans)
        # Redesenha a malha
    desenha(superficies)


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

def limpa_tela(user_data):
    global superficies
    dpg.delete_item("main_drawlist", children_only=True)
    superficies.clear()

def desenha(listas):
    dpg.delete_item("main_drawlist", children_only=True)
    for superficie in listas:
        superficie.desenha_wireframe()

def reabrir_janela(user_data):
    if user_data == "menu":
        dpg.show_item("janela_com_abas")
    else:
        dpg.show_item("desenho")

# Configuração inicial do Dear PyGui
dpg.create_context()

# Cria uma área de desenho
with dpg.window(label="Janela de Desenho", width=WINDOW.WIDTH, height=WINDOW.HEIGHT, tag="desenho"):
    dpg.add_drawlist(width=WINDOW.WIDTH, height=WINDOW.HEIGHT, tag="main_drawlist")

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback='')
        dpg.add_menu_item(label="Save As", callback='')

        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Setting 1", callback='', check=True)
            dpg.add_menu_item(label="Setting 2", callback='')

    dpg.add_menu_item(label="Help", callback='')

    with dpg.menu(label="Tela"):
        dpg.add_button(label="Limpar tela", callback=limpa_tela, user_data="limpa")
        dpg.add_button(label="Abrir Menu", callback=reabrir_janela, user_data="menu")
        dpg.add_button(label="Abrir tela de Desenho", callback=reabrir_janela)

# Cria a janela com abas
with dpg.window(label="Menu principal", width=320, height=400, tag="janela_com_abas"):
    with dpg.tab_bar(tag="tab_bar"):
        with dpg.tab(label="Malha", tag="malha"):
            dpg.add_text("Criar malha")
            dpg.add_input_int(label="NI", tag="input_NI", default_value=4)
            dpg.add_input_int(label="NJ", tag="input_NJ", default_value=4)
            dpg.add_input_int(label="TI", tag="input_TI", default_value=3)
            dpg.add_input_int(label="TJ", tag="input_TJ", default_value=3)
            dpg.add_input_int(label="ResolutionI", tag="input_ResolutionI", default_value=10)
            dpg.add_input_int(label="ResolutionJ", tag="input_ResolutionJ", default_value=10)
            dpg.add_button(label="Criar malha", callback=surface_callback)

        with dpg.tab(label="Tela", tag="tab4"):
            dpg.add_text("Editar Window")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="Width", tag="width", default_value=WINDOW.HEIGHT, width=80)
                dpg.add_input_int(label="Height", tag="height", default_value=WINDOW.HEIGHT, width=80)
            dpg.add_button(label="Aplicar", callback='')

        with dpg.tab(label="Transformações", tag="transf"):
            dpg.add_text("Editar posição da Câmera")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="vrp_x", default_value=CAMERA.VRP[0], width=80)
                dpg.add_input_int(label="Y", tag="vrp_y", default_value=CAMERA.VRP[1], width=80)
                dpg.add_input_int(label="Z", tag="vrp_z", default_value=CAMERA.VRP[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_vrp)
            dpg.add_separator()

            dpg.add_text("Aplicar Translação")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="translada_x", default_value=0, width=80)
                dpg.add_input_int(label="Y", tag="translada_y", default_value=0, width=80)
                dpg.add_input_int(label="Z", tag="translada_z", default_value=0, width=80)
            dpg.add_button(label="Aplicar", callback=translada)
            dpg.add_separator()

            dpg.add_text("Aplicar Rotação ou Escala")
            dpg.add_input_float(label="Grau", tag="grau", default_value=0.0)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Escala", callback=rotaciona, user_data="E")
                dpg.add_button(label="Rotação X", callback=rotaciona, user_data="X")
                dpg.add_button(label="Rotação Y", callback=rotaciona, user_data="Y")
                dpg.add_button(label="Rotação Z", callback=rotaciona, user_data="Z")

        with dpg.tab(label="Elementos da Luz", tag="tab3"):
            dpg.add_text("Editar Posição da Fonte de Luz")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="pos_x", default_value=Fonte_Luz.pos[0], width=80)
                dpg.add_input_int(label="Y", tag="pos_y", default_value=Fonte_Luz.pos[1], width=80)
                dpg.add_input_int(label="Z", tag="pos_z", default_value=Fonte_Luz.pos[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="pos_luz")
            dpg.add_separator()

            dpg.add_text("Editar Intensidade da Luz Ambiente")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="la_x", default_value=Fonte_Luz.ila[0], width=80)
                dpg.add_input_int(label="Y", tag="la_y", default_value=Fonte_Luz.ila[1], width=80)
                dpg.add_input_int(label="Z", tag="la_z", default_value=Fonte_Luz.ila[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="la")
            dpg.add_separator()

            dpg.add_text("Editar Intensidade da Fonte de Luz")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="il_x", default_value=Fonte_Luz.il[0], width=80)
                dpg.add_input_int(label="Y", tag="il_y", default_value=Fonte_Luz.il[1], width=80)
                dpg.add_input_int(label="Z", tag="il_z", default_value=Fonte_Luz.il[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="il")
            dpg.add_separator()

            dpg.add_text("Editar ka")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="ka_x", default_value=Fonte_Luz.Ka[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="ka_y", default_value=Fonte_Luz.Ka[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="ka_z", default_value=Fonte_Luz.Ka[2], width=80, format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ka")
            dpg.add_spacer()
            dpg.add_text("Editar kd")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="kd_x", default_value=Fonte_Luz.Kd[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="kd_y", default_value=Fonte_Luz.Kd[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="kd_z", default_value=Fonte_Luz.Kd[2], width=80, format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ka")
            dpg.add_spacer()
            dpg.add_text("Editar ks")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="ks_x", default_value=Fonte_Luz.Ks[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="ks_y", default_value=Fonte_Luz.Ks[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="ks_z", default_value=Fonte_Luz.Ks[2], width=80, format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ks")

# Configuração da viewport
dpg.create_viewport(title='Custom Title', width=WINDOW.WIDTH, height=WINDOW.HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()