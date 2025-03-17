from pipeline import normalize, cross, dot
from pygame import *
from buffer import Buffer
import dearpygui.dearpygui as dpg
from utils import XYZ, RGB
import numpy as np
from config import Fonte_Luz, CAMERA, WINDOW

def It_calc(Ia, Id, Is):
    IT = RGB(Ia.red+Id.red+Is.red, Ia.green+Id.green+Is.green, Ia.blue+Id.blue+Is.blue)

    if IT.red > 255:
        IT.red = 255
    elif IT.red < 0:
        IT.red = 0

    if IT.green > 255:
        IT.green = 255
    elif IT.green < 0:
        IT.green = 0

    if IT.blue > 255:
        IT.blue = 255
    elif IT.blue < 0:
        IT.blue = 0

    return IT

def somb_const(face, vrp, L, ila, il, ka, kd, ks, n):
    centroide = face.centroide
    N = face.vetor_normal #normal da face
    L_dir = normalize([L.x-centroide.x,  L.y-centroide.y,  L.z-centroide.z]) #vetor direção da luz 

    Ia = RGB(ila.red*ka[0], ila.green*ka[1], ila.blue*ka[2])

    n_dot_l = dot(N, L_dir)
    if n_dot_l < 0:
        it_face = It_calc(Ia, RGB(0, 0, 0), RGB(0, 0, 0)) #apenas iluminação ambiente p a face atual
        return it_face
    
    Id = RGB(il.red*kd[0]*n_dot_l,   il.green*kd[1]*n_dot_l,   il.blue*kd[2]*n_dot_l)
    
    aux =        [   2*n_dot_l*N[0],       2*n_dot_l*N[1],       2*n_dot_l*N[2]   ] 
    r = normalize([ aux[0]-L_dir[0],      aux[1]-L_dir[1],      aux[2]-L_dir[2]  ])
    s = normalize([vrp[0]-centroide.x,   vrp[1]-centroide.y,   vrp[2]-centroide.z])
    r_dot_s = dot(r, s)

    if r_dot_s < 0:
        it_face = It_calc(Ia, Id, RGB(0, 0, 0)) #apenas iluminação ambiente e difusa p a face atual
        return it_face
    
    aux = r_dot_s**n
    Is = RGB(il.red*ks[0]*aux,  il.green*ks[1]*aux,  il.blue*ks[2]*aux)

    it_face = It_calc(Ia, Id, Is)

    return it_face

def somb_gouraud(obj, faces, v_faces, vrp, L, ila, il, ka, kd, ks, n):

    vertices = [0 for i in range(len(obj))] #lista de faces em que cada vertice está contido

    f_normals = []
    for i in range(len(faces)): #para cada face
        aux = faces[i]
        for a in aux: #para cada vertice da face
            if vertices[a] == 0:
                vertices[a] = [i]  #adiciona a face na lista de faces do vertice
            else:
                vertices[a].append(i)
        f_normals.append(normalize()) #normal unitária de todas as faces

    marmota = [] #lista de vertices das faces visíveis
    for v_face in v_faces: #para cada face visível
        for i in v_face: #para cada vertice da face visível
            if i not in marmota:
                marmota.append(i) #adiciona o vertice na lista de vertices das faces visíveis

    for i in range(len(vertices)):
        if i not in marmota:
            vertices[i] = []    #vertices que não estão contidos em nenhuma face são zerados

    vnmu = [[] for i in range(len(obj))] #vetor normal médio unitário
    for i in range(len(vertices)):
        if vertices[i] != []:  #para cada vértice contido em alguma face visível
            v = [0, 0, 0]
            for j in vertices[i]:
                v = [v[0]+f_normals[j][0],  v[1]+f_normals[j][1],  v[2]+f_normals[j][2]] 
            vnmu[i] = (normalize(v)) #vetor normal médio unitário dos vertices das faces visíveis

    Ia = [ila[0]*ka[0],   ila[1]*ka[1],   ila[2]*ka[2]] #iluminação ambiente

    It_verts = []
    for i in range(len(vertices)):
        It_verts.append([])
        if vertices[i] != []:
            L_dir = normalize([L[0]-obj[i][0],  L[1]-obj[i][1],  L[2]-obj[i][2]]) #vetor direção da luz para vértice
            n_dot_l = dot(vnmu[i], L_dir)
            if n_dot_l < 0:
                It_verts[i] = (It_calc(Ia, [0,0,0], [0,0,0])) #apenas iluminação ambiente p o vértice atual
                continue
            else:
                Id = [il[0]*kd[0]*n_dot_l,   il[1]*kd[1]*n_dot_l,   il[2]*kd[2]*n_dot_l]
            
            r = normalize([2*n_dot_l*vnmu[i][0]-L_dir[0],  2*n_dot_l*vnmu[i][1]-L_dir[1],  2*n_dot_l*vnmu[i][2]-L_dir[2]])
            s = normalize([vrp[0]-obj[i][0],  vrp[1]-obj[i][1],  vrp[2]-obj[i][2]])

            r_dot_s = dot(r, s)
            if r_dot_s < 0:
                It_verts[i] = (It_calc(Ia, Id, [0, 0, 0])) #apenas iluminação ambiente e difusa p o vértice atual
                continue
            else:
                aux = r_dot_s**n
                Is = [il[0]*ks[0]*aux,  il[1]*ks[1]*aux,  il[2]*ks[2]*aux]
            It_verts[i] = (It_calc(Ia, Id, Is))
        
    return It_verts

def fillpoly_gouraud(screen, obj, It_vertices, v_faces, zbuffer, imgbuffer):

    for i in range(len(v_faces)):
        a,b,c,d = v_faces[i]
        corA = It_vertices[a]
        corB = It_vertices[b]
        corC = It_vertices[c]
        corD = It_vertices[d]
        
        #abc = triangulo1
        #acd = triangulo2
        cor = [corA, corB, corC]
        keys = [a, b, c]
        # Ordene as chaves com base no valor de y
        sorted_keys = sorted(keys, key=lambda k: obj[k][1])
        # Ordene o vetor vor de acordo com a nova ordem das chaves
        sorted_cor = [cor[keys.index(k)] for k in sorted_keys]
        # Objetos ordenados e vetor vor ordenado
        sorted_objects = [obj[k] for k in sorted_keys]

        fill_triangulo(screen, sorted_objects[0], sorted_objects[1], sorted_objects[2], sorted_cor, zbuffer, imgbuffer)


        cor = [corA, corC, corD]
        keys = [a, c, d]
        # Ordene as chaves com base no valor de y
        sorted_keys = sorted(keys, key=lambda k: obj[k][1])
        # Ordene o vetor vor de acordo com a nova ordem das chaves
        sorted_cor = [cor[keys.index(k)] for k in sorted_keys]
        # Objetos ordenados e vetor vor ordenado
        sorted_objects = [obj[k] for k in sorted_keys]
        
        fill_triangulo(screen, sorted_objects[0], sorted_objects[1], sorted_objects[2], sorted_cor,zbuffer, imgbuffer)



        ''' # Ordenar os pontos por y
        pontos_ordenados = sorted([obj[a], obj[b], obj[c], obj[d]], key=lambda ponto: ponto[1])

        # Dividir os pontos em duas metades
        metade_superior = pontos_ordenados[:2]
        metade_inferior = pontos_ordenados[2:]

        # Ordenar as metades por x
        metade_superior.sort(key=lambda ponto: ponto[0])
        metade_inferior.sort(key=lambda ponto: ponto[0])

        for y in range(round(metade_superior[0][1]), round(metade_inferior[1][1])):
            if y < metade_inferior[0][1]:
                x1 = metade_superior[0][0] + (metade_superior[1][0] - metade_superior[0][0]) * (y - metade_superior[0][1]) / (metade_superior[1][1] - metade_superior[0][1])
                x2 = metade_superior[0][0] + (metade_inferior[0][0] - metade_superior[0][0]) * (y - metade_superior[0][1]) / (metade_inferior[0][1] - metade_superior[0][1])
            else:
                x1 = metade_inferior[0][0] + (metade_inferior[1][0] - metade_inferior[0][0]) * (y - metade_inferior[0][1]) / (metade_inferior[1][1] - metade_inferior[0][1])
                x2 = metade_superior[1][0] + (metade_inferior[1][0] - metade_superior[1][0]) * (y - metade_superior[1][1]) / (metade_inferior[1][1] - metade_superior[1][1])

            for x in range(round(min(x1, x2)), round(max(x1, x2))):
                screen.set_at((x,y),cor_pixel)'''

def algoritmo_pintor(lista_faces_tela, lista_faces, tela):
    fillpoly(lista_faces_tela, lista_faces, tela, 0)

def pintar_constante(lista_faces_tela, lista_faces, tela):
    def scanline_calc(face): # Codigo de calculo das scanlines de forma incremental
        list_scanlines = []
        nv = len(face.vertices) # Numero de vertices
        y_max, y_min = 0, 99999
        for v in face.vertices:
            if v.y > y_max:
                y_max = v.y
            if v.y < y_min:
                y_min = v.y      
        y_max = int(y_max)
        y_min = int(y_min)      
        ns = y_max - y_min # Numero de scanlines

        for i in range(ns):
            scanline = []
            list_scanlines.append(scanline)

        for i in range(nv):
            x1, y1, z1 = int(face.vertices[i].x), int(face.vertices[i].y), int(face.vertices[i].z)
            x2, y2, z2 = int(face.vertices[(i+1)%nv].x), int(face.vertices[(i+1)%nv].y), int(face.vertices[(i+1)%nv].z)
            if y2 < y1:
                xa, ya, za = x2, y2, z2
                x2, y2, z2 = x1, y1, z1
                x1, y1, z1 = xa, ya, za
            y1, y2 = y1-y_min, y2-y_min
            xn = x1
            zn = z1
            if y1+y_min != y_max or y2+y_min != y_max:
                if x1 == x2 or y1 == y2:
                    tx = 0
                else:
                    tx = (x2-x1)/(y2-y1)
                if z1 == z2 or y1 == y2:
                    tz = 0
                else:
                    tz = (z2-z1)/(y2-y1)

                list_scanlines[y1].append((x1, z1))
                for c in range(y1+1, y2):
                    xn = xn+tx
                    zn = zn+tz
                    list_scanlines[c].append((int(xn), int(zn)))
        for sl in list_scanlines:
            sl.sort(key=lambda z: z[0])
        return list_scanlines, y_min, y_max
    
    # Preenche o buffer
    buffer = Buffer(WINDOW.WIDTH, WINDOW.HEIGHT)
    for i in range(len(lista_faces_tela)):
        cor = somb_const(lista_faces[i], CAMERA.VRP, Fonte_Luz.pos, Fonte_Luz.ila, Fonte_Luz.il, Fonte_Luz.Ka, Fonte_Luz.Kd, Fonte_Luz.Ks, Fonte_Luz.n)
        scanlines, y_min, y_max = scanline_calc(lista_faces_tela[i])
        for i, scanline in enumerate(scanlines):
            x1 = scanline[0][0]
            x2 = scanline[1][0]
            z1 = scanline[0][1]
            z2 = scanline[1][1]
            if z1 == z2 or x1 == x2:
                tz = 0
            else:
                tz = (z2-z1)/(x2-x1)
            zn = z1
            for j in range(x1, x2):
                buffer.test_and_set(j, i+y_min, zn, cor)
                zn += tz
    # Pinta a tela com base no buffer
    for i in range(WINDOW.WIDTH-1):
        #print()
        for j in range(WINDOW.HEIGHT-1):
            #print(i, j)
            #print(f"({buffer.image_buffer[i, j].red}, {buffer.image_buffer[i, j].green}, {buffer.image_buffer[i, j].blue})", end=" ")
            #print(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue)
            if (buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue) != WINDOW.BACKGROUND:
                dpg.draw_line((i, j), (i+1, j), color=(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue), thickness=1, parent=tela)
                
def pintar_gouraud(lista_faces_tela, lista_faces, RESOLUTIONI, RESOLUTIONJ, tela):
    def calc_luz_vertic(lista_faces_tela, lista_faces):
        lista_normal_vec = [RESOLUTIONI][RESOLUTIONJ]
        for vec in lista_normal_vec:
            vec = XYZ(0, 0, 0)
        i = 0
        j = 0
        for face in lista_faces:
            lista_normal_vec[i][j].x += face.vetor_normal.x
            lista_normal_vec[i][j].y += face.vetor_normal.y
            lista_normal_vec[i][j].z += face.vetor_normal.z
            lista_normal_vec[i+1][j].x += face.vetor_normal.x
            lista_normal_vec[i+1][j].y += face.vetor_normal.y
            lista_normal_vec[i+1][j].z += face.vetor_normal.z
            lista_normal_vec[i+1][j+1].x += face.vetor_normal.x
            lista_normal_vec[i+1][j+1].y += face.vetor_normal.y
            lista_normal_vec[i+1][j+1].z += face.vetor_normal.z
            lista_normal_vec[i][j+1].x += face.vetor_normal.x
            lista_normal_vec[i][j+1].y += face.vetor_normal.y
            lista_normal_vec[i][j+1].z += face.vetor_normal.z
            if j == RESOLUTIONJ-1:
                j = 0
                i += 1
        for vec in lista_normal_vec:
            module = np.sqrt(vec.x**2 + vec.y**2 + vec.z**2)
            vec.x = vec.x/module
            vec.y = vec.y/module
            vec.z = vec.z/module

    def scanline_calc(face): # Codigo de calculo das scanlines de forma incremental
        list_scanlines = []
        nv = len(face.vertices) # Numero de vertices
        y_max, y_min = 0, 99999
        for v in face.vertices:
            if v.y > y_max:
                y_max = v.y
            if v.y < y_min:
                y_min = v.y      
        y_max = int(y_max)
        y_min = int(y_min)      
        ns = y_max - y_min # Numero de scanlines

        for i in range(ns):
            scanline = []
            list_scanlines.append(scanline)

        for i in range(nv):
            x1, y1, z1 = int(face.vertices[i].x), int(face.vertices[i].y), int(face.vertices[i].z)
            x2, y2, z2 = int(face.vertices[(i+1)%nv].x), int(face.vertices[(i+1)%nv].y), int(face.vertices[(i+1)%nv].z)
            if y2 < y1:
                xa, ya, za = x2, y2, z2
                x2, y2, z2 = x1, y1, z1
                x1, y1, z1 = xa, ya, za
            y1, y2 = y1-y_min, y2-y_min
            xn = x1
            zn = z1
            if y1+y_min != y_max or y2+y_min != y_max:
                if x1 == x2 or y1 == y2:
                    tx = 0
                else:
                    tx = (x2-x1)/(y2-y1)
                if z1 == z2 or y1 == y2:
                    tz = 0
                else:
                    tz = (z2-z1)/(y2-y1)

                list_scanlines[y1].append((x1, z1))
                for c in range(y1+1, y2):
                    xn = xn+tx
                    zn = zn+tz
                    list_scanlines[c].append((int(xn), int(zn)))
        for sl in list_scanlines:
            sl.sort(key=lambda z: z[0])
        return list_scanlines, y_min, y_max
    
    # Preenche o buffer
    buffer = Buffer(WINDOW.WIDTH, WINDOW.HEIGHT)
    for i in range(len(lista_faces_tela)):
        cor = somb_const(lista_faces[i], CAMERA.VRP, Fonte_Luz.pos, Fonte_Luz.ila, Fonte_Luz.il, Fonte_Luz.Ka, Fonte_Luz.Kd, Fonte_Luz.Ks, Fonte_Luz.n)
        scanlines, y_min, y_max = scanline_calc(lista_faces_tela[i])
        for i, scanline in enumerate(scanlines):
            x1 = scanline[0][0]
            x2 = scanline[1][0]
            z1 = scanline[0][1]
            z2 = scanline[1][1]
            if z1 == z2 or x1 == x2:
                tz = 0
            else:
                tz = (z2-z1)/(x2-x1)
            zn = z1
            for j in range(x1, x2):
                buffer.test_and_set(j, i+y_min, zn, cor)
                zn += tz
    print("Zbuffer calculado")
    # Pinta a tela com base no buffer
    for i in range(WINDOW.WIDTH-1):
        #print()
        for j in range(WINDOW.HEIGHT-1):
            #print(i, j)
            #print(f"({buffer.image_buffer[i, j].red}, {buffer.image_buffer[i, j].green}, {buffer.image_buffer[i, j].blue})", end=" ")
            #print(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue)
            if (buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue) != WINDOW.BACKGROUND:
                dpg.draw_line((i, j), (i+1, j), color=(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue), thickness=1, parent=tela)

def fillpoly(lista_faces_tela, lista_faces, tela, shading=0, cor_fundo=RGB(0, 0, 0)): # Algoritmo fillpoly em si. Pega a lista de scanlines e preenche linha por linha
    def scanline_calc(face): # Codigo de calculo das scanlines de forma incremental
        list_scanlines = []
        nv = len(face.vertices) # Numero de vertices
        y_max, y_min = 0, 99999
        for v in face.vertices:
            if v.y > y_max:
                y_max = v.y
            if v.y < y_min:
                y_min = v.y      
        y_max = int(y_max)
        y_min = int(y_min)      
        ns = y_max - y_min # Numero de scanlines

        for i in range(ns):
            scanline = []
            list_scanlines.append(scanline)

        for i in range(nv):
            x1, y1 = int(face.vertices[i].x), int(face.vertices[i].y)
            x2, y2 = int(face.vertices[(i+1)%nv].x), int(face.vertices[(i+1)%nv].y)
            if y2 < y1:
                xa, ya = x2, y2
                x2, y2 = x1, y1
                x1, y1 = xa, ya
            y1, y2 = y1-y_min, y2-y_min
            xn = x1
            if y1+y_min != y_max or y2+y_min != y_max:
                if x1 == x2 or y1 == y2:
                    tx = 0
                else:
                    tx = (x2-x1)/(y2-y1)
                list_scanlines[y1].append(x1)
                for c in range(y1+1, y2):
                    xn = xn+tx
                    list_scanlines[c].append(int(xn))
        for sl in list_scanlines:
            sl.sort()
        return list_scanlines, y_min, y_max
    
    for i in range(len(lista_faces_tela)):
        scanlines, y_min, y_max = scanline_calc(lista_faces_tela[i])
        row = y_min

        # Fillpoly tradicional, usado para o wireframe. Pinta com uma cor solida definida (cor de fundo)
        if shading == 0: 
            for j in range(len(scanlines)):
                for i in range(0, len(scanlines[j])-1, 2):
                    dpg.draw_line([scanlines[j][i]+1, row], [scanlines[j][i+1], row], color=cor_fundo, thickness=1, parent=tela)
                row = row+1
        # Fillpoly com sombreamento constante com z-buffer
        """elif shading == 1: 
            cor = somb_const(lista_faces[i], CAMERA.VRP, Fonte_Luz.pos, Fonte_Luz.ila, Fonte_Luz.il, Fonte_Luz.Ka, Fonte_Luz.Kd, Fonte_Luz.Ks, Fonte_Luz.n)
            for sl in scanlines: # Percorre entre as scanlines
                for i in range(0, len(sl)-1, 2): # Percorre entre as interseccoes na scanline
                    x = sl[i]
                    for j in range(sl[i], sl[(i+1)%len(lista_faces_tela[i].vertices)]): # Percorre pelos pixels entre as interseccoes
                        
                row = row+1
            for sl in scanlines: # Percorre entre as scanlines
                for i in range(0, len(sl)-1, 2): # Percorre entre as interseccoes na scanline
                    x = sl[i]
                    for j in range(sl[i], sl[(i+1)%len(lista_faces_tela[i].vertices)]): # Percorre pelos pixels entre as interseccoes
                        dpg.draw_line([x, row], [x, row], color=cor, thickness=1, parent=tela)
                row = row+1
        # Fillpoly com sombreamento gouraud
        elif shading == 2: 
            for sl in scanlines:
                for i in range(0, len(sl)-1, 2):
                    dpg.draw_line([sl[i], row], [sl[i+1], row], color=cor_fundo, thickness=1, parent=tela)
                row = row+1"""
