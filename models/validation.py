#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MFKN: Multilevel framework for kpartite networks

::Validate

Copyright (C) 2020 Alan Valejo <alanvalejo@gmail.com> All rights reserved

This program comes with ABSOLUTELY NO WARRANTY. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS
WITH YOU.

Owner or contributors are not liable for any direct, indirect, incidental, special, exemplary, or consequential
damages, (such as loss of data or profits, and others) arising in any way out of the use of this software,
even if advised of the possibility of such damage.

This program is free software and distributed in the hope that it will be useful: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with this program. If not,
see http://www.gnu.org/licenses/.

Giving credit to the author by citing the papers.
"""

__maintainer__ = 'Alan Valejo'
__email__ = 'alanvalejo@gmail.com'
__author__ = 'Alan Valejo'
__credits__ = ['Alan Valejo']
__homepage__ = 'https://www.alanvalejo.com.br'
__license__ = 'GNU.GPL.v3'
__docformat__ = 'markdown en'
__version__ = '0.1'
__date__ = '2020-05-05'

import csv
import json
import numpy

from sklearn import metrics
from collections import defaultdict, Counter

def number_external_edges(G):
    """ Number of external edges """

    ext_edges = 0.0
    for e in G.es():
        v = e.tuple[0]
        u = e.tuple[1]
        if G.vs['membership'][v] != G.vs['membership'][u]:
            ext_edges += G[v, u]

    return ext_edges

def internal_external_edges(G):
    """ External edges """

    comms = numpy.unique(G.vs['membership'])
    k = len(comms)
    init = [0.0] * k
    ext_edges = dict(zip(comms, init))
    int_edges = dict(zip(comms, init))
    for e in G.es():
        u = e.tuple[0]
        v = e.tuple[1]
        ku = G.vs['membership'][u]
        kv = G.vs['membership'][v]
        if ku != kv:
            ext_edges[ku] += 1
            ext_edges[kv] += 1
        else:
            int_edges[ku] += 1

    return int_edges, ext_edges, k, comms

def conductance(G):
    """
    Conductance is the ratio between the (weighted) number of external
    (boundary) edges in a cluster and the cluster's total (weighted) number
    of edges
    """

    rv = []
    int_edges, ext_edges, k, comms = internal_external_edges(G)
    for i in comms:
        denominator = int_edges[i] + ext_edges[i]
        if denominator > 0:
            rv.append(ext_edges[i] / denominator)

    return sum(rv) / len(rv)

def barber_modularity(B, m, R, T):
    RtBT = R.transpose().dot(B.dot(T))
    Qcoms = (1 / m) * (numpy.diagonal(RtBT))
    Q = sum(Qcoms)
    Qcoms = Qcoms[Qcoms > 0]
    return Q

def Qbip(w, gg, gh):
    """ Bipartite modularity sensu Barber
    Good candidate for a C version """

    gen = numpy.sum(w, axis=1)
    vul = numpy.sum(w, axis=0)
    tQ = 0.0
    for i in range(len(w)):
        for j in range(len(w[0])):
            if gg[i] == gh[j]:
                print('oi')
                tQ += (w[i][j] - (gen[i]*vul[j])/float(numpy.sum(w)))

    return tQ / float(numpy.sum(w))

def murata_modularity(graph, type_a=0, type_b=1):
    """
    New Modularity for Evaluating Communities in Bipartite Networks
    Tsuyoshi Murata, 2009
    :param graph: input bipartite graph
    :return: float murata modularity
    """

    top = graph.vs.select(type=type_a).indices
    bottom = graph.vs.select(type=type_b).indices
    top_coms = defaultdict(set)
    bottom_coms = defaultdict(set)

    for v in top:
        top_coms[graph.vs['membership'][v]].add(v)
    for v in bottom:
        bottom_coms[graph.vs['membership'][v]].add(v)

    topC_to_bottomC = dict()
    topC_to_V = dict()
    bottomC_to_topC = dict()
    bottomC_to_V = dict()

    for c, v in top_coms.items():
        c_count = Counter()
        for u in v:
            for neig in graph.neighbors(u):
                c_count.update({graph.vs['membership'][neig]: 1})
        topC_to_bottomC[c] = c_count
        topC_to_V[c] = sum(c_count.values())
    for c, v in bottom_coms.items():
        c_count = Counter()
        for u in v:
            for neig in graph.neighbors(u):
                c_count.update({graph.vs['membership'][neig]: 1})
        bottomC_to_topC[c] = c_count
        bottomC_to_V[c] = sum(c_count.values())

    E = graph.ecount()
    Q_top = 0
    Q_bottom = 0
    # top -> bottom
    for Ck, coms in topC_to_bottomC.items():
        if coms: # for graph with unconnected components
            Cl = max(coms, key=coms.get)
            Q_top += (coms[Cl] / (2 * E) - topC_to_V[Ck] * bottomC_to_V[Cl] / (4 * E * E))
    # bottom -> top
    for Ck, coms in bottomC_to_topC.items():
        if coms: # for graph with unconnected components
            Cl = max(coms, key=coms.get)
            Q_bottom += (coms[Cl] / (2 * E) - bottomC_to_V[Ck] * topC_to_V[Cl] / (4 * E * E))
    return Q_top + Q_bottom

class Validation:

    def __init__(self, graph, labels_true, labels_pred, schema, **kwargs):

        prop_defaults = {'format': '{:.3f}'}

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.graph = graph
        self.labels_true = labels_true
        self.labels_pred = labels_pred
        self.schema = schema
        # self.header = [''] + list(map(str, range(self.graph['layers']))) + ['Average']
        self.header = ['', 'alvo']
        self.rows_name = []
        self.rows_value = []

        self.labels_pred_split = []
        self.labels_true_split = []
        for layer in range(self.graph['layers'])[:1]:
            indices = graph.vs.select(type=layer).indices
            indices_with_label_true = [i-1 for i in indices if labels_true[i-1]!=-1]
            self.labels_pred_split.append(labels_pred[indices_with_label_true])
            self.labels_true_split.append(labels_true[indices_with_label_true])

    def compute_accuracy(self, label=''):
        args = []
        for layer in range(self.graph['layers'])[:1]:
            args.append(metrics.accuracy_score(self.labels_true_split[layer], self.labels_pred_split[layer]))

        average = sum(args) / len(args)
        args.append(average)
        for key, value in enumerate(args):
            args[key] = self.format.format(args[key])

        self.rows_name.append('accuracy' + label)
        self.rows_value.append(args)

    def print_tabular(self):
        max_row = max(self.rows_name + self.header, key=len)
        format_str = '{:>' + str(len(max_row) + 1) + '}'
        row_format = format_str * (len(self.header))
        print(row_format.format(*self.header))
        for row, item in zip(self.rows_name, self.rows_value):
            print(row_format.format(row, *item))

    def save_csv(self, output):
        with open(output, 'w+') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.header)
            for row, item in zip(self.rows_name, self.rows_value):
                writer.writerow([row] + item)

    def save_json(self, output):
        dictionary = dict(zip(self.rows_name, self.rows_value))
        dictionary['header'] = self.header
        with open(output, 'w+') as jsonfile:
            json.dump(dictionary, jsonfile, indent=4)
