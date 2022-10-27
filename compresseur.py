#!/usr/bin/env python

# from ssl import VERIFY_X509_PARTIAL_CHAIN
import math
import sys
from dis import dis
from hashlib import new
from multiprocessing.sharedctypes import Value
from os import listdir
from pickle import NEXT_BUFFER
from re import A

import numpy as np

import obja


class Test(obja.Model):
    """
    A test class that decimates a 3D model with arbitrary triangle meshes.
    """
        
    faces_rec = []
    tour = 1
        
    def __init__(self):
        super().__init__()
        
    def compressionne(self,output):
        """
        Compressionne un obj en obja.
        """
        op = []  
        
        while self.tour < 60:
            # print("tour n° " + str(self.tour) + "\n")
            # Etape 1 : trouver les sommets à supprimer 
            sommets = find_vertices_to_delete(self)
            
            # Etape 2 : Ordonner les patchs et décimer
            (patchs, faces) = self.find_patches(sommets)
            op = trace_Z(self, patchs, faces, sommets, op)
            
            output_model = obja.Output(output, random_color=True)

            self.tour += 1
            
                    


        # Après la compression, on sauvegarde l'état le plus compressé
        for (index, face) in enumerate(self.faces):
            if face is not None:
                op.append(('afnc', index, face))
        for (index, vertex) in enumerate(self.vertices):
            if vertex is not None:
                op.append(('av', index, vertex))
        
        # On inverse les opérations de compression pour simuler la décompression
        op.reverse()
        
        
        # Ecriture du fichier .obja
        for (ty, index, value) in op:
            if ty == 'av':
                output_model.add_vertex(index, value)
            elif ty == 'afnc':
                output_model.add_face(index, value)
            elif ty == 'af':
                output_model.add_face_color(index, value)
            elif ty == 'ef':
                output_model.edit_face(index, value)
        
  
        
    def sort_patch_rec(self, list_faces, del_vert, vert_prec):
        """
        Fonction récursive qui range dans les faces d'un patch, avant suppression du
        sommet au centre, et retourne la liste des indices des sommets du patch dans 
        un ordre de contour.
        (L'ordre se décide lors de l'appel de la fonction avec le paramètre vert_prec)
        """
        if list_faces == []:
            return []
        else:
            # Pour chaque face
            for ind in range(len(list_faces)):
                (f,_) = list_faces[ind]
                # liste des sommets de la face courante
                verts_f = [f.a, f.b, f.c]
                # si le sommet à supprimer fait parti de la face courante
                # et le sommet précédent fait aussi parti de la face courante
                if del_vert in verts_f and vert_prec in verts_f:
                    # Pour chaque sommet de la face courante
                    for v in verts_f:
                        # Si le sommet courant n'est pas le sommet à supprimer ni le sommet précédent
                        if v != del_vert and v != vert_prec:
                            self.faces_rec.append(list_faces[ind])
                            # Suppression de la face courante
                            list_faces.pop(ind)
                            # Ajout du sommet courant dans le liste des sommets du patch
                            return [v] + self.sort_patch_rec(list_faces, del_vert, v)
                    
    def find_patches(self, vertices_to_delete):
        """
        Fonction qui retourne les patchs et points à supprimer à partir de
        ces points.
        Il s'agit de l'étape de compression juste avant de dessiner les Z.
        
        arguments : - liste d'indices de sommets (au milieu des patchs) à supprimer
        
        retour :    - patches : liste des patchs (liste de liste d'indices de sommets)  
                    - faces_in_the_patches : liste des faces dans les patchs (liste de liste de faces) 
        """
        patches = []
        # liste intermédiaire de faces
        temp_faces_list = []
        # faces du patch
        faces_in_the_patches = []
        
        
        # On itère dans les sommets à supprimer
        for vert_index in vertices_to_delete:   
            
            self.faces_rec.clear()            
            # On itère sur les faces du modèle et on en conserve certaines temporairement
            for i in range(len(self.faces)):
                face = self.faces[i]
                if face is not None:
                    if vert_index in [face.a, face.b, face.c]:
                        # La face courante possède le sommet à supprimer courant
                        # On la conserve avec son indice absolue dans le modèle
                        temp_faces_list.append((face,i))
            
            if vert_index == temp_faces_list[0][0].a:
                # le précédent est le dernier de la première face
                next_vertex = temp_faces_list[0][0].c
                # Si le sommet courant est le second de la première face
            elif vert_index == temp_faces_list[0][0].b:
                # le précédent est le dernier de la première face
                next_vertex = temp_faces_list[0][0].a
            else:
                # le précédent est le second de la première face
                next_vertex = temp_faces_list[0][0].b

            # On construit la liste des sommets du patch
            # et on range les faces dans l'ordre trigonométrique
            patch = self.sort_patch_rec(temp_faces_list, vert_index, next_vertex)

            # ajoute la liste des sommets du patch à la liste des patchs
            patches.append(patch)
            faces_in_the_patches.append(list(self.faces_rec))
            
        return (patches, faces_in_the_patches)


def trace_Z(self, patches, faces_in_the_patches, vertices_to_delete, operations):
    """
    Fonction qui effectue les modification sur le mesh. Plus précisément supprime les
    points des milieus de patchs et trace les Z.
    
    arguments : - liste des patchs (liste de liste d'indices de sommets de contour)
                - liste des faces dans les patchs (liste de liste de tuples (face,indice) )
                - liste des sommets au milieu des patchs à supprimer (liste d'indices de sommets)
    
    retour :    - liste des opérations à effectuer (list de string)   
    """   
    
    # Dans cette fonction, remplacer les 'afnc' par 'af' pour voir les ajout de faces de chaque 
    # itération de compression en couleur.
    
    # On itère sur les patchs
    for i in range(len(patches)):
        patch = patches[i]
        vert_del = vertices_to_delete[i]
        
        # Etape 1 : Suppression des deux faces en face l'une de l'autre
        n2 = math.ceil(len(faces_in_the_patches[i])/2)
        operations.append(('afnc', faces_in_the_patches[i][0][1], faces_in_the_patches[i][0][0]))
        ind_to_del = self.faces.index(faces_in_the_patches[i][0][0])
        self.faces[ind_to_del] = None
        operations.append(('afnc', faces_in_the_patches[i][n2][1], faces_in_the_patches[i][n2][0]))
        ind_to_del = self.faces.index(faces_in_the_patches[i][n2][0])
        self.faces[ind_to_del] = None
            
        # Etape 2 : Modification des faces restantes du patch pour faire apparaitre le Z
        for j in range(len(faces_in_the_patches[i])):
            (face, index) = faces_in_the_patches[i][j]
            if self.faces[index] is not None: 
                # modifier les n-2 faces restantes                
                if vert_del == face.a:
                    
                    if patch.index(face.b) == 0 :
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.c)])
                    elif patch.index(face.b) == n2:
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.c)])
                    else:
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.b)])
                        
                elif vert_del == face.b:
                    
                    if patch.index(face.c) == 0 :
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    elif patch.index(face.c) == n2:
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    else:
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.c)])
                        
                elif vert_del == face.c:
                    
                    if patch.index(face.a) == 0 :
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    elif patch.index(face.a) == n2:
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    else:
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.a)])
                        
                else:
                    print("ERREUR : patch non conforme")
                    
                operations.append(('ef', index, face))
                self.faces[index] = new_face
                            
                            
        # Etape 3 : Suppression du sommet du milieu du patch        
        operations.append(('av', vert_del, self.vertices[vert_del]))
        self.vertices[vert_del] = None
        
    return operations
        
        
        
    

                            
       
def find_vertices_to_delete(self):
    
    # Distances entre un sommet et le plan moyen du patch associé au sommet
    distances = []

    # Indices des sommets 
    index_vertices = []

    # Voisins des sommets 
    voisins_vertices = []

    # Parcours de l'ensemble des sommets par indice (vertex_index) et valeur du sommet (vertex)
    for (vertex_index, vertex) in enumerate(self.vertices):

        if vertex is not None:
            # Définition de la liste des points formant le patch 
            liste_points = []

            # Parcours de l'ensemble des faces par indice (face_index) et valeur de la face (face)
            for (face_index, face) in enumerate(self.faces):

                if face is not None:
                    # Liste des points d'une face
                    L = [face.a, face.b, face.c]

                    # Si le sommet courant fait parti de la face
                    if vertex_index in L:

                        # Parcours des sommets d'une face
                        for l in L:

                            # Si le sommet courant n'appartient pas à la liste des points d'un patch 
                            if l not in liste_points+[vertex_index]:
                                # on ajoute le point à la liste de points d'un patch
                                liste_points.append(l)
                            # fin sommet courant n'appartient pas dans les points d'un patch
                        # fin parcours des sommets d'une face
                # fin de sommet courant fait parti de la face

            # Si le nombre de points d'un patch est supérieur ou égal à 5 
            # (on ne travaille pas sur des patchs de taille inférieure à 5)                

            if len(liste_points) > 5:
                
                # Calcul des coefficients du plan moyen pour ce patch
                A = np.ones((len(liste_points)+1, 4))
                # Première ligne initialisée avec le sommet courant
                A[0, 0:3] = vertex
                # print('liste des vertices du mesh : '+str(self.vertices))
                # Parcours des points du patch par indice (i) et valeur (l)
                for (i, l) in enumerate(liste_points):
                    # i-ème ligne initialisée avec les sommets du patch
                    A[i+1, 0:3] = self.vertices[l]
                # fin parcours des points du patch
                tAA = A.transpose() @ A
                # print("tAA = "+str(tAA))

                # Calcul des vecteurs propres et valeurs prorpes 
                valeurs_propres, vecteurs_propres = np.linalg.eig(tAA)
                # Indice de la plus petite valeur propre
                ind = np.argmin(valeurs_propres)
                # Vecteur propre associé à la plus petite valeur propre
                X = vecteurs_propres[:, ind]
                # Calcul de
                n = np.array(X[0:3])
                # Calcul de la distance entre le sommet courant (vertex) et le plan moyen
                k = (- X[3] - n.transpose() @ vertex) / np.linalg.norm(n)
                # Mémorise la distance du sommet courant et du plan moyen
                distances.append(abs(k))
                # Mémorise l'indice du sommet courant
                index_vertices.append(vertex_index)
                # Mémorise les voisins du somme courant
                voisins_vertices.append(liste_points[:])
            # fin len(liste_points) >= 5
    # fin du parcours des sommets


    # Construit la liste des indices par ordre décroissant de distance
    indices_tries = [i[0] for i in sorted(enumerate(distances), key=lambda x:x[1])]
    # distance seuil croissante en fonction du nombre d'itérations
    d0 = (2 + 0.5*(self.tour**2)) * distances[indices_tries[0]]
    # Si un sommet d'une face est supprimé, il faut conserver les autres sommets de la face
    dont_touch = []
    # Parcours des indices des sommets triés par distance
    i = 0

    # Définition de la liste des sommets supprimés 
    deleted_vertices = []
    # Recherche d'un sommet dont la distance est inférieure à d0
    while i < len(indices_tries) and distances[indices_tries[i]] < d0 :
        # Si le sommet courant peut être supprimé
        if index_vertices[indices_tries[i]] not in dont_touch:
            # Test de conformité du path (pourrait être plus robuste)
            if try_patch(self, voisins_vertices[indices_tries[i]], index_vertices[indices_tries[i]]):
                # ajout du sommet à supprimer à la liste des suppressions
                deleted_vertices.append(index_vertices[indices_tries[i]])
            # ajout de la liste des voisins qui ne doivent pas être supprimés
            for ind in voisins_vertices[indices_tries[i]]:
                if ind not in dont_touch:
                    dont_touch.append(ind)
        # fin sommet courant peut être supprimé
        # passage au sommet suivant
        i += 1
    # fin recherche sommet dont la distance est inférieure à d0
    return deleted_vertices    
    
    
    
def try_patch(self, vertices, vert_del):
    """
    Fonction qui teste si un patch est utilisable.
    Retourne un booleen
    """                
    liste = []
    for f in self.faces:
        if f is not None:
            if vert_del in [f.a, f.b, f.c]:
                liste.append(f.a)
                liste.append(f.b)
                liste.append(f.c)
                liste.remove(vert_del)    
    if len(liste) < 10:
        return False
    
    for v in vertices:
        if liste.count(v) != 2:
            return False
    return True
        
                           

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Test()
    model.parse_file('example/suzanne.obj')

    with open('example/suzanne.obja', 'w') as output:
        model.compressionne(output)
    

if __name__ == '__main__':
    main()
