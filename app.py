import dearpygui.dearpygui as dpg
from superfice import *
from shading import *
from pipeline import *
from config import *
from numpy import matmul
from callbacks import *

# Configuração inicial do Dear PyGui
dpg.create_context()

# Criar um tema personalizado com fundo branco
with dpg.theme(tag="tema_fundo_branco"):
    with dpg.theme_component():
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (210, 210, 210), category=dpg.mvThemeCat_Core)

# Cria uma área de desenho
with dpg.window(label="Janela de Desenho", width=WINDOW.WIDTH, height=WINDOW.HEIGHT, tag="desenho"):
    dpg.add_drawlist(width=DESENHO.VP_max[0], height=DESENHO.VP_max[1], tag="main_drawlist")

# Cria um handler registry para a janela
    with dpg.handler_registry(tag="handler_registry"):
        # Adiciona o handler de clique do mouse ao handler registry
        dpg.add_mouse_click_handler(callback=callback_select)
        dpg.add_mouse_click_handler(callback=callback_select_ponto)

with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback=salvar_arquivo)
        dpg.add_menu_item(label="Load", callback=carregar_arquivo)

        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Setting 1", callback='', check=True)
            dpg.add_menu_item(label="Setting 2", callback='')

    with dpg.menu(label="Tela"):
        dpg.add_button(label="Limpar tela", callback=limpa_tela, user_data="limpa")
        dpg.add_button(label="Abrir Menu", callback=reabrir_janela, user_data="menu")
        dpg.add_button(label="Abrir tela de Desenho", callback=reabrir_janela)

# Cria a janela com abas
with dpg.window(label="Menu principal", width=WINDOW.WIDTH*0.3, height=WINDOW.HEIGHT/2, tag="janela_com_abas"):
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
            dpg.add_separator()
            dpg.add_text("Mover ponto Selecionado")
            # Caixas de entrada para x, y, z
            dpg.add_input_int(label="X", tag="xinput", default_value=0, min_value=DESENHO.VP_min[0], max_value=DESENHO.VP_max[0], min_clamped=True, max_clamped=True)
            dpg.add_input_int(label="Y", tag="yinput", default_value=0, min_value=DESENHO.VP_min[1], max_value=DESENHO.VP_max[1], min_clamped=True, max_clamped=True)
            dpg.add_input_int(label="Z", tag="zinput", default_value=0, min_value=DESENHO.VP_min[0], max_value=DESENHO.VP_max[0], min_clamped=True, max_clamped=True)
            
            # Botão de confirmação
            dpg.add_button(label="Confirmar", callback=confirm_callback)    
            
        with dpg.tab(label="Tela", tag="tab4"):
            dpg.add_text("Editar Window")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="Width", tag="width", default_value=WINDOW.WIDTH, width=80)
                dpg.add_input_int(label="Height", tag="height", default_value=WINDOW.HEIGHT, width=80)
            dpg.add_button(label="Aplicar", callback=att_tela, user_data="window")
            dpg.add_separator()

            dpg.add_text("Editar VP")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="Umin", tag="umin", default_value=DESENHO.VP_min[0], width=80)
                dpg.add_input_int(label="Vmin", tag="vmin", default_value=DESENHO.VP_min[1], width=80)
            with dpg.group(horizontal=True):   
                dpg.add_input_int(label="Umax", tag="umax", default_value=DESENHO.VP_max[0], width=80)
                dpg.add_input_int(label="Vmax", tag="vmax", default_value=DESENHO.VP_max[1], width=80)
            dpg.add_button(label="Aplicar", callback=att_tela, user_data="vp")
            dpg.add_separator()

        with dpg.tab(label="Transformações", tag="transf"):
            dpg.add_text("Editar posição da Câmera")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="vrp_x", default_value=CAMERA.VRP[0], width=80)
                dpg.add_input_int(label="Y", tag="vrp_y", default_value=CAMERA.VRP[1], width=80)
                dpg.add_input_int(label="Z", tag="vrp_z", default_value=CAMERA.VRP[2], width=80)
            dpg.add_button(label="Aplicar", callback=att_tela, user_data="vrp")
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
                dpg.add_input_int(label="X", tag="pos_x", default_value=Fonte_Luz.pos.x, width=80)
                dpg.add_input_int(label="Y", tag="pos_y", default_value=Fonte_Luz.pos.y, width=80)
                dpg.add_input_int(label="Z", tag="pos_z", default_value=Fonte_Luz.pos.z, width=80)
            dpg.add_separator()

            dpg.add_text("Editar Intensidade da Luz Ambiente")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="la_x", default_value=Fonte_Luz.ila.red, width=80)
                dpg.add_input_int(label="Y", tag="la_y", default_value=Fonte_Luz.ila.green, width=80)
                dpg.add_input_int(label="Z", tag="la_z", default_value=Fonte_Luz.ila.blue, width=80)
            dpg.add_separator()

            dpg.add_text("Editar Intensidade da Fonte de Luz")
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="X", tag="il_x", default_value=Fonte_Luz.il.red, width=80)
                dpg.add_input_int(label="Y", tag="il_y", default_value=Fonte_Luz.il.green, width=80)
                dpg.add_input_int(label="Z", tag="il_z", default_value=Fonte_Luz.il.blue, width=80)
            dpg.add_separator()

            dpg.add_text("Editar ka")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="ka_x", default_value=Fonte_Luz.Ka[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="ka_y", default_value=Fonte_Luz.Ka[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="ka_z", default_value=Fonte_Luz.Ka[2], width=80, format="%.1f")
            dpg.add_spacer()
            dpg.add_text("Editar kd")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="kd_x", default_value=Fonte_Luz.Kd[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="kd_y", default_value=Fonte_Luz.Kd[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="kd_z", default_value=Fonte_Luz.Kd[2], width=80, format="%.1f")
            dpg.add_spacer()
            dpg.add_text("Editar ks")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label="X", tag="ks_x", default_value=Fonte_Luz.Ks[0], width=80, format="%.1f")
                dpg.add_input_float(label="Y", tag="ks_y", default_value=Fonte_Luz.Ks[1], width=80, format="%.1f")
                dpg.add_input_float(label="Z", tag="ks_z", default_value=Fonte_Luz.Ks[2], width=80, format="%.1f")
            dpg.add_text("Sombreamento")
            dpg.add_input_int(label="N", tag="n", default_value=Fonte_Luz.n, width=80)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Constante", callback=att_fonte_luz, user_data="C")
                dpg.add_button(label="Gouraud", callback=att_fonte_luz, user_data="G")
                dpg.add_button(label="Phong", callback=att_fonte_luz, user_data="P")

# Aplicar o tema à janela
dpg.bind_item_theme("desenho", "tema_fundo_branco")
dpg.set_primary_window("desenho", True)
# Configuração da viewport
dpg.create_viewport(title='Custom Title', width=WINDOW.WIDTH, height=WINDOW.HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()