import dearpygui.dearpygui as dpg
from superfice import *
from pipeline import *
from config import *

#vetor para armazenar superficies
superficies = []
superfices_tela = []
inp = []
outp = []
att_inp = []
index=0

def att_vrp():
    CAMERA.VRP[0] = dpg.get_value("vrp_x")
    CAMERA.VRP[1] = dpg.get_value("vrp_y")
    CAMERA.VRP[2] = dpg.get_value("vrp_z")

def att_fonte_luz():
    a =0

def print_vet(vet):
    for i, row in enumerate(vet):
        for j, point in enumerate(row):
            print(f"inp[{i}][{j}]: x = {point.x}, y = {point.y}, z = {point.z}")
    

def surface_callback():
    # Obtém os valores dos widgets de entrada
    NI = dpg.get_value("input_NI")
    NJ = dpg.get_value("input_NJ")
    TI = dpg.get_value("input_TI")
    TJ = dpg.get_value("input_TJ")
    RESOLUTIONI = dpg.get_value("input_ResolutionI")
    RESOLUTIONJ = dpg.get_value("input_ResolutionJ")

    # Chama a função para gerar a superfície
    inp, outp = generate_spline_surface(NI, NJ, TI, TJ, RESOLUTIONI, RESOLUTIONJ)
    #print_vet(inp)
    superficies.append((inp,outp))
    #aplica o pipeline
    result_tuple = pipeline(DESENHO.PERS, superficies[0][0],superficies[0][1], CAMERA.VRP, CAMERA.p, CAMERA.dp, CAMERA.Y, 0, -WINDOW.HEIGHT,
                    WINDOW.WIDTH, WINDOW.HEIGHT, DESENHO.VP_min[0], DESENHO.VP_min[1], DESENHO.VP_max[0], DESENHO.VP_max[1])
    
    print_vet(superfices_tela[0][0])

def translada():
    # Obtém os valores das caixas de entrada
    x = dpg.get_value("translada_x")
    y = dpg.get_value("translada_y")
    z = dpg.get_value("translada_z")

    trans = Traslacao(x,y,z)
    #att_inp = trans @ inp
     
    #aplica a translacao aos pontos decontrole e regenera a malha

def rotaciona(sender, app_data, user_data):
    #obtem o angulo
    grau = dpg.get_value("Grau")

    if user_data == "X":
        mat = Rotacao_em_x(grau)
        #aplica a translacao aos pontos decontrole e regenera a malha
    elif user_data =="Y":
        mat = rotacao_em_y(grau)
        #aplica a translacao aos pontos decontrole e regenera a malha
    elif user_data == "Z":
        mat = rotacao_em_z(grau)
        #aplica a translacao aos pontos decontrole e regenera a malha
    elif user_data == "E":
        mat = Escala(grau)
        #aplica a translacao aos pontos decontrole e regenera a malha
    

def limpa_tela():
    dpg.delete_item("viewport_back", children_only=True)

def desenha():
    dpg.draw_circle((400, 300), radius=5, color=(255, 0, 200), parent="viewport_back")

def reabrir_janela():
    dpg.show_item("janela_com_abas")

#---------------------------------COLOCAR FUNÇÕES DAQUI PARA CIMA---------------------------------------------
#-------------------------------------------------------------------------------------------------------------    
dpg.create_context()

# creating font and back viewport drawlists
with dpg.viewport_drawlist(front=False, tag="viewport_back"):
    #dpg.draw_circle((100, 100), 25, color=(255, 255, 255, 255))
    desenha()

dpg.add_viewport_drawlist(front=False, label="viewport_canva")

#dpg.draw_circle((200, 200), 25, color=(255, 255, 255, 255), parent="viewport_back")


with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback='')
        dpg.add_menu_item(label="Save As", callback='')

        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Setting 1", callback='', check=True)
            dpg.add_menu_item(label="Setting 2", callback='')

    dpg.add_menu_item(label="Help", callback='')

    with dpg.menu(label="Tela"):
        dpg.add_button(label="Limpar Tela", callback=limpa_tela)
        dpg.add_button(label="Abrir Janela", callback=reabrir_janela)

# Cria uma janela com abas
with dpg.window(label="Menu principal", width=320, height=400, tag="janela_com_abas"):
    # Cria uma barra de abas
    with dpg.tab_bar(tag="tab_bar"):
        with dpg.tab(label="Malha", tag="malha"):
            dpg.add_text("Criar malha")
            dpg.add_input_int(label="NI", tag = "input_NI", default_value=4)
            dpg.add_input_int(label="NJ", tag = "input_NJ", default_value=4)
            dpg.add_input_int(label="TI", tag = "input_TI", default_value=3)
            dpg.add_input_int(label="TJ", tag = "input_TJ", default_value=3)
            dpg.add_input_int(label="ResolutionI", tag = "Input_resI", default_value=10)
            dpg.add_input_int(label="ResolutionJ", tag = "Input_resJ", default_value=10)
            dpg.add_button(label="Criar malha", callback=surface_callback)

        with dpg.tab(label="Tela", tag="tab4"):
            dpg.add_text("Editar Window")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="Width", tag="width", default_value=WINDOW.HEIGHT, width=80)
                dpg.add_input_int(label="Height", tag="height", default_value=WINDOW.HEIGHT, width=80)
            dpg.add_button(label="Aplicar", callback=att_vrp)

        # Aba 2
        with dpg.tab(label="Transformações", tag="transf"):
            dpg.add_text("Editar posição da Câmera")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="vrp_x", default_value=CAMERA.VRP[0], width=80)
                dpg.add_input_int(label="Y", tag="vrp_y", default_value=CAMERA.VRP[1], width=80)
                dpg.add_input_int(label="Z", tag="vrp_z", default_value=CAMERA.VRP[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_vrp)
            dpg.add_separator()

            dpg.add_text("Editar posição do ponto focal")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="p_x", default_value=CAMERA.VRP[0], width=80)
                dpg.add_input_int(label="Y", tag="p_y", default_value=CAMERA.VRP[1], width=80)
                dpg.add_input_int(label="Z", tag="p_z", default_value=CAMERA.VRP[2], width=80)
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

        # Aba 3
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
                dpg.add_input_float(label="X", tag="ka_x", default_value=Fonte_Luz.Ka[0], width=80,format="%.1f")
                dpg.add_input_float(label="Y", tag="ka_y", default_value=Fonte_Luz.Ka[1], width=80,format="%.1f")
                dpg.add_input_float(label="Z", tag="ka_z", default_value=Fonte_Luz.Ka[2], width=80,format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ka")
            dpg.add_spacer()
            dpg.add_text("Editar kd")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="kd_x", default_value=Fonte_Luz.Kd[0], width=80,format="%.1f")
                dpg.add_input_float(label="Y", tag="kd_y", default_value=Fonte_Luz.Kd[1], width=80,format="%.1f")
                dpg.add_input_float(label="Z", tag="kd_z", default_value=Fonte_Luz.Kd[2], width=80,format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ka")
            dpg.add_spacer()
            dpg.add_text("Editar ks")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="ks_x", default_value=Fonte_Luz.Ks[0], width=80,format="%.1f")
                dpg.add_input_float(label="Y", tag="ks_y", default_value=Fonte_Luz.Ks[1], width=80,format="%.1f")
                dpg.add_input_float(label="Z", tag="ks_z", default_value=Fonte_Luz.Ks[2], width=80,format="%.1f")
            dpg.add_button(label="Aplicar", callback=att_fonte_luz, user_data="ks")

dpg.create_viewport(title='Custom Title', width=WINDOW.WIDTH, height=WINDOW.HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()