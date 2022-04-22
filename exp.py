import sys
import numpy
import os
import inspect
import json
import math

from sklearn.metrics import precision_recall_fscore_support

from CoarseKlass.models.mlp import MultiLabelPropagation
from models.coarseklass import CoarseKlass
from models.coarsening import Coarsening
from models.solutionfinding import SolutionFinding
from sklearn import metrics

from models.timing import Timing
import models.args as args

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


def get_metrics(graph, labels_true, labels_pred):
    indices = graph.vs.select(type=0).indices
    indices_with_label_true = [i - 1 for i in indices if labels_true[i - 1] != -1]
    labels_pred = labels_pred[indices_with_label_true]
    labels_true = labels_true[indices_with_label_true]
    accuracy = metrics.accuracy_score(labels_true, labels_pred)
    precision_micro, recall_micro, fscore_micro, _ = precision_recall_fscore_support(labels_true, labels_pred, average='micro')
    precision_macro, recall_macro, fscore_macro, _ = precision_recall_fscore_support(labels_true, labels_pred, average='macro')
    return accuracy, precision_micro, precision_macro, recall_micro, recall_macro, fscore_micro, fscore_macro



def main():
    exp()


def exp():
    # Timing instance
    metrics_writer = Timing(['Snippet', 'Time [min]', 'Time [sec]'])


    # Setup parse options command line
    current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parser = args.setup_parser(current_path + '/args/coarseklass.json')
    options = parser.parse_args()
    args.update_json(options)
    args.check_output(options)

    # Load graph
    with metrics_writer.timeit_context_add('Load graph'):

        kwargs = dict(
            itr=options.itr, threshold=options.threshold,
            reverse=options.reverse, seed_priority=options.seed_priority,
            max_prop_label=options.max_prop_label,
            schema=options.schema
            # until_convergence=options.until_convergence
        )

        source_graph = CoarseKlass(**kwargs)
        # source_graph = MultiLabelPropagation(**kwargs)
        source_size = source_graph.load(options.input, type_filename=options.type_filename)

        target_vertices_num = len(source_graph.vs.select(type=0))

        if options.upper_bound is not None:
            source_graph.upper_bound = []
            for layer in range(len(source_graph['vertices'])):
                source_graph.upper_bound.append(int(
                    math.ceil(((1.0 + (options.upper_bound[layer] * (source_graph.max_size[layer] - 1)))
                               * source_graph['vertices'][layer]) / source_graph.max_size[layer])
                ))

        labels_true = numpy.loadtxt(options.file_labels_true)
        source_size['membership'] = os.stat(options.file_labels_true).st_size
        indices = source_graph.vs.select(type=0).indices  # particao alvo
        indices_with_label_true = [i for i in indices if labels_true[i] != -1]

    # Coarsening
    with metrics_writer.timeit_context_add('Coarsening'):

        kwargs = dict(
            reduction_factor=options.reduction_factor, max_levels=options.max_levels,
            max_size=options.max_size
        )

        print('options.max_size', options.max_size)
        coarsening = Coarsening(source_graph, **kwargs)
        coarsening.run()

    for index, row in enumerate(metrics_writer.elapsed_set):
        metrics_writer.elapsed_set[index] = ['--', '--'] + row + ['--', '--', '--', '--', '--', '--', '--', '--', '--']
    metrics_writer.header = ['Snippet', 'Amostragem', 'Reduction', 'Time [min]', 'Time [sec]', 'Accuracy',
                             'Precision (micro)', 'Precision (macro)', 'Recall (micro)', 'Recall (macro)',
                             'F-score (micro)', 'F-score (macro)', 'Vertices Size', 'Edges Size']

    for amostragem in {0.01, 0.1, 0.2, 0.5}:
    #for amostragem in {0.001}:
        sample_indices = numpy.random.choice(indices_with_label_true, size=math.ceil(len(indices_with_label_true) * amostragem),
                                             replace=False)
        for graph in coarsening.graph_hierarchy:
            reduction = 1- ((len(graph.vs) - target_vertices_num) / (len(source_graph.vs) - target_vertices_num))
            timing_row = len(metrics_writer.rows)
            with metrics_writer.timeit_context_add('Classificacao-a=%.2f-r=%.2f' % (amostragem, reduction)):

                kwargs = dict(
                    schema=options.schema, labels_true=labels_true, particao_principal=options.particao_principal,
                    communities=options.communities, sample_indices=sample_indices
                )
                sf = SolutionFinding(graph, **kwargs)
                sf.gnetmine()

            labels_pred = numpy.array(sf.solution)

            accuracy, precision_micro, precision_macro, recall_micro, recall_macro, fscore_micro, fscore_macro = get_metrics(graph, labels_true, labels_pred)

            if reduction == 0:
                vertices_size = source_size["membership"] + source_size["types"]
                edges_size = source_size["ncol"]
            else:

                coarse_file = options.output + '-red_%.2f' % reduction
                with open(coarse_file + '.source', 'w+') as f:
                    for v in graph.vs():
                        f.write(' '.join(map(str, v['source'])) + '\n')

                numpy.savetxt(coarse_file + '.membership', labels_pred, fmt='%.d')
                vertices_size = os.stat(coarse_file + '.membership').st_size
                numpy.savetxt(coarse_file + '.type', graph.vs['type'], fmt='%.d')
                vertices_size = vertices_size + os.stat(coarse_file + '.type').st_size
                graph.write(coarse_file + '.ncol', format='ncol')
                edges_size = os.stat(coarse_file + '.ncol').st_size


            metrics_writer.elapsed_set[timing_row] = ['%.2f' % amostragem, '%.2f' % reduction] + metrics_writer.elapsed_set[timing_row] + ['%.2f' % accuracy, '%.2f' % precision_micro, '%.2f' % precision_macro, '%.2f' % recall_micro, '%.2f' % recall_macro, '%.2f' % fscore_micro, '%.2f' % fscore_macro, '%d' % vertices_size, '%d' % edges_size]

    if options.show_timing:
        print()
        metrics_writer.print_tabular()
    metrics_writer.save_csv(options.metrics_output + '-metrics-complete.csv')


if __name__ == "__main__":
    sys.exit(main())