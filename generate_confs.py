import json
import math
import os

import numpy

coarsening_directory = "/home/paulo_althoff/development/coarsening/"
conf_directory = coarsening_directory + "input/"
graphs_directory = coarsening_directory + "graphs/"

# if not os.path.exists(clpk_input_directory):
#     os.makedirs(clpk_input_directory)
# if not os.path.exists(clpk_output_directory):
#     os.makedirs(clpk_output_directory)

max_itr = 10
max_itr_bnoc = 10
schema = [[0, 1]]
communities_set = range(4, 10)
noise_set = numpy.linspace(0.0, 1.0, num=100)
dispersion_set = numpy.linspace(0.0, 1.0, num=100)

schemas = {
    's1': {
        'layers': 4,
        'schema': [
            [0,1],
            [1,2],
            [2,3],
            [3,1]
        ],
    }
}

for key, noise in enumerate(noise_set):
    noise_set[key] = float("{:.3f}".format(noise_set[key]))

for key, dispersion in enumerate(dispersion_set):
    dispersion_set[key] = float("{:.3f}".format(dispersion_set[key]))

for target_vertices in range(100, 1000, 100):
    for id in schemas:
        layers = schemas[id]['layers']
        schema = schemas[id]['schema']

        vertices = [5 * target_vertices] * layers
        vertices[0] = target_vertices
        total_vertices = sum(vertices)

        max_levels = [100] * layers
        max_levels[0] = 0

        for num_communities in communities_set:
            communities = [num_communities] * layers

            # for key, noise in enumerate(noise_set):
            for i in range(1):
                noise_value = 0.100
                noise = float("{:.3f}".format(noise_value))

                for dispersion_value in numpy.arange(0.1, 1, 0.01):
                #for i in range(1):
                    dispersion = float("{:.3f}".format(dispersion_value))
                    for itr in range(max_itr):

                            filename = "v_" + str(target_vertices) + "-s_" + id + "-c_" + str(num_communities) + "-n_" \
                                       + "{:.3f}".format(noise) + "-d" + "{:.3f}".format(dispersion) + "-itr_" + str(itr)
                            print(filename)

                            _dict = {
                                "output_directory":  graphs_directory,
                                "output": filename,
                                "vertices": vertices,
                                "communities": communities,
                                "dispersion": dispersion,
                                "mu": 0.8,
                                "noise": noise,
                                "balanced": False,
                                "unweighetd": True,
                                "normalize": True,
                                "show_timing": True,
                                "save_metrics_csv": True,
                                "save_metrics_json": True,

                                "unique_key": False,
                                "hard": True,
                                "save_cover": False,
                                "max_levels": max_levels,
                                "max_size": [math.ceil(vertice * 0.2) for vertice in vertices],
                                "reduction_factor": [
                                    0.8
                                ],
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
                                "save_conf": True,
                                "save_ncol": False,
                                "save_type": False,
                                "save_membership": True,
                                "save_predecessor": False,
                                "save_successor": False,
                                "save_weight": False,
                                "save_source": False,
                                "save_timing_csv": True,
                                "save_timing_json": True,
                                "show_conf": False,
                                "show_metrics": True
                            }

                            dict_file = conf_directory + filename + ".json"

                            with open(dict_file, "w+") as f:
                                json.dump(_dict, f, indent=4)

                            # os.system('python ../../../mcdkn/mcdkn.py -cnf ' + dict_file)
