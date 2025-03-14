from math import *

def cross(A, B): #A x B = vector
    return [A[1]*B[2] - A[2]*B[1],
            A[2]*B[0] - A[0]*B[2],
            A[0]*B[1] - A[1]*B[0]]

def processa_malha(malha):
    faces = [] # Initialize faces list outside the loops
    for i in range(len(malha) - 1): # Processa todas as linhas exceto a última
        for j in range(len(malha[i]) - 1): # Processa todas as colunas exceto a última
            p1 = malha[i][j]
            p2 = malha[i+1][j]
            p3 = malha[i+1][j+1]
            p4 = malha[i][j+1]
            # Armazena a face (quadrado formado por p1, p2, p3, p4)
            faces.append([p1, p2, p3, p4])
    return faces # Return AFTER both loops complete - FIX THE INDENTATION HERE

def print_faces(faces):
    print(f"Total faces: {len(faces)}")
    for i, face in enumerate(faces):
        print(f"Face {i}:")
        for j, point in enumerate(face):
            print(f" Point {j}: ({point.x}, {point.y}, {point.z})")

def visibility(malha, VRP):
    visible_points = []
    visible_faces = []
    faces_ord = []
    d_values = []  # To collect D values
    
    faces = processa_malha(malha)
    #print(f"Total faces generated: {len(faces)}")  # Debug print
    
    for face in faces:
        p1, p2, p3, p4 = face
        x1, y1, z1 = p1.x, p1.y, p1.z
        x2, y2, z2 = p2.x, p2.y, p2.z
        x3, y3, z3 = p3.x, p3.y, p3.z
        x4, y4, z4 = p4.x, p4.y, p4.z
        
        # Vetores
        vB_A = [x1-x2, y1-y2, z1-z2]
        vB_C = [x3-x2, y3-y2, z3-z2]
        
        # normal = vB_C x vB_A
        normal = cross(vB_A,vB_C)
        
        # Normalize the normal vector
        modulo = sqrt((normal[0]**2) + (normal[1]**2) + (normal[2]**2))
        if modulo == 0:
            continue  # Skip degenerate faces
            
        n = (normal[0]/modulo, normal[1]/modulo, normal[2]/modulo)
        
        # Calculate centroid
        centroide = [(x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, (z1 + z2 + z3 + z4) / 4]
        
        # Vector from centroid to VRP
        Ozao = (VRP[0]-centroide[0], VRP[1]-centroide[1], VRP[2]-centroide[2])
        
        # Normalize the VRP-centroid vector
        modulo = sqrt((Ozao[0]**2) + (Ozao[1]**2) + (Ozao[2]**2))  # FIX: use Ozao[2] instead of Ozao[1] twice
        
        if modulo == 0:
            continue  # Skip if centroid == VRP
            
        ozinho = (Ozao[0]/modulo, Ozao[1]/modulo, Ozao[2]/modulo)
        
        # Dot product of normalized vectors (cosine of angle between them)
        D = ozinho[0]*n[0] + ozinho[1]*n[1] + ozinho[2]*n[2]
        d_values.append(D)  # Store the D value
        
        # Calculate depth for painter's algorithm
        depth = ((VRP[0]-centroide[0])**2 + (VRP[1]-centroide[1])**2 + (VRP[2]-centroide[2])**2)
        faces_ord.append((depth, face))
        
        # If D > 0, observer is in front of the plane
        if D > 0:
            visible_faces.append(face)
            visible_points.extend([p1, p2, p3, p4])
    
    # Debug information
    #print(f"Total D values calculated: {len(d_values)}")
    #print(f"Positive D values (visible faces): {sum(1 for d in d_values if d > 0)}")
    #print(f"Negative D values (non-visible faces): {sum(1 for d in d_values if d <= 0)}")
    
    # Sort visible faces by depth
    faces_ord = sorted(faces_ord, key=lambda x: x[0], reverse=True)
    
    return visible_points, visible_faces, faces_ord