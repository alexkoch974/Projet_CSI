#!/usr/bin/env python

# from ssl import VERIFY_X509_PARTIAL_CHAIN
import obja
import numpy as np
import sys

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
        sommets = [6,7] # sommets 7 et 8 du mesh
        (patch, faces) = self.find_patches(sommets)
        print(patch)
        print(faces)
        
        
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
        # Pour chaque sommet à supprimer
        for vert_index in vertices_to_delete:   
            
            # Iterate through the faces and store them temporarily
            # Pour chaque facette
            for face in self.faces:
                # Si le sommet courant est un des sommets de la facette courante
                if vert_index in [face.a, face.b, face.c]:
                    # Ajout de la facette courante dans la liste intermédiaire
                    temp_faces_list.append(face)

            # ensemble des facettes du patch
            faces_in_the_patches.append(list(temp_faces_list))

            # CP : pourquoi uniquement la première facette de la liste ?
            # Si le sommet courant est le premier de la première facette
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
            
def trace_Z(self, patches, vertices_to_delete):
    """
    Fonction qui effectue les modification sur le mesh. Plus précisément supprime les
    points des milieus de patchs et trace les Z.
    
    arguments : - liste des patchs (liste de liste d'indices de sommets de contour)
                - liste des sommets a supprimer (liste d'indices de sommets)
                - liste des faces dans les patchs (liste de liste de face)
    
    retour :    - liste des opérations à effectuer (list de string)   
    """        
    operations = []      
    
    for i in range(len(patches)):
        
        # Deleting the vertex in the middle of the patch
        
        
                            
                            
                
                
                

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Test()
    model.parse_file('example/test.obj')

    # with open('example/etoile_test.obja', 'w') as output:
    #     model.compressionne(output)

    output = 1
    model.compressionne(output)

if __name__ == '__main__':
    main()
