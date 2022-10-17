#!/usr/bin/env python

import os
import obja
import numpy as np
import sys

class Decimater(obja.Model):
    """
    Decimation procedure derived from article ???.
    """
    def __init__(self):
        super().__init__()
        # collect delected faces
        self.deleted_faces = set()

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
                A = np.ones(len(liste_points)+1, 4)
                # Première ligne initialisée avec le sommet courant
                A[0, 0:3] = vertex
                # Parcours des points du patch par indice (i) et valeur (l)
                for (i, l) in enumerate(liste_points):
                    # i-ème ligne initialisée avec les sommets du patch
                    A[i+1, 0:3] = self.vertices[l]
                # fin parcours des points du patch
                tAA = A.transpose * A

                # Calcul des vecteurs propres et valeurs prorpes 
                valeurs_propres, vecteurs_propres = np.linalg.eig(tAA)
                # Indice de la plus petite valeur propre
                ind = np.argmin(valeurs_propres)
                # Vecteur propre associé à la plus petite valeur propre
                X = vecteurs_propres[:, ind]
                # Calcul de
                n = np.array(X[0:3])
                # Calcul de la distance entre le sommet courant (vertex) et le plan moyen
                k = (- X[3] - n.transpose * vertex) / np.linalg.norm(vertex)
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
        # TODO : tampon n'est pas défini pour l'instant...
        if len(tampon) < len(self.vertices):
            return deleted_vertices
        else:
            return []



    def contract(self, output):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """
        operations = []

        for (vertex_index, vertex) in enumerate(self.vertices):
            operations.append(('ev', vertex_index, vertex + 0.25))

        # Iterate through the vertex
        for (vertex_index, vertex) in enumerate(self.vertices):

            # Iterate through the faces
            for (face_index, face) in enumerate(self.faces):

                # Delete any face related to this vertex
                if face_index not in self.deleted_faces:
                    if vertex_index in [face.a,face.b,face.c]:
                        self.deleted_faces.add(face_index)
                        # Add the instruction to operations stack
                        operations.append(('face', face_index, face))

            # Delete the vertex
            operations.append(('vertex', vertex_index, vertex))

        # To rebuild the model, run operations in reverse order
        operations.reverse()

        # Write the result in output file
        output_model = obja.Output(output, random_color=True)

        for (ty, index, value) in operations:
            if ty == "vertex":
                output_model.add_vertex(index, value)
            elif ty == "face":
                output_model.add_face(index, value)   
            else:
                output_model.edit_vertex(index, value)

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Decimater()
    model.parse_file(os.path('example','suzanne.obj'))

    with open(os.path('example','suzanne.obja'), 'w') as output:
        model.contract(output)


if __name__ == '__main__':
    main()
