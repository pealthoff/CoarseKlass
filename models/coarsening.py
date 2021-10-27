#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MFKN: Multilevel framework for kpartite networks

::Coarsening

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

import math
import sys
import numpy

def modified_starmap_async(function, kwargs):
    return function(**kwargs)

class Coarsening:

    def __init__(self, source_graph, **kwargs):

        prop_defaults = {
            'reduction_factor': None, 'max_levels': None, 'max_size': None
        }

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.source_graph = source_graph
        self.graph_hierarchy = []
        self.level_hierarchy = []

        self.validate()

    def validate(self):

        # Validation of list values
        for prop_name in ['reduction_factor', 'max_levels', 'max_size']:
            if isinstance(getattr(self, prop_name), list):
                if len(getattr(self, prop_name)) == 1:
                    setattr(self, prop_name, [getattr(self, prop_name)[0]] * self.source_graph['layers'])
            elif getattr(self, prop_name):
                setattr(self, prop_name, [getattr(self, prop_name)] * self.source_graph['layers'])

        # Parameters dimension validation
        for prop_name in ['reduction_factor', 'max_levels', 'max_size']:
            if getattr(self, prop_name) and self.source_graph['layers'] != len(getattr(self, prop_name)):
                print('Number of layers and ' + str(prop_name) + ' do not match.')
                sys.exit(1)

    def run(self):

        graph = self.source_graph
        self.graph_hierarchy.append(graph)
        self.level_hierarchy.append(graph)

        while True:

            if self.reduction_factor != [None] * graph['layers']:
                graph.max_size = []
                for layer in range(graph['layers']):
                    size = int(math.ceil(graph['vertices'][layer] * (1.0 - self.reduction_factor[layer])))
                    if self.max_size[layer] and size < self.max_size[layer]:
                        size = self.max_size[layer]
                    graph.max_size.append(size)
            else:
                graph.max_size = self.max_size

            # print('before max size', graph['vertices'], graph.max_size)

            graph.run()
            matching = numpy.array(graph.vs['label'])
            coarsened_graph = graph.contract(matching)

            coarsened_graph['level'] = graph['level']
            for layer in range(graph['layers']):
                if coarsened_graph['vertices'][layer] < graph['vertices'][layer]:
                    coarsened_graph['level'][layer] += 1

            self.graph_hierarchy.append(coarsened_graph)
            self.level_hierarchy.append(coarsened_graph['level'][:])

            if self.max_levels and coarsened_graph['level'] == self.max_levels:
                break
            elif self.max_size and coarsened_graph['vertices'] <= self.max_size:
                break
            elif coarsened_graph['vertices'] == graph['vertices']:
                break

            graph = coarsened_graph

            # print('after max size', graph['vertices'], graph.max_size)

            if graph.until_convergence:
                break
