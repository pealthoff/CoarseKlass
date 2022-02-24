#!/usr/bin/env python3
# coding: utf-8

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

class MultiLevelClassificationK(MGraph):

    def __init__(self, *args, **kwargs):
        super().__init__()

        prop_defaults = {
            'seed_priority': 'random', 'max_comm_size': None, 'upper_bound': None,
            'reverse': None, 'threshold': 0.3, 'max_prop_label': 7,
            'itr': 10, 'max_size': 100, 'until_convergence': False,
            'target_partition': 0
        }

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.w_comms = []
        self.n_comms = []
        self.itr_convergence = 0
        self.schema_neighborhood = {}
        self.guides = {}
        self.coarsening_order = []

        self.neighborhood_from_guide = []
        self.neighbors_from_guide = {}

    def calculate_guides(self):
        schema_neighborhood = {}
        for layer in range(self['layers']):
            schema_neighborhood[layer] = []
        for edge in self.schema:
            schema_neighborhood[edge[0]].append(edge[1])
            schema_neighborhood[edge[1]].append(edge[0])

        for layer in range(self['layers']):
            schema_neighborhood[layer] = set(schema_neighborhood[layer])

        bfsList = [self.target_partition]
        added = [self.target_partition]

        while len(bfsList) != 0:
            partition = bfsList.pop(0)
            for s in schema_neighborhood[partition]:
                if s not in added:
                    added.append(s)
                    bfsList.append(s)
                    self.guides[s] = partition

        self.coarsening_order = added

    def calculate_neighborhood_from_guide(self):
        # edges_to_exclude = []
        # for edge in self.es():
        #     v = self.vs[edge.tuple[0]]
        #     u = self.vs[edge.tuple[1]]
        #
        #     if ((v['type'] != self.target_partition or v['type'] != self.target_partition) and (self.guides[v['type']] != u['type'] and self.guides[u['type']] != v['type'])):
        #         edges_to_exclude.append((u, v))
        # self.delete_edges(edges_to_exclude)

        for layer in range(self['layers']):
            if layer == self.target_partition:
                guide_vertices = []
            else:
                guide_vertices = self['vertices_by_type'][self.guides[layer]]
            for v in self['vertices_by_type'][layer]:
                neighbors = list(filter(lambda u: u in guide_vertices, self.neighbors(v)))
                self.neighbors_from_guide[v] = neighbors
                self.neighborhood_from_guide.append([v] + neighbors)

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
        coarse = MultiLevelClassificationK(**kwargs)
        coarse.add_vertices(uniqid)
        coarse.vs['type'] = types
        coarse.vs['weight'] = weights
        coarse.vs['name'] = range(coarse.vcount())
        coarse.vs['successor'] = [None] * coarse.vcount()
        coarse.vs['source'] = sources
        coarse.vs['predecessor'] = predecessors
        coarse['layers'] = self['layers']
        coarse['similarity'] = None
        coarse.schema = self.schema
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

    def load_guides(self):
        self.calculate_guides()
        self.calculate_neighborhood_from_guide()

    def load(self, filename, filetype='ncol', vertices=None, type_filename=None):
        super(MultiLevelClassificationK, self).load(filename, filetype=filetype, vertices=vertices, type_filename=type_filename)
        self.validate()
        self.load_guides()

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
        for n in self.neighbors_from_guide[u]:
            for t in self.vs[n]['label']:
                label_freq.update({t[0]: t[1]})
                sum_freq += t[1]
        return label_freq, sum_freq

    def _propagation(self, layer):
        receivers = self['vertices_by_type'][layer]
        propagators = list(filter(lambda neighborhood: neighborhood[0] in receivers, self.neighborhood_from_guide))
        propagators = list(set(functools.reduce(operator.iconcat, propagators, [])))
        convergence = True
        self._score(propagators)

        for r in random.sample(receivers, len(receivers)):
            if self.degree(r) > 0 and len(self.neighborhood_from_guide[r]) > 0:
                old_labels, old_freqs = zip(*self.vs[r]['label'])
                label_freq, sum_freq = self._frequency(r)
                if len(label_freq) > 0:
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
            for layer in self.coarsening_order:
                if layer is not self.target_partition:
                    convergence = self._propagation(layer)

            if convergence:
                break

        self.itr_convergence = itr

        for v in self.vs():
            v['label'] = max(v['label'], key=itemgetter(1))[0]
