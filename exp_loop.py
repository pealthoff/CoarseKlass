import json
import math
import os

import numpy
import argparse
import pandas

ap = argparse.ArgumentParser()

ap.add_argument("-m", "--mode", required=True)
ap.add_argument("-n", "--noise", required=False)
ap.add_argument("-d", "--dispersion", required=False)
ap.add_argument("-c", "--communities", required=False)
ap.add_argument("-mxcs", "--max_communities_step", required=False)
ap.add_argument("-mxc", "--max_communities", required=False)
ap.add_argument("-v", "--vertices", required=False)
ap.add_argument("-mxv", "--max_vertices", required=False)
ap.add_argument("-s", "--schema", required=False)
ap.add_argument("-dir", "--directory", required=False)
ap.add_argument("-itr", "--iterations", required=False)

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
    },
    'h1': {
        'layers': 5,
        'schema': [
            [0, 1],
            [0, 2],
            [1, 3],
            [1, 4],
            [3, 4]
        ],
    },
    'b1': {
        'layers': 2,
        'schema': [
            [0, 1],
        ],
    },

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

df = pandas.DataFrame()

df_controle = pandas.DataFrame(columns=['v', 'c', 'n', 'd', 'graph', 'metric'])


def load_metrics(df, filename, vertices, noise, dispersion, num_communities, schema_id):
    try:
        df1 = pandas.read_csv(coarsening_directory + 'output/metrics/'+ filename +'-metrics-complete.csv')
        coarsening_time = df1.loc[df1['Snippet'] == 'Coarsening'].iloc[0]['Time [min]'] * 60 + df1.loc[df1['Snippet'] == 'Coarsening'].iloc[0]['Time [sec]']
        df1 = df1.loc[df1['Amostragem'] != '--']
        df1.insert(2, 'Vertices', [vertices] * len(df1), True)
        df1.insert(2, 'Noise', [noise] * len(df1), True)
        df1.insert(2, 'Dispersion', [dispersion] * (len(df1)), True)
        df1['Time class'] = df1['Time [min]'] * 60 + df1['Time [sec]']
        df1['Communities'] = num_communities
        df1['Schema'] = schema_id
        cols = df1.columns.drop(['Snippet', 'Time [min]', 'Time [sec]', 'Schema'])
        df1[cols] = df1[cols].apply(pandas.to_numeric, errors='ignore')
        for amostragem in [0.01, 0.1, 0.2, 0.5]:
            df2 = df1.loc[df1['Amostragem'] == amostragem]
            df2 = df2.drop(columns=['Accuracy'])
            for metric in ['Time class', 'F-score (micro)', 'F-score (macro)', 'Precision (micro)', 'Precision (macro)', 'Recall (micro)', 'Recall (macro)']:
                df2[metric + ' N'] = df2[metric] / df2.loc[df1['Reduction'] == 0].iloc[0][metric]
                df2[metric + ' 0 Red'] = df2.loc[df1['Reduction'] == 0].iloc[0][metric]
            df2['Time with coarsening N'] = (df2['Time class'] + coarsening_time) / df2.loc[df1['Reduction'] == 0].iloc[0]['Time class']
            df2['Coarsening Time'] = coarsening_time
            df = df.append(df2, ignore_index=True)


        # df = df.append(df1, ignore_index=True)
    except Exception:
        print()
    return df

if args["vertices"] is None:
    if args["max_vertices"] is None:
        vertices_range = [*range(100, 1000, 100)]
    else:
        vertices_range = [*range(100, int(args["max_vertices"]), 100)]
else:
    vertices_range = [int(args["vertices"])]
for target_vertices in vertices_range:
    if args["schema"] is None:
        schemas_values = schemas
    else:
        schemas_values = [str(args["schema"])]
    for id in schemas_values:
        layers = schemas[id]['layers']
        schema = schemas[id]['schema']

        vertices = [5 * target_vertices] * layers
        vertices[0] = target_vertices
        total_vertices = sum(vertices)

        max_levels = [100] * layers
        max_levels[0] = 0

        if args["max_communities_step"] is None:
            step_comm = 1
        else:
            step_comm = int(args["max_communities_step"])

        if args["communities"] is None:
            if args["max_communities"] is None:
                communities_range = range(4, 10)
            else:
                communities_range = [*range(4, int(args["max_communities"]), step_comm)]
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
                    if args["iterations"] is None:
                        iterations_range = range(max_itr)
                    else:
                        iterations_range = range(int(args["iterations"]))
                    for itr in iterations_range:
                        filename = "v_" + str(target_vertices) + "-s_" + id + "-c_" + str(num_communities) + "-n_" \
                                   + "{:.3f}".format(noise) + "-d" + "{:.3f}".format(dispersion) + "-itr_" + str(itr)

                        print(filename)
                        if args["mode"] == "control":
                            if os.path.exists(graphs_directory + filename + '.ncol'):
                                graph = 1
                            else:
                                graph = 0
                            if os.path.exists(coarsening_directory + 'output/metrics/'+ filename +'-metrics-complete.csv'):
                                metric = 1
                            else:
                                metric = 0
                            row = { 'v': total_vertices, 'c': num_communities, 'n': noise, 'd': dispersion, 'graph': graph, 'metric': metric }
                            df_controle = df_controle.append(row, ignore_index=True)

                        if args["mode"] == "conf":
                            generate_conf(filename)

                        if args["mode"] == "graph":
                            print('python "' + coarsening_directory +'bnoc/bnoc/bnoc.py" -cnf "' + conf_directory + filename + '.json"')
                            if os.path.exists(graphs_directory + filename + '.ncol'):
                                pass
                            else:
                                os.system('python "' + coarsening_directory +'bnoc/bnoc/bnoc.py" -cnf "' + conf_directory + filename + '.json"')

                        if args["mode"] == "class":
                            if os.path.exists(coarsening_directory + 'output/metrics/'+ filename +'-metrics-complete.csv'):
                                pass
                            else:
                                os.system('python "' + coarsening_directory + 'cmk/exp.py" -cnf "' + conf_directory + filename + '.json"')

                        if args["mode"] == "metrics":
                            df = load_metrics(df, filename, total_vertices, noise, dispersion, num_communities, id)

if args["mode"] == "control":
    df_controle.to_csv(coarsening_directory + 'output/metrics/metrics-control.csv')
if args["mode"] == "metrics":
    df.to_csv(coarsening_directory + 'output/metrics/all-metrics-norm-complete.csv')

print("ok")
