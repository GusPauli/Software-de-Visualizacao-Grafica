from pipeline import normalize, cross, dot
from copy import deepcopy
from pygame import *
from buffer import Buffer
import dearpygui.dearpygui as dpg
from utils import XYZ, RGB
import numpy as np
from config import Fonte_Luz, CAMERA, WINDOW

def It_calc(L, N, vrp, ponto, ila, il, ka, kd, ks, n):
    def it_sum(Ia, Id, Is):
        IT = RGB(0, 0, 0)

        IT.red = Ia.red + Id.red + Is.red
        IT.green = Ia.green + Id.green + Is.green
        IT.blue = Ia.blue + Id.blue + Is.blue

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

    L_dir = normalize([L.x-ponto.x,  L.y-ponto.y,  L.z-ponto.z]) #vetor direção da luz 

    Ia = RGB(ila.red*ka[0], ila.green*ka[1], ila.blue*ka[2])

    n_dot_l = dot(N, L_dir)
    if n_dot_l < 0:
        it_face = it_sum(Ia, RGB(0, 0, 0), RGB(0, 0, 0)) #apenas iluminação ambiente p a face atual
        return it_face
    
    Id = RGB(il.red*kd[0]*n_dot_l,   il.green*kd[1]*n_dot_l,   il.blue*kd[2]*n_dot_l)
    
    aux =        [   2*n_dot_l*N[0],       2*n_dot_l*N[1],       2*n_dot_l*N[2]   ] 
    r = normalize([ aux[0]-L_dir[0],      aux[1]-L_dir[1],      aux[2]-L_dir[2]  ])
    s = normalize([vrp[0]-ponto.x,   vrp[1]-ponto.y,   vrp[2]-ponto.z])
    r_dot_s = dot(r, s)

    if r_dot_s < 0:
        it_face = it_sum(Ia, Id, RGB(0, 0, 0)) #apenas iluminação ambiente e difusa p a face atual
        return it_face
    
    aux = r_dot_s**n
    Is = RGB(il.red*ks[0]*aux,  il.green*ks[1]*aux,  il.blue*ks[2]*aux)
    IT = it_sum(Ia, Id, Is)

    return IT

def somb_const(face, vrp, L, ila, il, ka, kd, ks, n):
    centroide = face.centroide
    N = face.vetor_normal #normal da face

    it_face = It_calc(L, N, vrp, centroide, ila, il, ka, kd, ks, n)

    return it_face

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
        for j, scanline in enumerate(scanlines):
            x1 = scanline[0][0]
            x2 = scanline[1][0]
            z1 = scanline[0][1]
            z2 = scanline[1][1]
            if z1 == z2 or x1 == x2:
                tz = 0
            else:
                tz = (z2-z1)/(x2-x1)
            zn = z1
            for k in range(x1, x2):
                buffer.test_and_set(k, j+y_min, zn, cor)
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
    def calc_normal_vertic(lista_faces, RESOLUTIONI, RESOLUTIONJ):
        lista_normal_vec = []
        for i in range(RESOLUTIONI):
            norm = []
            for j in range(RESOLUTIONJ):
                norm.append(XYZ(0, 0, 0))
            lista_normal_vec.append(norm)

        i = 0
        j = 0
        for face in lista_faces:
            lista_normal_vec[i][j].x += face.vetor_normal[0]
            lista_normal_vec[i][j].y += face.vetor_normal[1]
            lista_normal_vec[i][j].z += face.vetor_normal[2]
            lista_normal_vec[i+1][j].x += face.vetor_normal[0]
            lista_normal_vec[i+1][j].y += face.vetor_normal[1]
            lista_normal_vec[i+1][j].z += face.vetor_normal[2]
            lista_normal_vec[i+1][j+1].x += face.vetor_normal[0]
            lista_normal_vec[i+1][j+1].y += face.vetor_normal[1]
            lista_normal_vec[i+1][j+1].z += face.vetor_normal[2]
            lista_normal_vec[i][j+1].x += face.vetor_normal[0]
            lista_normal_vec[i][j+1].y += face.vetor_normal[1]
            lista_normal_vec[i][j+1].z += face.vetor_normal[2]
            j += 1
            if j == RESOLUTIONJ-1:
                i += 1
                j = 0
        for i, vec in enumerate(lista_normal_vec):
            for j, v in enumerate(vec):
                module = np.sqrt(v.x**2 + v.y**2 + v.z**2)
                v.x = v.x/module
                v.y = v.y/module
                v.z = v.z/module
        return lista_normal_vec

    def scanline_calc(face, cores_vertices): # Codigo de calculo das scanlines de forma incremental
        list_scanlines = []
        #print(normais[0].x, normais[0].y, normais[0].z)
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
            x1, y1, z1, cor1 = int(face.vertices[i].x), int(face.vertices[i].y), int(face.vertices[i].z), cores_vertices[i]
            x2, y2, z2, cor2 = int(face.vertices[(i+1)%nv].x), int(face.vertices[(i+1)%nv].y), int(face.vertices[(i+1)%nv].z), cores_vertices[(i+1)%nv]
            if y2 < y1:
                xa, ya, za, cora = x2, y2, z2, deepcopy(cor2)
                x2, y2, z2, cor2 = x1, y1, z1, deepcopy(cor1)
                x1, y1, z1, cor1 = xa, ya, za, deepcopy(cora)
            y1, y2 = y1-y_min, y2-y_min
            xn = x1
            zn = z1
            corn = deepcopy(cor1)
            if y1+y_min != y_max or y2+y_min != y_max:
                if y1 == y2:
                    tx = tz = tr = tg = tb = 0
                else:
                    tr = (cor2.red-cor1.red)/(y2-y1)
                    tg = (cor2.green-cor1.green)/(y2-y1)
                    tb = (cor2.blue-cor1.blue)/(y2-y1)
                    if x1 == x2:
                        tx = 0
                    else:
                        tx = (x2-x1)/(y2-y1)
                    if z1 == z2:
                        tz = 0
                    else:
                        tz = (z2-z1)/(y2-y1)

                list_scanlines[y1].append((x1, z1, deepcopy(cor1)))
                for c in range(y1+1, y2):
                    xn = xn+tx
                    zn = zn+tz
                    corn.red += tr
                    corn.green += tg
                    corn.blue += tb
                    list_scanlines[c].append((int(xn), int(zn), deepcopy(corn)))
        for sl in list_scanlines:
            sl.sort(key=lambda z: z[0])
        return list_scanlines, y_min, y_max
    
    lista_normal_vertices = calc_normal_vertic(lista_faces, RESOLUTIONI, RESOLUTIONJ)
    lista_cor_vertices = []
    for i, normais in enumerate(lista_normal_vertices):
        norms = []
        for j, normal in enumerate(normais):
            norms.append(deepcopy(It_calc(Fonte_Luz.pos, [normal.x, normal.y, normal.z], CAMERA.VRP, lista_faces[i+j].vertices[0], Fonte_Luz.ila, Fonte_Luz.il, Fonte_Luz.Ka, Fonte_Luz.Kd, Fonte_Luz.Ks, Fonte_Luz.n)))
        lista_cor_vertices.append(norms)
    #print(lista_normal_vertices)
    # Preenche o buffer
    buffer = Buffer(WINDOW.WIDTH, WINDOW.HEIGHT)
    m = 0
    l = 0
    for i in range(len(lista_faces_tela)):
        face = lista_faces[i]
        normais = [lista_cor_vertices[m][l], lista_cor_vertices[m+1][l], lista_cor_vertices[m+1][l+1], lista_cor_vertices[m][l+1]]
        #print(f"[{m}][{l}] = {lista_cor_vertices[m][l].red} [{m}][{l+1}] = {lista_cor_vertices[m][l+1].red} [{m+1}][{l+1}] = {lista_cor_vertices[m+1][l+1].red} [{m+1}][{l}] = {lista_cor_vertices[m+1][l].red}")
        #print(cores_normais[0].red, cores_normais[1].red, cores_normais[2].red, cores_normais[3].red)
        l += 1
        if l == RESOLUTIONJ-1:
            m += 1
            l = 0

        scanlines, y_min, y_max = scanline_calc(lista_faces_tela[i], normais)
        for j, scanline in enumerate(scanlines):
            x1 = scanline[0][0]
            x2 = scanline[1][0]
            z1 = scanline[0][1]
            z2 = scanline[1][1]
            cor1 = deepcopy(scanline[0][2])
            cor2 = deepcopy(scanline[1][2])
            #print(scanline[0])
            #print([n1.x, n1.y, n1.z], [n2.x, n2.y, n2.z])
            
            if x1 == x2:
                tz = tr = tg = tb = 0
            else:
                tr = (cor2.red-cor1.red)/(x2-x1)
                tg = (cor2.green-cor1.green)/(x2-x1)
                tb = (cor2.blue-cor1.blue)/(x2-x1)
                if z1 == z2:
                    tz = 0
                else:
                    tz = (z2-z1)/(x2-x1)
            zn = z1
            corn = deepcopy(cor1)
            
            for k in range(x1, x2):
                buffer.test_and_set(k, j+y_min, zn, deepcopy(corn))
                zn += tz
                corn.red += tr
                corn.green += tg
                corn.blue += tb
    #print("Zbuffer calculado")
    # Pinta a tela com base no buffer
    for i in range(WINDOW.WIDTH-1):
        #print()
        for j in range(WINDOW.HEIGHT-1):
            #print(i, j)
            #print(f"({buffer.image_buffer[i, j].red}, {buffer.image_buffer[i, j].green}, {buffer.image_buffer[i, j].blue})", end=" ")
            #print(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue)
            if (buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue) != WINDOW.BACKGROUND:
                dpg.draw_line((i, j), (i+1, j), color=(buffer.image_buffer[i, j].red, buffer.image_buffer[i, j].green, buffer.image_buffer[i, j].blue), thickness=1, parent=tela)
                
def fillpoly(lista_faces_tela, lista_faces, tela, shading=0, cor_fundo=RGB(210, 210, 210)): # Algoritmo fillpoly em si. Pega a lista de scanlines e preenche linha por linha
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
                    dpg.draw_line([scanlines[j][i]+2, row], [scanlines[j][i+1], row], color=(cor_fundo.red, cor_fundo.green, cor_fundo.blue), thickness=1, parent=tela)
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
