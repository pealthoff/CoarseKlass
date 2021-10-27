#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MFKN: Multilevel framework for kpartite networks

::Uncoarsening

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

class Uncoarsening:

    def __init__(self, hierarchy_graphs, **kwargs):

        prop_defaults = {'initial_solution': None}

        self.__dict__.update(prop_defaults)
        self.__dict__.update(kwargs)

        self.hierarchy_graphs = hierarchy_graphs
        self.final_solution = None

    def naive_uncoarsening_community_detection(self):
        self.final_solution = list(range(self.hierarchy_graphs[0].vcount()))
        for vertex in self.hierarchy_graphs[-1].vs():
            for source in vertex['source']:
                self.final_solution[source] = vertex.index
