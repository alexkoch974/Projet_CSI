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
        patch = self.find_patches(sommets)
        print(patch)
        
        
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
            for f in list_faces:
                verts_f = [f.a, f.b, f.c]
                if del_vert in verts_f and vert_prec in verts_f:
                    for v in verts_f:
                        if v != del_vert and v != vert_prec:
                            list_faces.remove(f)
                            return [v] + self.sort_patch_rec(list_faces, del_vert, v)
                    
    def find_patches(self, vertices_to_delete):
        """
        Fonction qui retourne les patchs et points à supprimer à partir de
        ces points.
        Il s'agit de l'étape de compression juste avant de dessiner les Z.
        
        arguments : - liste d'indices de sommets (au milieu des patchs) à supprimer
        
        retour :    - patches : liste des patchs (liste de liste d'indices de sommets)   
        """
        patches = []
        temp_faces_list = []
        
        
        # Iterate through the vertices to delete
        # ----------- TODO : check avec Kuremon pour avoir des index
        for vert_index in vertices_to_delete:   
            
            # Iterate through the faces and store them temporarily
            for face in self.faces:
                if vert_index in [face.a, face.b, face.c]:
                    temp_faces_list.append(face)
                    print([face.a, face.b, face.c])
            print(len(temp_faces_list))

            if vert_index == temp_faces_list[0].a:
                vertex_to_store = temp_faces_list[0].b
                next_vertex = temp_faces_list[0].c
            elif vert_index == temp_faces_list[1].b:
                vertex_to_store = temp_faces_list[0].c
                next_vertex = temp_faces_list[0].a
            else:
                vertex_to_store = temp_faces_list[0].a
                next_vertex = temp_faces_list[0].b
            
            patch = self.sort_patch_rec(temp_faces_list, vert_index, next_vertex)
            
            patches.append(patch)
        
        return patches
            
def trace_Z(self, patches):
    """
    Fonction qui effectue les modification sur le mesh. Plus précisément supprime les
    points des milieus de patchs et trace les Z.
    
    arguments : - liste des patchs (liste de liste d'indices de sommets de contour)
    
    retour :    - liste des opérations à effectuer (list de string)   
    """              
                            
                            
                
                
                

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
        