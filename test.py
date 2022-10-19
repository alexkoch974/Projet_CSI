#!/usr/bin/env python

# from ssl import VERIFY_X509_PARTIAL_CHAIN
from dis import dis
from re import A
import obja
import numpy as np
import sys
import math

class Test(obja.Model):
    """
    A test class that decimates a 3D model with arbitrary triangle meshes.
    """
    
    def __init__(self):
        super().__init__()
        self.deleted_faces = set()
        
    def compressionne(self,output):
        """
        Compressionne un obj en obja.
        """
        # sommets = [6] # sommet 7 du mesh
        sommets = decimation(self)
        print(sommets)
        (patch, faces) = self.find_patches(sommets)
        print(patch)
        print(faces)
        op = trace_Z(self, patch, faces)
        print(op)
        op.reverse()
        
        output_model = obja.Output(output, random_color=True)

        for i in patch:
            for j in i:
                op.append(("vertex",j,self.vertices[j]))
                output_model.add_vertex(j,self.vertices[j])
                        
        for (ty, value, index) in op:
            if ty == "df":
                output_model.del_face(index)
            elif ty == "af":
                output_model.add_face(index,value)
        
        
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
            # Pour chaque facette
            for f in list_faces:
                # liste des sommets de la facette courante
                verts_f = [f.a, f.b, f.c]
                # si le sommet à supprimer fait parti de la facette courante
                # et le sommet précédent fait aussi parti de la facette courante
                if del_vert in verts_f and vert_prec in verts_f:
                    # Pour chaque sommet de la facette courante
                    for v in verts_f:
                        # Si le sommet courant n'est pas le sommet à supprimer ni le sommet précédent
                        if v != del_vert and v != vert_prec:
                            # Suppression de la facette courante
                            list_faces.remove(f)
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
        # liste intermédiaire de facettes
        temp_faces_list = []
        # facettes du patch
        faces_in_the_patches = []
        
        
        # Iterate through the vertices to delete
        # ----------- TODO : check avec Kuremon pour avoir des index
        for vert_index in vertices_to_delete:   
            
            # Iterate through the faces and store them temporarily
            for face in self.faces:
                if vert_index in [face.a, face.b, face.c]:
                    # Ajout de la facette courante dans la liste intermédiaire
                    temp_faces_list.append(face)
            
            faces_in_the_patches.append(list(temp_faces_list))


            if vert_index == temp_faces_list[0].a:
                # le précédent est le dernier de la première facette
                next_vertex = temp_faces_list[0].c
            # Si le sommet courant est le second de la première facette
            elif vert_index == temp_faces_list[0].b: # 1 remplacé par 0 (CP)
                # le précédent est le dernier de la première facette
                next_vertex = temp_faces_list[0].a
            else:
                # le précédent est le second de la première facette
                next_vertex = temp_faces_list[0].b

            # construit la liste des sommets du patch
            patch = self.sort_patch_rec(temp_faces_list, vert_index, next_vertex)

            # ajoute la liste des sommets du patch à la liste des patchs
            patches.append(patch)
        
        return (patches, faces_in_the_patches)
            
def trace_Z(self, patches, faces_in_the_patches):
    """
    Fonction qui effectue les modification sur le mesh. Plus précisément supprime les
    points des milieus de patchs et trace les Z.
    
    arguments : - liste des patchs (liste de liste d'indices de sommets de contour)
                - liste des faces dans les patchs (liste de liste de face)
    
    retour :    - liste des opérations à effectuer (list de string)   
    """        
    operations = []      
    
    for i in range(len(patches)):
        
        index = len(self.faces) - 1
        
        # Deleting the vertex in the middle of the patch by deleting all its related faces
        for face in faces_in_the_patches[i]:
            operations.append(('df', face, face))
        
        n =  len(patches[i]) - 2
        a = -1
        b_ind = 0
        c = 1
        face = obja.Face(patches[i][a],patches[i][b_ind],patches[i][c])
        index += 1
        operations.append(('af', face, index))
        for j in range(2,n+1):
            if (j/2) == math.floor(j/2):
                b_ind += 1
                c += 1
            else:
                a -= 1
            b = pow((-1),j) * b_ind
            
            face = obja.Face(patches[i][a],patches[i][b],patches[i][c])
            index += 1
            operations.append(('af', face, index))
            
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

            # Définition de la liste des points formant le patch 
            liste_points = []

            # Parcours de l'ensemble des facettes par indice (face_index) et valeur de la facette (face)
            for (face_index, face) in enumerate(self.faces):

                # Liste des points d'une facette
                L = [face.a, face.b, face.c]

                # Si le sommet courant fait parti de la facette
                if vertex_index in L:

                    # Parcours des sommets d'une facette
                    for l in L:

                        # Si le sommet courant n'appartient pas à la liste des points d'un patch 
                        if l not in liste_points+[vertex_index]:
                            # on ajoute le point à la liste de points d'un patch
                            liste_points.append(l)
                        # fin sommet courant n'appartient pas dans les points d'un patch
                    # fin parcours des sommets d'une facette
                # fin de sommet courant fait parti de la facette

            # Si le nombre de points d'un patch est supérieur ou égal à 5 (on ne travaille pas sur des patchs de taille inférieure
            # à 5)
            if len(liste_points) >= 5:

                # Calcul des coefficients du plan moyen pour ce patch
                A = np.ones((len(liste_points)+1, 4))
                # Première ligne initialisée avec le sommet courant
                A[0, 0:3] = vertex
                # Parcours des points du patch par indice (i) et valeur (l)
                for (i, l) in enumerate(liste_points):
                    # i-ème ligne initialisée avec les sommets du patch
                    A[i+1, 0:3] = self.vertices[l]
                # fin parcours des points du patch
                tAA = A.transpose() @ A

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
        indices_tries = [i[0] for i in sorted(enumerate(distances), key=lambda x:x[1], reverse=True)]
        # distance seuil égale à 90% de la distance maximale 
        d0 = 0.9 * distances[indices_tries[0]]
        # Si un sommet d'une facette est supprimé, il faut conserver les autres sommets de la facette
        dont_touch = []
        # Parcours des indices des sommets triés par distance
        i = 0

        # Définition de la liste des sommets supprimés 
        deleted_vertices = []
        # Recherche d'un sommet dont la distance est inférieure à d0
        print(indices_tries)
        print(len(distances))
        while distances[indices_tries[i]] > d0 and i < len(indices_tries):
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
    model.parse_file('example/test.obj')

    with open('example/test.obja', 'w') as output:
        model.compressionne(output)
    

if __name__ == '__main__':
    main()
