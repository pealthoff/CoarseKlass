import sys
import numpy
import os
import inspect
import json
import math
from models.mgraph import MGraph
from models.mlck import MultiLevelClassificationK

from models.timing import Timing
import models.args as args

print("oi")

def calcular_guias():
    g = "grafo"
    s = {}
    adicionados = {}
    a = "partição alvo"
    bfsList = [s[a]]
    guia = {}
    while len(bfsList) != 0:
        v = bfsList.pop(0)
        for w in g[v]:
            if not adicionados[w]:
                adicionados[w] = True
                bfsList.append(w)
                guia[w] = v


def main():
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
            max_prop_label=options.max_prop_label,
            schema=options.schema
            # until_convergence=options.until_convergence
        )

        source_graph = MultiLevelClassificationK(**kwargs)
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
        
        print(source_graph.vs)
        source_graph.run()


if __name__ == "__main__":
    sys.exit(main())