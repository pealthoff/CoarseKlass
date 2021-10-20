#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import numpy

if __name__ == '__main__':

    bnoc_input_directory = "/mnt/003E67FC3E67E95C/Software/exp_mcdkn/exp_bipartite/accuracy_noise/bnoc_input/"
    bnoc_output_directory = "/mnt/003E67FC3E67E95C/Software/exp_mcdkn/exp_bipartite/accuracy_noise/bnoc_output/"

    clpk_input_directory = "/mnt/003E67FC3E67E95C/Software/exp_mcdkn/exp_bipartite/accuracy_noise/clpk_input/"
    clpk_output_directory = "/mnt/003E67FC3E67E95C/Software/exp_mcdkn/exp_bipartite/accuracy_noise/clpk_output/"

    if not os.path.exists(clpk_input_directory):
        os.makedirs(clpk_input_directory)
    if not os.path.exists(clpk_output_directory):
        os.makedirs(clpk_output_directory)

    max_itr_alg = 10
    max_itr_bnoc = 10
    layers = 2
    vertices = [1000] * layers
    schema = [[0, 1]]
    communities = [10] * layers
    noise_set = numpy.linspace(0.0, 1.0, num=100)
    for key, noise in enumerate(noise_set):
        noise_set[key] = float("{:.3f}".format(noise_set[key]))

    for key, noise in enumerate(noise_set):

        for itr_bnoc in range(max_itr_bnoc):

            for itr_alg in range(max_itr_alg):

                # if key < 40:
                #     continue

                # if key < 70:
                #     continue

                # if key != 50 or itr_bnoc != 0 or itr_alg != 0:
                #     continue

                print(str(key) + ', ' + str(noise) + ', ' + str(itr_bnoc) + ', ' + str(itr_alg))

                bnoc_input_filename = str(noise).replace('.', '') + '_' + str(itr_bnoc)
                clpk_input_filename = clpk_output_filename = str(noise).replace('.', '') + '_' + str(itr_bnoc) + '_' + str(itr_alg)

                _dict = {
                    "vertices": vertices,
                    "reduction_factor": [
                        None
                    ],
                    "max_levels": [
                        None
                    ],
                    "max_size": communities,
                    "matching": "single-label",
                    "seed_priority": "random",
                    "upper_bound": [0.1, 0.1],
                    "threshold": 0.3,
                    "max_prop_label": 1,
                    "until_convergence": False,
                    "itr": 10,
                    "reverse": True,
                    "output_directory": clpk_output_directory,
                    "output": clpk_output_filename,
                    "input": bnoc_output_directory + bnoc_input_filename + ".ncol",
                    "type_filename": bnoc_output_directory + bnoc_input_filename + ".type",
                    "file_labels_true": bnoc_output_directory + bnoc_input_filename + ".membership",
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
                    "unique_key": False,
                    "show_timing": True,
                    "show_conf": False,
                    "metrics": ["nmi"],
                    "schema": schema,
                    "save_metrics_csv": True,
                    "save_metrics_json": True,
                    "show_metrics": True
                }

                dict_file = clpk_input_directory + clpk_input_filename + ".json"

                with open(dict_file, "w+") as f:
                    json.dump(_dict, f, indent=4)

                os.system('python ../../../mcdkn/mcdkn.py -cnf ' + dict_file)
