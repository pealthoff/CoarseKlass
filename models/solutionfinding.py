#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint

import numpy as np
import scipy.sparse as sp

from gnetmine_bnoc import GNetMine


class SolutionFinding:

    def __init__(self, graph, **kwargs):

        prop_defaults = {}

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.graph = graph
        self.solution = None

    def naive_community_detection(self):
        self.solution = range(self.graph.vcount())

    def gnetmine(self):
        def desencapsular(propriedade):
            try:
                while True:
                    propriedade = propriedade[0]
            except TypeError:
                return propriedade
        types_array = self.graph.vs.get_attribute_values('type')
        types = {id + 1: type for id, type in enumerate(types_array)}

        k = len(self.graph['vertices'])
        offset = [sum(self.graph['vertices'][0: i]) for i in range(k)]

        matrices = {}
        for edge in self.graph.es():
            vertice1 = self.graph.vs[edge.tuple[0]]
            type1 = vertice1['type']
            name1 = desencapsular(vertice1['name'])
            vertice2 = self.graph.vs[edge.tuple[1]]
            type2 = vertice2['type']
            name2 = desencapsular(vertice2['name'])

            if str(type1) not in matrices:
                matrices[str(type1)] = {}
            if str(type2) not in matrices[str(type1)]:
                matrices[str(type1)][str(type2)] = np.zeros((self.graph['vertices'][type1], self.graph['vertices'][type2]), dtype=int)

            matrices[str(type1)][str(type2)][name1-offset[type1]][name2-offset[type2]] = edge['weight']

        connections = {}
        for x1 in matrices:
            for x2 in matrices[x1]:
                R = sp.csc_matrix(matrices[x1][x2])

                D1 = np.diag(np.array(np.power(R.sum(axis=1), -0.5)).flatten())
                D2 = np.diag(np.array(np.power(R.sum(axis=0), -0.5)).flatten())

                out = sp.csc_matrix(D1) * R * sp.csc_matrix(D2)

                connections[x1+x2], connections[x2+x1] = out, sp.csc_matrix.transpose(out)

        labels = {}
        for vertex in self.graph.vs():
            name = desencapsular(vertex['name'])
            # ainda nao entendi pq source eh uma lista, mas eh assim q o uncoarsening faz
            for source in vertex['source']:
                if self.labels_true[source] != -1:
                    labels[name+1] = int(self.labels_true[source])

        labels_por_particao = {str(i): {} for i in range(k)}
        for id in labels:
            labels_por_particao[str(types[id])][id] = labels[id]

        if self.particao_principal:
            for particao in range(1, k):
                del labels_por_particao[str(particao)]

        y, multilabel_y = GNetMine(connections, self.graph['vertices'], 100,
                                   labels=labels_por_particao)

        # y ta dividido por particao, vou retornar soh da particao principal
        self.solution = y['0']
