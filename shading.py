from pipeline import normalize, cross, dot
from pygame import *
from buffer import *
from superfice import XYZ
import dearpygui.dearpygui as dpg

class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

class Face:
    def __init__(self, lista_vertices):
        self.vertices = lista_vertices
        self.centroide = self.calc_centroid()
        self.vetor_normal = self.calc_vetor_normal()
    
    def calc_centroid(self):
        centroide = XYZ(0, 0, 0)
        for vertice in self.lista_vertices:
            centroide.x += vertice.x
            centroide.y += vertice.y
            centroide.z += vertice.z
        centroide.x = centroide.x/len(self.lista_vertices)
        centroide.y = centroide.y/len(self.lista_vertices)
        centroide.z = centroide.z/len(self.lista_vertices)
        return centroide
    
    def calc_vetor_normal(self):
        ver_a, ver_b, ver_c = self.lista_vertices[0], self.lista_vertices[1], self.lista_vertices[2]
        vec_b_a = [ver_a.x-ver_b.x, ver_a.y-ver_b.y, ver_a.z-ver_b.z]
        vec_b_c = [ver_c.x-ver_b.x, ver_c.y-ver_b.y, ver_c.z-ver_b.z]
        return normalize(cross(vec_b_c, vec_b_a))

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

def somb_const(list_faces, vrp, L, ila, il, ka, kd, ks, n):
    It_faces = []
    for fc in list_faces:
        centroide = fc.centroide
        N = fc.vetor_normal #normal da face
        L_dir = normalize([L.x-centroide.x,  L.y-centroide.y,  L.z-centroide.z]) #vetor direção da luz 

        Ia = RGB(ila.red*ka.red, ila.green*ka.green, ila.blue*ka.blue)

        n_dot_l = dot(N, L_dir)
        if n_dot_l < 0:
            It_faces.append(It_calc(Ia, RGB(0, 0, 0), RGB(0, 0, 0))) #apenas iluminação ambiente p a face atual
            continue
        
        Id = [il.red*kd.red*n_dot_l,   il.green*kd.green*n_dot_l,   il.blue*kd.blue*n_dot_l]
        
        aux =        [   2*n_dot_l*N.x,       2*n_dot_l*N.y,       2*n_dot_l*N.z   ] 
        r = normalize([ aux.x-L_dir.x,      aux.y-L_dir.y,      aux.z-L_dir.z  ])
        s = normalize([vrp.x-centroide.x,   vrp.y-centroide.y,   vrp.z-centroide,z])
        r_dot_s = dot(r, s)

        if r_dot_s < 0:
            It_faces.append(It_calc(Ia, Id, RGB(0, 0, 0))) #apenas iluminação ambiente e difusa p a face atual
            continue
        
        aux = r_dot_s**n
        Is = [il.red*ks.red*aux,  il.green*ks.green*aux,  il.blue*ks.blue*aux]

        It_faces.append(It_calc(Ia, Id, Is))

    return It_faces


def fillpoly_constante(screen, obj, It_faces, v_faces, zbuffer, imgbuffer):
    for i in range(len(It_faces)):
        R,G,B = It_faces[i]
        cor_pixel = (int(R),int(G),int(B))
        a,b,c,d = v_faces[i]


        #abc = triangulo1
        #acd = triangulo2
        ABC = sorted([obj[a], obj[b], obj[c]], key=lambda ponto: ponto[1])
        fill_triangulo(screen, ABC[0], ABC[1], ABC[2], cor_pixel,zbuffer,imgbuffer)

        ABC = sorted([obj[a], obj[c], obj[d]], key=lambda ponto: ponto[1])
        fill_triangulo(screen, ABC[0], ABC[1], ABC[2], cor_pixel,zbuffer,imgbuffer)

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
        f_normals.append(normalize(normal(obj[aux[0]],  obj[aux[1]],  obj[aux[2]]))) #normal unitária de todas as faces

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

def fillpoly(face, tela, shading=0, cor_fundo=RGB(255, 255, 255)): # Algoritmo fillpoly em si. Pega a lista de scanlines e preenche linha por linha
    def scanline_calc(face): # Codigo de calculo das scanlines de forma incremental
        list_scanlines = []
        nv = len(face.vertices) # Numero de vertices
        y_max, y_min = 0, np.inf
        for v in face.vertices:
            if v.y > y_max:
                y_max = v.y
            elif v.y < y_min:
                y_min = v.y
        ns = y_max - y_min # Numero de scanlines

        for i in range(ns):
            scanline = []
            list_scanlines.append(scanline)

        for i in range(nv):
            x1, y1 = face.vertices[i]
            x2, y2 = face.vertices[(i+1)%nv]
            if y2 < y1:
                xa, ya = x2, y2
                x2, y2 = x1, y1
                x1, y1 = xa, ya
            y1, y2 = y1-y_min, y2-y_min
            xn = x1
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
    
    scanlines, y_min, y_max = scanline_calc()
    row = y_min

    # Fillpoly tradicional, usado para o wireframe. Pinta com uma cor solida definida (cor de fundo)
    if shading == 0: 
        for sl in scanlines:
            for i in range(0, len(sl)-1, 2):
                dpg.draw_line([sl[i], row], [sl[i+1], row], color=cor_fundo, thickness=1, parent=tela)
            row = row+1
    # Fillpoly com sombreamento constante com z-buffer
    elif shading == 1: 
        for sl in scanlines: # Percorre entre as scanlines
            for i in range(0, len(sl)-1, 2): # Percorre entre as interseccoes na scanline
                x = sl[i]
                for j in range(sl[i], sl[(i+1)%len(face.vertices)]): # Percorre pelos pixels entre as interseccoes
                    dpg.draw_line([x, row], [x, row], color=cor_fundo, thickness=1, parent=tela)
            row = row+1
    # Fillpoly com sombreamento gouraud
    elif shading == 2: 
        for sl in scanlines:
            for i in range(0, len(sl)-1, 2):
                dpg.draw_line([sl[i], row], [sl[i+1], row], color=cor_fundo, thickness=1, parent=tela)
            row = row+1

def fill_triangulo(screen, A, B, C, cor, zbuffer, imgbuffer):
    cor_A_rgb = cor[0]
    cor_B_rgb = cor[1]
    cor_C_rgb = cor[2]

    tx_corA_B = tx_corA_C = tx_corB_C = [0.01, 0.01, 0.01] #declaração

    if A[1] == B[1]:
        txA_B = 0
        tzA_B = 0
        tx_corA_B = [0.01, 0.01, 0.01]

        txB_C = (C[0] - B[0]) / (C[1] - B[1])
        tzB_C = (C[2] - B[2]) / (C[1] - B[1])
        tx_corB_C = [((1 / (C[1] - B[1])) * (cor_C_rgb[x] - cor_B_rgb[x])) for x in range(len(tx_corB_C))]

    elif B[1] == C[1]:
        txA_B = (B[0] - A[0]) / (B[1] - A[1])
        tzA_B = (B[2] - A[2]) / (B[1] - A[1])
        tx_corA_B = [((1 / (B[1] - A[1])) * (cor_B_rgb[x] - cor_A_rgb[x])) for x in range(len(tx_corA_B))] 

        txB_C = 0 
        tzB_C = 0
        tx_corB_C = [0.0, 0.0, 0.0]

    else:
        txA_B = (B[0] - A[0]) / (B[1] - A[1])
        tzA_B = (B[2] - A[2]) / (B[1] - A[1])
        tx_corA_B = [((1 / (B[1] - A[1])) * (cor_B_rgb[x] - cor_A_rgb[x])) for x in range(len(tx_corA_B))]

        txB_C = (C[0] - B[0]) / (C[1] - B[1])    
        tzB_C = (C[2] - B[2]) / (C[1] - B[1])
        tx_corB_C = [((1 / (C[1] - B[1])) * (cor_C_rgb[x] - cor_B_rgb[x])) for x in range(len(tx_corB_C))]

    txA_C = (C[0] - A[0]) / (C[1] - A[1])
    tzA_C = (C[2] - A[2]) / (C[1] - A[1])
    tx_corA_C = [((1 / (C[1] - A[1])) * (cor_C_rgb[x] - cor_A_rgb[x])) for x in range(len(tx_corA_C))]

    x1 = x2 = A[0]
    z1 = z2 = A[2]
    corA_B = corA_C = cor_A_rgb

    for y in range((int(A[1]+1)), (int(C[1] - 1))):
        if (y < B[1]):
            x1 += txA_B
            z1 += tzA_B
            corA_B = [x + y for x, y in zip(corA_B, tx_corA_B)]

        elif (y == B[1]):
            x1 = B[0]
            z1 = B[2]
            corA_B = cor_B_rgb
        else:
            x1 += txB_C
            z1 += tzB_C
            corA_B = [x + y for x, y in zip(corA_B, tx_corB_C)]

        x2 += txA_C
        z2 += tzA_C
        corA_C = [i + j for i, j in zip(corA_C, tx_corA_C)]



        tx_cor_pixel = [0.01, 0.01, 0.01]
        tx_cor_pixel = [((1 / abs(x2 - x1)) * (corA_C[x] - corA_B[x])) for x in range(len(tx_cor_pixel))]

        if (x1<x2):
            tzX1_X2 = ((z2-z1) / (x2-x1))
            zint = z1
            cor_pixel = corA_B
            tx_cor_pixel = [((corA_C[x] - corA_B[x]) / (x2 - x1)) for x in range(len(tx_cor_pixel))]
        else:
            tzX1_X2 = ((z1-z2) / (x1-x2))
            zint = z2
            cor_pixel = corA_C
            tx_cor_pixel = [((corA_B[x] - corA_C[x]) / (x1 - x2)) for x in range(len(tx_cor_pixel))]


        for x in range(round(min(x1, x2)), (round(max(x1, x2)))):
            cor_pixel = [x + y for x, y in zip(cor_pixel, tx_cor_pixel)]
            cor_pixel_int = [int(round(x)) for x in cor_pixel]
            pixel = imgbuffer.get_pixel(x,y) #pega a posição no buffer de imagem
            if np.all(pixel != [0,0,0]): #se for diferente de (0,0,0) ja esta pintado
                if zbuffer.test_and_set(round(x),round(y),round(zint)): #verifica se o z em processamento é maior ou menor que o z armazenado
                    imgbuffer.put_pixel(round(x),round(y),cor) #atualiza o buffer de imagem
                    screen.set_at((x,y),cor) #pinta a tela
            else:
                imgbuffer.put_pixel(round(x),round(y),cor)
                screen.set_at((x,y),cor)
            zint+=tzX1_X2
