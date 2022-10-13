#!/usr/bin/env python

import os
import obja
import numpy as np
import sys

class Decimater(obja.Model):
    """
    A simple class that decimates a 3D model stupidly.
    """
    def __init__(self):
        super().__init__()
        self.deleted_faces = set()

    def decimaton(self):
        distances = []
        index_vertices = []
        voisins_vertices = []
        for (vertex_index, vertex) in enumerate(self.vertices):
            liste_points = []
            for (face_index, face) in enumerate(self.faces):
                L = [face.a, face.b, face.c]
                if vertex_index in L:
                    for l in L:
                        if l not in liste_points+[vertex_index]:
                            liste_points.append(l)
            if len(liste_points) > 4:
                A = np.ones(len(liste_points)+1, 4)
                A[0, 0:3] = vertex
                for (i, l) in enumerate(liste_points):
                    A[i+1, 0:3] = self.vertices[l]
                tAA = A.transpose*A
                lambdas, vecteurs_propres = np.linalg.eig(tAA)
                ind = np.argmin(lambdas)
                X = vecteurs_propres[:, ind]
                n = np.array(X[0:3])
                k = (-X[3]-n.transpose*vertex)/np.linalg.norm(vertex)
                distances.append(abs(k))
                index_vertices.append(vertex_index)
                voisins_vertices.append(liste_points[:])



        indices_tries = [i[0] for i in sorted(enumerate(distances), key=lambda x:x[1], reverse=True)]
        d0 = 0.9*distances[indices_tries[0]]
        dont_touch = []
        i = 0
        deleted_vertices = []
        while distances[indices_tries[i]] > d0 and i < len(indices_tries):
            if index_vertices[indices_tries[i]] not in dont_touch:
                deleted_vertices.append(index_vertices[indices_tries[i]])
                dont_touch.append(voisins_vertices[indices_tries[i]])
            i += 1
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
