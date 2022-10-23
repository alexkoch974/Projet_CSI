#!/usr/bin/env python

# from ssl import VERIFY_X509_PARTIAL_CHAIN
from dis import dis
from hashlib import new
from re import A
import obja
import numpy as np
import sys
import math

class Test(obja.Model):
    """
    A test class that decimates a 3D model with arbitrary triangle meshes.
    """

    # Facettes TODO CP
    faces_rec = []
        
    def __init__(self):
        super().__init__()
        
    def compressionne(self,output):
        """
        Compressionne un obj en obja.
        """
        # sommets = [6] # sommet 7 du mesh test.py
        # sommets = [75] # patch 76 317 355 303 354 316 pour suzanne
        # Nombre de sommets
        nb_vert_init = len(self.vertices)
        # TODO CP
        op = []
        # numéro de l'itération
        tour = 1
        
        # while len(self.vertices)/nb_vert_init >= 0.1:
        # tant que le nombre d'itération est inférieur à 3
        # CP : y a t'il une raison particulière pour 3 ?
        while tour < 3:
            print("tour n° " + str(tour) + "\n")
            # Choix des sommets qui peuvent être supprimés
            sommets = decimation(self)
            (patch, faces) = self.find_patches(sommets)
            op = trace_Z(self, patch, faces, sommets, op)
            output_model = obja.Output(output, random_color=True)
            
            new_nb_vert = len([i for i in self.vertices if i is not None])
            # self.faces = [i for i in self.faces if i is not None]
            # counter = 0
            # l = []
            # for f in self.faces:
            #     if f.a == f.b:
            #         counter += 1
            #         l.append(f)
            #     if f.a == f.c:
            #         counter += 1
            #         l.append(f)
            #     if f.b == f.c:
            #         counter += 1
            #         l.append(f)
            # if counter != 0:
            #     print(l)
            
            
            # print("Y a t il des None dans self.vertices ? ")
            # print(any(x is None for x in self.vertices))
            # print("Y a t il des None dans self.faces ? ")
            # print(any(x is None for x in self.faces))
            # Passage à l'itération suivante
            tour += 1
            
                    



        for (index, face) in enumerate(self.faces):
            if face is not None:
                op.append(('af', index, face))
        for (index, vertex) in enumerate(self.vertices):
            if vertex is not None:
                op.append(('av', index, vertex))
        
        
        op.reverse()
        print(op)
        
        
        for (ty, index, value) in op:
            print((ty, index, value))
            if ty == 'av':
                output_model.add_vertex(index, value)
            elif ty == 'af':
                output_model.add_face(index, value)
            elif ty == 'ef':
                output_model.edit_face(index, value)
        
        

        
        
    def sort_patch_rec(self, list_faces, del_vert, vert_prec):
        """
        Fonction récursive qui range dans les facettes d'un patch, avant suppression du
        sommet au centre, et retourne la liste des indices des sommets du patch dans 
        un ordre de contour.
        (L'ordre se décide lors de l'appel de la fonction avec le paramètre vert_prec qui est le précédent du
        sommet à supprimer dans le contour)
        """
        # print('list_faces : '+str(list_faces))
        # print('del_vert : '+str(del_vert))
        # print('vert_prec : '+str(vert_prec))
        if list_faces == []:
            return []
        else:
            # Pour chaque facette
            for ind in range(len(list_faces)):
                # facette courante
                ( f, _) = list_faces[ind]
                # liste des sommets de la facette courante
                verts_f = [f.a, f.b, f.c]
                # print(verts_f)
                # print('--------------------------------------')
                # si le sommet à supprimer fait partie de la facette courante
                # et le sommet précédent fait aussi partie de la facette courante
                if del_vert in verts_f and vert_prec in verts_f:
                    # Pour chaque sommet de la facette courante
                    for v in verts_f:
                        # Si le sommet courant n'est pas le sommet à supprimer ni le sommet précédent
                        if v != del_vert and v != vert_prec:
                            self.faces_rec.append(list_faces[ind])
                            # Suppression de la facette courante
                            list_faces.pop(ind)
                            # Ajout du sommet courant dans le liste des sommets du patch
                            zouz = self.sort_patch_rec(list_faces, del_vert, v)
                            # print(zouz)
                            return [v] + zouz
                    
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
        # liste intermédiaire de facettes
        temp_faces_list = []
        # facettes du patch
        faces_in_the_patches = []
        
        
        # Iterate through the vertices to delete
        # ----------- TODO : check avec Kuremon pour avoir des index
        for vert_index in vertices_to_delete:   
            
            self.faces_rec.clear()
            
            # Iterate through the faces and store them temporarily
            for i in range(len(self.faces)):
                face = self.faces[i]
                if face is not None:
                    if vert_index in [face.a, face.b, face.c]:
                        # Ajout de la facette courante dans la liste intermédiaire
                        temp_faces_list.append((face,i))
            
            # faces_in_the_patches.append(list(temp_faces_list))


            if vert_index == temp_faces_list[0][0].a:
                # le précédent est le dernier de la première facette
                next_vertex = temp_faces_list[0][0].c
                # Si le sommet courant est le second de la première facette
            elif vert_index == temp_faces_list[1][0].b: # 1 remplacé par 0 (CP)
                # le précédent est le dernier de la première facette
                next_vertex = temp_faces_list[0][0].a
            else:
                # le précédent est le second de la première facette
                next_vertex = temp_faces_list[0][0].b

            # construit la liste des sommets du patch
            # print(temp_faces_list)
            # print('########################################')
            patch = self.sort_patch_rec(temp_faces_list, vert_index, next_vertex)
            # print('########################################')

            # ajoute la liste des sommets du patch à la liste des patchs
            patches.append(patch)
            faces_in_the_patches.append(list(self.faces_rec))
                
        return (patches, faces_in_the_patches)


def trace_Z(self, patches, faces_in_the_patches, vertices_to_delete, operations):
    """
    Fonction qui modifie le maillage : supprime les sommets du milieu de patchs et trace les Z.
    
    Paramètres : - liste des patchs (liste de liste d'indices des sommets du contour de chaque patch)
                - liste des facettes dans les patchs (liste de liste de tuples (facette,indice) )
                - liste des sommets au milieu des patchs à supprimer (liste d'indices de sommets)
    
    Retour : - liste des opérations à effectuer (list de string)
    """
    # Pour chaque indice de patch
    for i in range(len(patches)):
        # Patch courant : suite de sommets qui forment le contour du patch
        patch = patches[i]
        # suppression des 2 facettes opposées (numéro 0 et n/2)
        # il y en a au moins 2 car les patchs contiennent au moins
        n2 = math.ceil(len(faces_in_the_patches[i])/2)
        # Ajout de l'opération que TODO
        operations.append(('af', 0, faces_in_the_patches[i][0][0]))
        # Indices des facettes à supprimer
        ind_to_del = self.faces.index(faces_in_the_patches[i][0][0])
        # Suppression des facettes concernées
        self.faces[ind_to_del] = None
        # Ajout de l'opération que TODO
        operations.append(('af', n2, faces_in_the_patches[i][n2][0]))
        # Indices des facettes à supprimer
        ind_to_del = self.faces.index(faces_in_the_patches[i][n2][0])
        # Suppression des facettes concernées
        self.faces[ind_to_del] = None
        # Sommet à supprimer
        vert_del = vertices_to_delete[i]        
        
        # print('taille du patch : '+str(len(faces_in_the_patches[i])))
        # print('n2 = '+str(n2))
        # print('patch : ')
        # print(faces_in_the_patches[i])
        # print()
        # print(patches[i])
        # print()
        # print(vertices_to_delete)
        # print()

        # Pour chaque indice de facette dans le patch courant
        for j in range(len(faces_in_the_patches[i])):
            # facette courante et son indice dans le patch (TODO CP : c'est à dire)
            (face, index) = faces_in_the_patches[i][j]
            # si la facette de l'indice courant n'est pas vide (TODO CP : c'est à dire)
            # ce n'est pas une facette qui a déjà été supprimée
            if self.faces[index] is not None:                   ########## ICI J'AI CHANGE != PAR is not
                # modifier les n - 2 facettes restantes du patch courant

                # si le sommet à supprimer est le sommet a de la facette
                if vert_del == face.a:
                    # si la position dans le contour du patch du sommet b de la facette courante est 0 (TODO CP : c'est à dire)
                    # il s'agit d'une facette adjacente à la facette 0 du patch
                    if patch.index(face.b) == 0:
                        # création d'une nouvelle facette à partir des sommets b, c et du
                        # sommet obtenu dans le contour de la facette à partir de l'indice
                        # de c dans le contour
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.c)])
                    # si la position dans le patch du sommet b de la facette courante est n / 2 (TODO CP : c'est à dire)
                    # il s'agit d'une facette adjacente à la facette n / 2 du patch
                    elif patch.index(face.b) == n2:
                        # création d'une nouvelle facette à partir des sommets b, c et du
                        # sommet obtenu dans le contour de la facette à partir de l'indice
                        # de c dans le contour
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.c)])
                    # sinon, c'est une facette entre 0 et n / 2 qui n'est pas adjacente
                    else:
                        # création d'une nouvelle facette à partir des sommets b, c et du
                        # sommet obtenu dans le contour de la facette à partir de l'indice
                        # de b dans le contour
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.b)])

                # si le sommet à supprimer est le sommet b de la face
                elif vert_del == face.b:
                    # si la position dans le patch du sommet c de la facette courante est 0 (TODO CP : c'est à dire)
                    if patch.index(face.c) == 0:
                        # création d'une nouvelle facette à partir des sommets c, a et de TODO CP
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    # si la position dans le patch du sommet c de la facette courante est n / 2 (TODO CP : c'est à dire)
                    elif patch.index(face.c) == n2:
                        # création d'une nouvelle facette à partir des sommets b, c et de TODO CP
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    #
                    else:
                        # création d'une nouvelle facette à partir des sommets c, a et de TODO CP
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.c)])

                # si le sommet à supprimer est le sommet c de la face
                elif vert_del == face.c:
                    # si la position dans le patch du sommet a de la facette courante est 0 (TODO CP : c'est à dire)
                    if patch.index(face.a) == 0:
                        # création d'une nouvelle facette à partir des sommets a, b et de TODO CP
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    # si la position dans le patch du sommet a de la facette courante est n / 2 (TODO CP : c'est à dire)
                    elif patch.index(face.a) == n2:
                        # création d'une nouvelle facette à partir des sommets a, b et de TODO CP
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    #
                    else:
                        # création d'une nouvelle facette à partir des sommets a, b et de TODO CP
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.a)])

                # sinon : Ce cas n'est pas possible
                else:
                    print("ERREUR !!")
                    print(vert_del)

                # Ajout de l'opération que effacer la face à l'indice
                operations.append(('ef', index, face))
                self.faces[index] = new_face
                            
                # if new_face.a == new_face.b:
                #     print('indice de la face dans le patch : '+str(j))
                #     print('=========================================')
                #     print((face, index))
                #     print('->')
                #     print(new_face)
                #     print('-----------------------------')
                # elif new_face.b == new_face.c:
                #     print('indice de la face dans le patch : '+str(j))
                #     print('=========================================')
                #     print((face, index))
                #     print('->')
                #     print(new_face)
                #     print('-----------------------------')
                # elif new_face.c == new_face.a:
                #     print('indice de la face dans le patch : '+str(j))
                #     print('=========================================')
                #     print((face, index))
                #     print('->')
                #     print(new_face)
                #     print('-----------------------------')
                
                    
                

            
        # supprimer le sommet du milieu du patch        
        operations.append(('av', vert_del, self.vertices[vert_del]))
        self.vertices[vert_del] = None
        
    return operations
        
        
        
    

                            
       
def decimation(self):
    
        # Distances entre un sommet et le plan moyen du patch associé au sommet
        distances = []

        # Indices des sommets 
        index_vertices = []

        # Voisins des sommets 
        voisins_vertices = []

        # Parcours de l'ensemble des sommets par indice (vertex_index) et valeur du sommet (vertex)
        for (vertex_index, vertex) in enumerate(self.vertices):

            # Si le sommet courant existe
            if vertex is not None:
                # Définition de la liste des points formant le patch 
                liste_points = []

                # Parcours de l'ensemble des facettes par indice (face_index) et valeur de la facette (face)
                for (face_index, face) in enumerate(self.faces):

                    # Si la facette existe
                    if face is not None:
                        # Liste des points d'une facette
                        L = [face.a, face.b, face.c]

                        # Si le sommet courant fait parti de la facette
                        if vertex_index in L:

                            # Parcours des sommets d'une facette
                            for l in L:

                                # Si le sommet de la facette n'appartient pas à la liste des points d'un patch
                                # et n'est pas le comme courant
                                if l not in liste_points+[vertex_index]:
                                    # on ajoute le point à la liste de points d'un patch
                                    liste_points.append(l)
                                # fin sommet courant n'appartient pas dans les points d'un patch
                            # fin parcours des sommets d'une facette
                        # fin de sommet courant fait parti de la facette
                    # fin facette existe
                # fin parcours facettes

                # Si le nombre de points d'un patch est supérieur ou égal à 5 (on ne travaille pas sur des patchs de taille inférieure
                # à 5)
                if len(liste_points) >= 5:

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
            # fin sommet existe
        # fin du parcours des sommets


        # Construit la liste des indices par ordre décroissant de distance
        indices_tries = [i[0] for i in sorted(enumerate(distances), key=lambda x:x[1], reverse=True)]
        # distance seuil égale à 90% de la distance maximale 
        d0 = 0.75 * distances[indices_tries[0]]
        # Si un sommet d'une facette est supprimé, il faut conserver les autres sommets de la facette
        dont_touch = []
        # Parcours des indices des sommets triés par distance
        i = 0

        # Définition de la liste des sommets supprimés 
        deleted_vertices = []
        # Recherche d'un sommet dont la distance est inférieure à d0
        while i < len(indices_tries) and distances[indices_tries[i]] > d0 :
            # Si le sommet courant peut être supprimé
            if index_vertices[indices_tries[i]] not in dont_touch:
                # ajout du sommet supprimé à la liste des suppressions
                deleted_vertices.append(index_vertices[indices_tries[i]])
                # ajout de la liste des voisins qui ne doivent pas être supprimés
                dont_touch.append(voisins_vertices[indices_tries[i]])
            # fin sommet courant peut être supprimé
            # passage au sommet suivant
            i += 1
        # fin recherche sommet dont la distance est inférieure à d0
        return deleted_vertices                     
                
                
                

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
