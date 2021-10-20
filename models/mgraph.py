#!/usr/bin/env python3
# coding: utf-8

"""
MFKN: Multilevel framework for kpartite networks

::K-partite data structure

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

import numpy

from igraph import Graph
# from mlp import MultiLabelPropagation

__maintainer__ = 'Alan Valejo'
__email__ = 'alanvalejo@gmail.com'
__author__ = 'Alan Valejo'
__credits__ = ['Alan Valejo']
__homepage__ = 'https://www.alanvalejo.com.br'
__license__ = 'GNU.GPL.v3'
__docformat__ = 'markdown en'
__version__ = '0.1'
__date__ = '2020-05-05'

def load_ncol(filename):
    """
    Load ncol npartite graph and generate special attributes
    """

    data = numpy.loadtxt(filename, skiprows=0, dtype=str)
    dict_edges = dict()
    for row in data:
        if len(row) == 3:
            dict_edges[(int(row[0]), int(row[1]))] = float(row[2])
        else:
            dict_edges[(int(row[0]), int(row[1]))] = 1

    edges, weights = list(zip(*dict_edges.items()))
    return edges, weights

class MGraph(Graph):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, filename, filetype='ncol', vertices=None, type_filename=None):
        """
        filename_type: ncol, arff
        """

        edges, weights = None, None
        if filetype == 'ncol':
            edges, weights = load_ncol(filename)

        if vertices:
            self.add_vertices(sum(vertices))
            self['layers'] = len(vertices)
            types = []
            for layer in range(self['layers']):
                types += [layer] * vertices[layer]
            self.vs['type'] = types
        elif type_filename:
            types = numpy.loadtxt(type_filename, skiprows=0, dtype=int)
            self.add_vertices(len(types))
            self.vs['type'] = types
            unique, vertices = numpy.unique(types, return_counts=True)
            self['layers'] = len(vertices)
        else:
            print('Please provide the number of vertices for each layer or a file with types.')
            exit()

        self.add_edges(edges)
        self['adjlist'] = list(map(set, self.get_adjlist()))
        self['vertices'] = list(vertices)
        self['level'] = [0] * self['layers']
        self['similarity'] = None
        self.es['weight'] = weights
        for v in self.vs():
            v['weight'] = 1
            v['source'] = [v.index]
            v['name'] = [v.index]
            v['predecessor'] = [v.index]
            v['successor'] = [None]

        self['vertices_by_type'] = []
        for layer in range(self['layers']):
            self['vertices_by_type'].append(self.vs.select(type=layer).indices)

        # Not allow direct graphs
        if self.is_directed():
            self.to_undirected(combine_edges=True)

    def number_of_components(self):
        components = self.components()
        components_sizes = components.sizes()
        return len(components_sizes)
