import json
import math
import os

import numpy
import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-m", "--mode", required=True)
ap.add_argument("-n", "--noise", required=False)
ap.add_argument("-d", "--dispersion", required=False)
ap.add_argument("-c", "--communities", required=False)
ap.add_argument("-dir", "--directory", required=False)

args = vars(ap.parse_args())

if args["directory"] is None:
    coarsening_directory = "/home/paulo_althoff/development/coarsening/"
else:
    coarsening_directory = args["directory"]

conf_directory = coarsening_directory + "input/"
graphs_directory = coarsening_directory + "graphs/"

max_itr = 10
schema = [[0, 1]]

schemas = {
    's1': {
        'layers': 4,
        'schema': [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 1]
        ],
    }
}


def generate_conf(filename):
    print(filename)
    _dict = {
        "output_directory": graphs_directory,
        "coarse_graph_directory": coarsening_directory + "output/coarsed_graphs/",
        "metrics_directory": coarsening_directory + "output/metrics/",
        "output": filename,
        "vertices": vertices,
        "communities": communities,
        "dispersion": dispersion,
        "mu": 0.8,
        "noise": noise,
        "balanced": False,
        "unweighted": True,
        "normalize": True,
        "show_timing": True,
        "unique_key": False,
        "hard": True,
        "save_cover": False,
        "max_levels": max_levels,
        "max_size": [math.ceil(vertice * 0.2) for vertice in vertices],
        "reduction_factor": [
            0.2
        ],
        "upper_bound": None,
        "matching": "multi-label",
        "seed_priority": "random",
        "threshold": 0.4,
        "max_prop_label": num_communities,
        "itr": 10,
        "reverse": True,
        "input": graphs_directory + "/" + filename + ".ncol",
        "type_filename": graphs_directory + "/" + filename + ".type",
        "file_labels_true": graphs_directory + "/" + filename + ".membership",
        "metrics": [
            "accuracy"
        ],
        "particao_principal": True,
        "schema": schema,
        "until_convergence": False,
        "output_text": True,
        "save_conf": False,
        "save_ncol": True,
        "save_type": True,
        "save_membership": True,
        "save_predecessor": False,
        "save_successor": False,
        "save_weight": False,
        "save_source": False,
        "show_conf": False,
    }
    dict_file = conf_directory + filename + ".json"
    with open(dict_file, "w") as f:
        json.dump(_dict, f, indent=4)


for target_vertices in range(100, 1000, 100):
    for id in schemas:
        layers = schemas[id]['layers']
        schema = schemas[id]['schema']

        vertices = [5 * target_vertices] * layers
        vertices[0] = target_vertices
        total_vertices = sum(vertices)

        max_levels = [100] * layers
        max_levels[0] = 0

        if args["communities"] is None:
            communities_range = range(4, 10)
        else:
            communities_range = [int(args["communities"])]
        for num_communities in communities_range:
            communities = [num_communities] * layers

            if args["noise"] is None:
                noise_range = numpy.arange(0.1, 1, 0.1)
            else:
                noise_range = [float(args["noise"])]
            for noise_value in noise_range:
                noise = float("{:.3f}".format(noise_value))

                if args["dispersion"] is None:
                    dispersion_range = numpy.arange(0.10, 1, 0.1)
                else:
                    dispersion_range = [float(args["dispersion"])]
                for dispersion_value in dispersion_range:
                    dispersion = float("{:.3f}".format(dispersion_value))
                    for itr in range(max_itr):
                        filename = "v_" + str(target_vertices) + "-s_" + id + "-c_" + str(num_communities) + "-n_" \
                                   + "{:.3f}".format(noise) + "-d" + "{:.3f}".format(dispersion) + "-itr_" + str(itr)

                        print(filename)
                        if args["mode"] == "conf":
                            generate_conf(filename)

                        if args["mode"] == "graph":
                            os.system('python "' + coarsening_directory +'bnoc/bnoc/bnoc.py" -cnf "' + conf_directory + filename + '.json"')

                        if args["mode"] == "class":
                            os.system('python "' + coarsening_directory + 'cmk/exp.py" -cnf "' + conf_directory + filename + '.json"')
