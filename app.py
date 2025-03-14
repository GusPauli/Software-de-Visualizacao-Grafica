import dearpygui.dearpygui as dpg
from superfice import *
from pipeline import *
from config import *

# Vetor para armazenar superfícies
superficies = []
superfices_tela = []
inp = []
outp = []
att_inp = []
index = 0

def att_vrp():
    CAMERA.VRP[0] = dpg.get_value("vrp_x")
    CAMERA.VRP[1] = dpg.get_value("vrp_y")
    CAMERA.VRP[2] = dpg.get_value("vrp_z")

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
    x = dpg.get_value("translada_x")
    y = dpg.get_value("translada_y")
    z = dpg.get_value("translada_z")
    trans = Traslacao(x, y, z)
    # Aplica a translação aos pontos de controle e regenera a malha

def rotaciona(sender, app_data, user_data):
    grau = dpg.get_value("Grau")
    if user_data == "X":
        mat = Rotacao_em_x(grau)
    elif user_data == "Y":
        mat = rotacao_em_y(grau)
    elif user_data == "Z":
        mat = rotacao_em_z(grau)
    elif user_data == "E":
        mat = Escala(grau)
    # Aplica a transformação aos pontos de controle e regenera a malha

def surface_callback():
    NI = dpg.get_value("input_NI")
    NJ = dpg.get_value("input_NJ")
    TI = dpg.get_value("input_TI")
    TJ = dpg.get_value("input_TJ")
    RESOLUTIONI = dpg.get_value("input_ResolutionI")
    RESOLUTIONJ = dpg.get_value("input_ResolutionJ")

    superficies.append(spline_surface(NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ))
    new_inp, new_outp = pipeline(DESENHO.PERS, superficies[0].control_points, superficies[0].surface_points, CAMERA.VRP, CAMERA.p, CAMERA.dp, CAMERA.Y, 0, -WINDOW.HEIGHT,
                                WINDOW.WIDTH, WINDOW.HEIGHT, DESENHO.VP_min[0], DESENHO.VP_min[1], DESENHO.VP_max[0], DESENHO.VP_max[1])
    superfices_tela.append((new_inp, new_outp))
    desenha(superfices_tela)  # Renderiza a superfície na tela

def limpa_tela():
    dpg.delete_item("main_drawlist", children_only=True)

def desenha(listas):
    limpa_tela()  # Limpa a tela antes de desenhar
    for superficie in listas:
        pontos_controle, pontos_superficie = superficie
        desenha_pontos(pontos_controle, cor_pontos=(255, 0, 0))  # Desenha pontos de controle em vermelho
        desenha_malha(pontos_superficie, cor_linha=(0, 0, 255))  # Desenha malha em azul
        desenha_pontos(pontos_superficie, cor_pontos=(0, 255, 0))  # Desenha pontos da superfície em verde

def desenha_pontos(matriz_pontos, cor_pontos=(255, 255, 255)):
    for linha in matriz_pontos:
        for ponto in linha:
            x, y, z = ponto  # Assumindo que cada ponto é [x, y, z]
            dpg.draw_circle([x, y], radius=1, color=cor_pontos, fill=cor_pontos, parent="main_drawlist")

def desenha_malha(matriz_pontos, cor_linha=(255, 255, 255)):
    num_linhas = len(matriz_pontos)
    if num_linhas == 0:
        return
    num_colunas = len(matriz_pontos[0])
    for i in range(num_linhas):
        for j in range(num_colunas - 1):
            x1, y1, _ = matriz_pontos[i][j]
            x2, y2, _ = matriz_pontos[i][j + 1]
            dpg.draw_line([x1, y1], [x2, y2], color=cor_linha, thickness=1, parent="main_drawlist")
    for j in range(num_colunas):
        for i in range(num_linhas - 1):
            x1, y1, _ = matriz_pontos[i][j]
            x2, y2, _ = matriz_pontos[i + 1][j]
            dpg.draw_line([x1, y1], [x2, y2], color=cor_linha, thickness=1, parent="main_drawlist")

def reabrir_janela():
    dpg.show_item("janela_com_abas")

# Configuração inicial do Dear PyGui
dpg.create_context()

# Cria uma área de desenho
with dpg.window(label="Janela de Desenho", width=WINDOW.WIDTH, height=WINDOW.HEIGHT):
    dpg.add_drawlist(width=WINDOW.WIDTH, height=WINDOW.HEIGHT, tag="main_drawlist")

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
            dpg.add_button(label="Aplicar", callback=att_vrp)

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