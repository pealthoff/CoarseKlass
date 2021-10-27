#!/usr/bin/env python3
# coding: utf-8

"""
MFKN: Multilevel framework for kpartite networks

::Multi-label propagation

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

import random
import math
import sys
import copy
import numpy

from models.mgraph import MGraph
from collections import Counter
from operator import itemgetter
from heapq import nlargest
import functools
import operator

__maintainer__ = 'Alan Valejo'
__email__ = 'alanvalejo@gmail.com'
__author__ = 'Alan Valejo'
__credits__ = ['Alan Valejo']
__homepage__ = 'https://www.alanvalejo.com.br'
__license__ = 'GNU.GPL.v3'
__docformat__ = 'markdown en'
__version__ = '0.1'
__date__ = '2020-05-05'

class MultiLabelPropagation(MGraph):

    def __init__(self, *args, **kwargs):
        super().__init__()

        prop_defaults = {
            'seed_priority': 'random', 'max_comm_size': None, 'upper_bound': None,
            'reverse': None, 'threshold': 0.3, 'max_prop_label': 7,
            'itr': 10, 'max_size': 100, 'until_convergence': False
        }

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.w_comms = []
        self.n_comms = []
        self.itr_convergence = 0

    def contract(self, matching):
        """
        Create coarse graph from matching of groups
        """

        # Contract vertices: Referencing the original graph of the coarse graph
        types = []
        weights = []
        sources = []
        predecessors = []
        matching = numpy.array(matching)
        uniqid = 0
        for layer in range(self['layers']):
            vertices_layer = numpy.array(self['vertices_by_type'][layer])
            matching_layer = matching[vertices_layer]
            clusters = numpy.unique(matching_layer)
            for cluster_id in clusters:
                ids = numpy.where(matching_layer == cluster_id)[0]
                vertices = vertices_layer[ids]
                weight = 0
                source = []
                predecessor = []
                for vertex in vertices:
                    self.vs[vertex]['successor'] = uniqid
                    weight += self.vs[vertex]['weight']
                    source.extend(self.vs[vertex]['source'])
                    predecessor.append(vertex)
                weights.append(weight)
                types.append(layer)
                sources.append(source)
                predecessors.append(predecessor)
                uniqid += 1

        # Create coarsened version
        kwargs = dict(
            itr=self.itr, threshold=self.threshold, upper_bound=self.upper_bound,
            reverse=self.reverse, seed_priority=self.seed_priority,
            max_prop_label=self.max_prop_label, until_convergence=self.until_convergence
        )
        coarse = MultiLabelPropagation(**kwargs)
        coarse.add_vertices(uniqid)
        coarse.vs['type'] = types
        coarse.vs['weight'] = weights
        coarse.vs['name'] = range(coarse.vcount())
        coarse.vs['successor'] = [None] * coarse.vcount()
        coarse.vs['source'] = sources
        coarse.vs['predecessor'] = predecessors
        coarse['layers'] = self['layers']
        coarse['similarity'] = None
        coarse['vertices'] = []
        coarse['itr_convergence'] = self.itr_convergence

        coarse['vertices_by_type'] = []
        for layer in range(self['layers']):
            coarse['vertices_by_type'].append(coarse.vs.select(type=layer).indices)
            coarse['vertices'].append(len(coarse['vertices_by_type'][layer]))

        # Contract edges
        dict_edges = dict()
        for edge in self.es():
            v_successor = self.vs[edge.tuple[0]]['successor']
            u_successor = self.vs[edge.tuple[1]]['successor']

            # Add edge in coarsened graph
            if v_successor < u_successor:
                dict_edges[(v_successor, u_successor)] = dict_edges.get((v_successor, u_successor), 0) + edge['weight']
            else:
                dict_edges[(u_successor, v_successor)] = dict_edges.get((u_successor, v_successor), 0) + edge['weight']

        if len(dict_edges) > 0:
            edges, weights = list(zip(*dict_edges.items()))
            coarse.add_edges(edges)
            coarse.es['weight'] = weights
            coarse['adjlist'] = list(map(set, coarse.get_adjlist()))

        return coarse

    def load(self, filename, filetype='ncol', vertices=None, type_filename=None):
        super(MultiLabelPropagation, self).load(filename, filetype=filetype, vertices=vertices, type_filename=type_filename)
        self.validate()

    def validate(self):

        # Validation of list values
        for prop_name in ['max_size']:
            if isinstance(getattr(self, prop_name), list):
                if len(getattr(self, prop_name)) == 1:
                    setattr(self, prop_name, [getattr(self, prop_name)[0]] * self['layers'])
            else:
                setattr(self, prop_name, [getattr(self, prop_name)] * self['layers'])

        # Parameters dimension validation
        for prop_name in ['max_size']:
            if self['layers'] != len(getattr(self, prop_name)):
                print('Number of layers and ' + str(prop_name) + ' do not match.')
                sys.exit(1)

        # Seed priority validation
        valid_seed_priority = ['strength', 'degree', 'random']
        self.seed_priority = self.seed_priority.lower()
        if self.seed_priority not in valid_seed_priority:
            print('Seed priority ' + self.seed_priority + ' is invalid.')
            print('Please select an option: ' + ', '.join(valid_seed_priority))
            sys.exit(1)

        # Reverse validation
        if type(self.reverse) is str:
            self.reverse = self.reverse.lower()
            if type(self.reverse) is str:
                if self.reverse in ('yes', 'true', 't', 'y', '1'):
                    self.reverse = True
                elif self.reverse in ('no', 'false', 'f', 'n', '0'):
                    self.reverse = False
                else:
                    print('Invalid reverse boolean value expected in -rv.')
                    sys.exit(1)

    def _score(self, propagators):
        for p in propagators:
            d_sqrt = math.sqrt(self.strength(p))
            for key, t in enumerate(self.vs[p]['label']):
                if d_sqrt != 0:
                    self.vs[p]['label'][key] = (t[0], t[1] / d_sqrt)

    def _frequency(self, u):
        label_freq = Counter()
        sum_freq = 0.0
        for n in self.neighbors(u):
            for t in self.vs[n]['label']:
                label_freq.update({t[0]: t[1]})
                sum_freq += t[1]
        return label_freq, sum_freq

    def _propagation(self, layer):
        receivers = self['vertices_by_type'][layer]
        propagators = self.neighborhood(receivers)[1:]
        propagators = list(set(functools.reduce(operator.iconcat, propagators, [])))
        convergence = True
        self._score(propagators)

        for r in random.sample(receivers, len(receivers)):
            if self.degree(r) > 0:
                old_labels, old_freqs = zip(*self.vs[r]['label'])
                label_freq, sum_freq = self._frequency(r)
                freq_max = max(label_freq.values())
                new_labels_freqs = [(label, freq / sum_freq) for label, freq in label_freq.items()
                                    if freq / freq_max >= self.threshold]
                new_labels, new_freqs = zip(*nlargest(self.max_prop_label, new_labels_freqs, key=lambda e: e[1]))

                if self.upper_bound is not None:
                    for label in new_labels:
                        if self.w_comms[layer][label] + self.vs[r]['weight'] > self.upper_bound[layer]:
                            new_labels = new_labels[1:]
                            new_freqs = new_freqs[1:]
                        else:
                            break

                if not self.until_convergence:
                    if self.w_comms[layer][old_labels[0]] - self.vs[r]['weight'] <= 0:
                        for label in new_labels:
                            if self.w_comms[layer][label] > 0:
                                if self.n_comms[layer] - 1 < self.max_size[layer]:
                                    new_labels = new_labels[1:]
                                    new_freqs = new_freqs[1:]
                                else:
                                    break
                            else:
                                break

                if new_labels:
                    self.vs[r]['label'] = list(zip(new_labels, new_freqs))
                    if old_labels != new_labels:
                        convergence = False
                        if old_labels[0] != new_labels[0]:
                            self.w_comms[layer][old_labels[0]] -= self.vs[r]['weight']
                            if self.w_comms[layer][old_labels[0]] <= 0:
                                self.n_comms[layer] -= 1
                            if self.w_comms[layer][new_labels[0]] <= 0:
                                self.n_comms[layer] += 1
                            self.w_comms[layer][new_labels[0]] += self.vs[r]['weight']

        return convergence

    def run(self):

        for layer in range(self['layers']):
            self.w_comms.append([0] * self.vcount())
            self.n_comms.append(0)
            for v in self['vertices_by_type'][layer]:
                self.vs[v]['label'] = [(v, 1.0)]
                self.w_comms[layer][v] = self.vs[v]['weight']
                self.n_comms[layer] += 1

        for itr in range(self.itr):
            convergence = False
            for layer in range(self['layers']):
                convergence = self._propagation(layer)

            if convergence:
                break

        self.itr_convergence = itr

        for v in self.vs():
            v['label'] = max(v['label'], key=itemgetter(1))[0]
