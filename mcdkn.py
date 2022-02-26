#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MFKN: Multilevel framework for kpartite networks

Copyright (C) 2020 Alan Valejo <alanvalejo@gmail.com> All rights reserved

Warning: The original implementations (i.e. paper versions) are deprecated. There may be divergences between
this version and the original algorithm. If you looking for the original version used in the paper don't hesitate to
contact the authors.

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

Giving credit to the author by citing the papers
"""

import sys
import numpy
import os
import inspect
import json
import math
import models.args as args

from models.mlp import MultiLabelPropagation
from models.slp import SingleLabelPropagation
from models.coarsening import Coarsening
from models.solutionfinding import SolutionFinding
from models.uncoarsening import Uncoarsening
from models.validation import Validation

from models.timing import Timing


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def main():
    """
    Main entry point for the application when run from the command line.
    """

    # Timing instance
    timing = Timing(['Snippet', 'Time [m]', 'Time [s]'])

    with timing.timeit_context_add('Pre-processing'):

        # Setup parse options command line
        current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parser = args.setup_parser(current_path + '/args/mcdkn.json')
        options = parser.parse_args()
        args.update_json(options)
        args.check_output(options)

    # Load bipartite graph
    with timing.timeit_context_add('Load graph'):

        kwargs = dict(
            itr=options.itr, threshold=options.threshold,
            reverse=options.reverse, seed_priority=options.seed_priority,
            max_prop_label=options.max_prop_label
            # , until_convergence=options.until_convergence
        )

        source_graph = MultiLabelPropagation(**kwargs)

        if options.type_filename:
            source_graph.load(options.input, type_filename=options.type_filename)
        else:
            source_graph.load(options.input, vertices=options.vertices)

        if options.upper_bound is not None:
            source_graph.upper_bound = []
            for layer in range(len(source_graph['vertices'])):
                source_graph.upper_bound.append(int(
                    math.ceil(((1.0 + (options.upper_bound[layer] * (source_graph.max_size[layer] - 1)))
                               * source_graph['vertices'][layer]) / source_graph.max_size[layer])
                ))

    # Coarsening
    with timing.timeit_context_add('Coarsening'):

        kwargs = dict(
            reduction_factor=options.reduction_factor, max_levels=options.max_levels,
            max_size=options.max_size
        )

        print('options.max_size', options.max_size)
        coarsening = Coarsening(source_graph, **kwargs)
        coarsening.run()

    # Solution finding
    with timing.timeit_context_add('Solution finding'):

        coarsest_graph = coarsening.graph_hierarchy[-1]
        print('coarsest', coarsest_graph['vertices'], options.max_size)
        if options.max_size and options.max_size != coarsest_graph['vertices']:
            print('Warning: The required minimum number of vertices is not reached. Adjust parameters '
                  'for a better result.')
        sf = SolutionFinding(coarsest_graph)

    # Uncoarsening
    with timing.timeit_context_add('Uncoarsening'):

        uncoarsening = Uncoarsening(coarsening.graph_hierarchy, initial_solution=sf.solution)
        uncoarsening.naive_uncoarsening_community_detection()

    # Compute metrics
    with timing.timeit_context_add('Compute metrics'):

        if options.metrics and (options.save_metrics_csv or options.save_metrics_json or options.show_metrics):
            labels_pred = numpy.array(uncoarsening.final_solution)
            labels_true = None
            if options.file_labels_true:
                labels_true = numpy.loadtxt(options.file_labels_true)
            validation = Validation(source_graph, labels_true, labels_pred, options.schema)

            if 'nmi' in options.metrics:
                validation.compute_normalized_mutual_info_score()
            if 'ars' in options.metrics:
                validation.compute_adjusted_rand_score()
            if 'murata_modularity' in options.metrics:
                validation.compute_murata_modularity()
            if 'barber_modularity' in options.metrics:
                validation.compute_barber_modularity()
            if 'one_mode_modularity' in options.metrics:
                validation.compute_one_mode_modularity()
            if 'one_mode_conductance' in options.metrics:
                validation.compute_one_mode_conductance()

    # Save
    with timing.timeit_context_add('Save'):

        if options.show_metrics:
            print()
            validation.print_tabular()
            print()

        if options.save_metrics_csv:
            validation.save_csv(options.output + '-metrics.csv')

        if options.save_metrics_json:
            validation.save_json(options.output + '-metrics.json')

        if options.save_conf or options.show_conf:
            d = {
                'source_input': options.input
                , 'source_vertices': source_graph['vertices']
                , 'source_vcount': source_graph.vcount()
                , 'source_ecount': source_graph.ecount()
                , 'ecount': coarsest_graph.ecount()
                , 'vcount': coarsest_graph.vcount()
                , 'vertices': coarsest_graph['vertices']
                , 'achieved_levels': coarsest_graph['level']
                , 'reduction_factor': options.reduction_factor
                , 'max_levels': options.max_levels
                , 'max_size': options.max_size
                , 'itr': options.itr
                , 'itr_convergence': coarsest_graph['itr_convergence']
                , 'level': coarsest_graph['level']
            }

            if options.save_conf:
                with open(options.output + '.conf', 'w+') as f:
                    json.dump(d, f, indent=4, cls=NpEncoder)

            if options.show_conf:
                print(json.dumps(d, indent=4, cls=NpEncoder))

        if options.save_membership:
            numpy.savetxt(options.output + '.membership', uncoarsening.final_solution, fmt='%.d')

        if options.save_type:
            numpy.savetxt(options.output + '.type', coarsest_graph.vs['type'], fmt='%.d')

        if options.save_source:
            with open(options.output + '.source', 'w+') as f:
                for v in coarsest_graph.vs():
                    f.write(' '.join(map(str, v['source'])) + '\n')

        if options.save_ncol:
            coarsest_graph.write(options.output + '.ncol', format='ncol')

        if options.save_predecessor:
            with open(options.output + '.predecessor', 'w+') as f:
                for v in coarsest_graph.vs():
                    f.write(' '.join(map(str, v['predecessor'])) + '\n')

        if options.save_successor:
            # bug o último nível não tem sucessor
            numpy.savetxt(options.output + '.successor', coarsest_graph.vs['successor'], fmt='%d')

        if options.save_weight:
            numpy.savetxt(options.output + '.weight', coarsest_graph.vs['weight'], fmt='%d')

    if options.show_timing:
        print()
        timing.print_tabular()
        print()
    if options.save_timing_csv:
        timing.save_csv(options.output + '-timing.csv')
    if options.save_timing_json:
        timing.save_json(options.output + '-timing.json')


if __name__ == "__main__":
    sys.exit(main())
