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

# bibliothèque pour manipuler les maillages au format obja
import obja


class Compresseur(obja.Model):
    """
    Classe qui hérite de la classe Model de la bibliothèque obja pour représenter un maillage et 
    fournir une opération de compression.
    """

    # Attribut qui mémorise les facettes composant un patch dans l'ordre du contour    
    faces_rec = []
    # Attribut qui compte le nombre d'étapes de compression effectuées
    tour = 1
        
    def __init__(self):
        super().__init__()
        
    def comprimer(self,output):
        """
        Comprimer un maillage au format obj en maillage au format obja.
        """

        # Séquence d'operations pour créer le maillage au format obja
        opérations = []  
        
        while self.tour < 60:
            # print("tour n° " + str(self.tour) + "\n")
            # Etape 1 : trouver les sommets à supprimer 
            sommets = find_vertices_to_delete(self)
            
            # Etape 2 : Ordonner les patchs et décimer
            (patchs, faces) = self.find_patches(sommets)
            opérations = trace_Z(self, patchs, faces, sommets, opérations)
            
            output_model = obja.Output(output, random_color=True)

            self.tour += 1
            
                    


        # Après la compression, on sauvegarde l'état le plus compressé
        # Pour chaque facette contenue dans le maillage
        for (index, face) in enumerate(self.faces):
            # Si la facette existe
            if face is not None:
                # Ajout de l'opération de création de facette
                opérations.append(('afnc', index, face))
        # Pour chaque somme contenu dans le maillage
        for (index, vertex) in enumerate(self.vertices):
            # Si le somme existe
            if vertex is not None:
                # Ajout de l'opération de création de sommet
                opérations.append(('av', index, vertex))
        
        # Inverse de l'ordre des opérations de compression pour simuler la décompression
        opérations.reverse()
        
        
        # Ecriture du fichier .obja
        # Pour chaque opération
        for (ty, index, value) in opérations:
            # cas de l'ajout d'un sommet
            if ty == 'av':
                output_model.add_vertex(index, value)
            # cas de l'ajout d'une facette
            elif ty == 'afnc':
                output_model.add_face(index, value)
            # cas de l'ajout de la couleur d'une facette
            elif ty == 'af':
                output_model.add_face_color(index, value)
            # cas de la modification d'une facette
            elif ty == 'ef':
                output_model.edit_face(index, value)
        
  
        
    def sort_patch_rec(self, list_faces, del_vert, vert_prec):
        """
        Fonction récursive qui construit le contour du patch dans l'ordre souhaité à partir
        de la liste des facettes, du sommet au centre du patch à supprimer et du sommet
        précédent dans le contour.
        (L'ordre se décide lors de l'appel de la fonction avec le paramètre vert_prec)
        Paramètres :
            list_faces : facettes du patch
            del_vert : sommet du patch à supprimer
            vert_prec : sommet précédent dans l'ordre souhaité pour le contour
        """
        # une liste vide est ordonnée (liste vide de facettes : cas d'arrêt de la fonction)
        if list_faces == []:
            return []
        else:
            # Pour chaque facette qui n'a pas encore été traitée
            for ind_face in range(len(list_faces)):
                # valeur de la facette courante
                (face,_) = list_faces[ind_face]
                # sommets de la facette courante
                verts_face = [face.a, face.b, face.c]
                # si le sommet à supprimer fait partie de la facette courante
                # remarque : c'est toujours le cas car ce sont les facettes d'un patch et le sommet est au centre du patch
                # et le sommet précédent fait aussi partie de la facette courante
                # remarque : cela permet de trouver la facette concernée par cette itération (la suivante)
                if del_vert in verts_face and vert_prec in verts_face:
                    # Pour chaque sommet de la facette courante
                    for vertex in verts_face:
                        # Si le sommet courant n'est pas le sommet à supprimer ni le sommet précédent
                        # cela permet d'obtenir le sommet suivant dans le contour
                        if vertex != del_vert and vertex != vert_prec:
                            # La facette courante fait partie du patch (conservée dans variable partagée)
                            # ceci permet d'ordonner les facettes dans le même ordre que le contour
                            self.faces_rec.append(list_faces[ind_face])
                            # Suppression de la facette courante
                            list_faces.pop(ind_face)
                            # Ajout du sommet courant dans le contour du patch
                            # ce sommet courant devient le précédent dans l'appel récursif
                            return [vertex] + self.sort_patch_rec(list_faces, del_vert, vertex)
                    
    def find_patches(self, vertices_to_delete):
        """
        Fonction qui retourne les patchs et points à supprimer à partir de
        ces points.
        Il s'agit de l'étape de compression juste avant de dessiner les Z.
        
        arguments : - liste d'indices de sommets (au milieu des patchs) à supprimer
        
        retour :    - patches : liste des patchs (liste de liste d'indices de sommets)  
                    - faces_in_the_patches : liste des faces dans les patchs (liste de listes de facettes) 
        """
        # liste des patches
        patches = []
        # liste intermédiaire de facettes concernées par la suppression d'un des sommets
        temp_faces_list = []
        # facettes qui composent chaque patch : liste de listes de facettes
        faces_in_the_patches = []
        
        # Pour chaque sommet à supprimer
        for vert_index in vertices_to_delete:   
            
            # Vide la variable partagée qui mémorise les facettes du patch dans l'ordre
            self.faces_rec.clear()            
            # Pour chaque indice de facette du maillage
            for ind_face in range(len(self.faces)):
                # Valeur de la facette associée à l'indice courant
                face = self.faces[ind_face]
                # Si la facette courante existe
                if face is not None:
                    # Si le sommet à supprimer est un des sommets de la facette
                    if vert_index in [face.a, face.b, face.c]:
                        # La facette courante possède le sommet à supprimer courant
                        # On la conserve avec son indice absolue dans le modèle
                        temp_faces_list.append((face,ind_face))
            
            # Le sommet courant à supprimer fait partie de chaque facette de la liste
            # La première facette de la liste est traitée différement des suivantes
            # Si le sommet courant est le premier sommet de la première facette
            if vert_index == temp_faces_list[0][0].a:
                # le précédent est le dernier de la première facette
                prec_vertex = temp_faces_list[0][0].c
            # Si le sommet courant est le second sommet de la première facette
            elif vert_index == temp_faces_list[0][0].b:
                # le précédent est le premier de la première facette
                prec_vertex = temp_faces_list[0][0].a
            # le sommet courant est alors le troisième sommet de la première facette
            else:
                # le précédent est le second de la première facette
                prec_vertex = temp_faces_list[0][0].b

            # Il faut traiter les autres facettes
            # et on range les facettes dans le même ordre que le contour du patch
            contour_patch = self.sort_patch_rec(temp_faces_list, vert_index, prec_vertex)

            # ajoute la liste des sommets du patch à la liste des patchs
            patches.append(contour_patch)
            faces_in_the_patches.append(list(self.faces_rec))
            
        return (patches, faces_in_the_patches)


def trace_Z(self, patches, faces_in_the_patches, vertices_to_delete, operations):
    """
    Fonction qui effectue les modification sur le maillage. Plus précisément, elle supprime les
    points du centre des patchs puis construit les facettes en Z qui maille le patch sans centre.
    
    arguments : - liste des patchs (liste de liste d'indices de sommets de contour)
                - liste des facettes dans les patchs (liste de liste de tuples (face,indice) )
                - liste des sommets au milieu des patchs à supprimer (liste d'indices de sommets)
    
    retour :    - liste des opérations à effectuer (liste de string)   
    """   
    
    # Dans cette fonction, remplacer les 'afnc' par 'af' pour voir les ajout de faces de chaque 
    # itération de compression en couleur.
    
    # Pour chaque indice de patch
    for ind_patch in range(len(patches)):
        # Patch courant : suite de sommets qui forment le contour du patch
        patch = patches[ind_patch]
        # Sommet qui doit être supprimé
        vert_del = vertices_to_delete[ind_patch]
        
        # Etape 1 : Suppression des deux faces symétriques l'une de l'autre par rapport au sommet central
        # suppression des 2 facettes opposées (numéro 0 et n/2)
        # il y en a au moins 2 car les patchs contiennent au moins 5 facettes
        n_sur_2 = math.ceil(len(faces_in_the_patches[ind_patch])/2)
        # Ajout de l'opération d'ajout de facette non colorée
        operations.append(('afnc', faces_in_the_patches[ind_patch][0][1], faces_in_the_patches[ind_patch][0][0]))
        # Indices ndes facettes à supprimer
        ind_to_del = self.faces.index(faces_in_the_patches[ind_patch][0][0])
        # Suppression des facettes concernées
        self.faces[ind_to_del] = None
        # Ajout de l'opération d'ajout de facette non colorée
        operations.append(('afnc', faces_in_the_patches[ind_patch][n_sur_2][1], faces_in_the_patches[ind_patch][n_sur_2][0]))
        # Indices des facettes à supprimer
        ind_to_del = self.faces.index(faces_in_the_patches[ind_patch][n_sur_2][0])
        # Suppression des facettes concernées
        self.faces[ind_to_del] = None
            
        # Etape 2 : Modification des facettes restantes du patch pour faire apparaitre le Z
        # Pour chaque indice de facette dans le patch courant
        for ind_face in range(len(faces_in_the_patches[ind_patch])):
            # facette courante et son indice dans le patch (TODO CP : c'est à dire)
            (face, index) = faces_in_the_patches[ind_patch][ind_face]
            # si la facette de l'indice courant n'est pas vide (TODO CP : c'est à dire)
            # ce n'est pas une facette qui a déjà été supprimée
            if self.faces[index] is not None: 
                # modifier les n - 2 facettes restantes du patch courant

                # si le sommet à supprimer est le sommet a de la facette           
                if vert_del == face.a:
                    # si la position dans le contour du patch du sommet b de la facette courante est 0
                    # il s'agit d'une facette adjacente à la facette 0 du patch
                    if patch.index(face.b) == 0 :
                        # création d'une nouvelle facette à partir des sommets b, c et du
                        # sommet obtenu dans le contour de la facette à partir de l'indice
                        # de c dans le contour
                        new_face = obja.Face(face.b, face.c, patch[-patch.index(face.c)])
                    # si la position dans le patch du sommet b de la facette courante est n / 2
                    # il s'agit d'une facette adjacente à la facette n / 2 du patch                        
                    elif patch.index(face.b) == n_sur_2:
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

                    # si la position dans le patch du sommet c de la facette courante est 0
                    # il s'agit d'une facette adjacente à la facette 0 du patch                   
                    if patch.index(face.c) == 0 :
                        # création d'une nouvelle facette à partir des sommets c, a et d'un sommet symétrique à a
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    # si la position dans le patch du sommet c de la facette courante est n / 2
                    # il s'agit d'une facette adjacente à la facette n / 2 du patch
                    elif patch.index(face.c) == n_sur_2:
                        # création d'une nouvelle facette à partir des sommets b, c et d'un sommet symétrique à a
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.a)])
                    #
                    else:
                        # création d'une nouvelle facette à partir des sommets c, a et d'un sommet symétrique à c
                        new_face = obja.Face(face.c, face.a, patch[-patch.index(face.c)])


                # si le sommet à supprimer est le sommet c de la face
                elif vert_del == face.c:
                    # si la position dans le patch du sommet a de la facette courante est 0
                    # il s'agit d'une facette adjacente à la facette 0 du patch 
                    if patch.index(face.a) == 0 :
                        # création d'une nouvelle facette à partir des sommets a, b et d'un sommet symétrique à b
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    # si la position dans le patch du sommet a de la facette courante est n / 2
                    # il s'agit d'une facette adjacente à la facette n / 2 du patch
                    elif patch.index(face.a) == n_sur_2:
                        # création d'une nouvelle facette à partir des sommets a, b et d'un sommet symétrique à b
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.b)])
                    #
                    else:
                        # création d'une nouvelle facette à partir des sommets a, b et d'un sommet symétrique à a
                        new_face = obja.Face(face.a, face.b, patch[-patch.index(face.a)])

                # sinon : Ce cas n'est pas possible
                else:
                    print("ERREUR : patch non conforme")

                # Ajout de l'opération que effacer la face à l'indice
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
    model = Compresseur()
    model.parse_file('example/suzanne.obj')

    with open('example/suzanne.obja', 'w') as output:
        model.comprimer(output)
    

if __name__ == '__main__':
    main()
