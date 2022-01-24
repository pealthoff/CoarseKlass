import inspect
import os
from random import randint

import numpy as np

from models import args
from models.timing import Timing
import scipy.sparse as sp
import time


# the main algorithm;
# S: PA, AP, PC, CP, PT, TP, AC, CA
# particao APCT: '0', '1', '2', '3';

def GNetMine(S, num_vertices_por_particao, t=100, a=0.1, l=0.2, labels={}):
    k = len(num_vertices_por_particao)

    offset = [sum(num_vertices_por_particao[0: i]) for i in range(k)]
    # label the items
    y = {str(n): [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in range(k)}
    for particao in labels:
        for i in labels[particao]:
            y[particao][labels[particao][i] - 1][i - offset[int(particao)] - 1, 0] = 1
            # y[particao][label[particao][i] - 1][i - 1, 0] = 1

    others = {str(i): [str(i) + str(j) for j in range(k) if j != i and str(i) + str(j) in S] for i in range(k)}

    # iterate until converge
    old_f = y
    for _ in range(t):
        new_f = {str(n): [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in range(k)}
        for particao in old_f:
            for j, fk in enumerate(old_f[particao]):
                sf = sum([S[i] * old_f[i[1]][j] for i in others[particao]])
                new_f[particao][j] = (l * sf + 2 * l * fk + a * y[particao][j]) \
                                     / (len(others[particao]) * l + 2 * l + a)
        old_f = new_f
        # print new_f

    # decide the labels
    f = {i: [j.tolist() for j in old_f[i]] for i in old_f}
    out = {str(n): np.zeros(num_vertices_por_particao[n]) for n in range(k)}
    for particao in f:
        for i in range(len(f[particao][0])):
            out[particao][i] = np.argmax([f[particao][j][i] for j in range(k)]) + 1

    # print [out[i].tolist() for i in out]
    return out, f


def S(particoes, types, options, vertices):
    offset = [sum(vertices[0: particoes[i]]) for i in range(len(particoes))]
    matrix = np.zeros((vertices[particoes[0]], vertices[particoes[1]]), dtype=int)
    with open(options.input, "r") as f:
        for line in f:
            a, b, c = line.split()
            entry = [int(a)+1, int(b)+1, float(c)]
            if types[entry[0]] > particoes[0]:
                break
            if types[entry[0]] == particoes[0] and types[entry[1]] == particoes[1]:
                matrix[entry[0] - offset[0] - 1][entry[1] - offset[1] - 1] = entry[2]
    R = sp.csc_matrix(matrix)

    # generate diagnol matrix
    D1 = np.diag(np.array(np.power(R.sum(axis=1), -0.5)).flatten())
    D2 = np.diag(np.array(np.power(R.sum(axis=0), -0.5)).flatten())

    out = sp.csc_matrix(D1) * R * sp.csc_matrix(D2)
    return out, sp.csc_matrix.transpose(out)


# generate results
def get_accuracy(result, label, num_vertices_por_particao):
    k = len(num_vertices_por_particao)
    offset = [sum(num_vertices_por_particao[0: i]) for i in range(k)]

    out = {str(i): [] for i in range(k)}

    for i in label:
        for j in label[i]:
            if result[i][j - offset[int(i)] - 1] == label[i][j]:
                out[i].append(1.0)
            else:
                out[i].append(0.0)

    accuracy = {str(i): 0 for i in range(k)}
    for particao in label:
        if len(out[particao]) != 0:
            accuracy[particao] = sum(out[particao]) / len(out[particao])
    return accuracy


def main():
    timing = Timing(['Snippet', 'Time [m]', 'Time [s]'])

    with timing.timeit_context_add('Pre-processing'):
        # Setup parse options command line
        current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parser = args.setup_parser(current_path + '/args/mlck.json')
        options = parser.parse_args()
        args.update_json(options)
        args.check_output(options)

    with timing.timeit_context_add('Load graph'):
        num_vertices_por_particao = options.vertices

        start = time.time()

        types = {}

        with open(options.type_filename, "r") as f:
            i = 1
            for line in f:
                types[i] = int(line)
                i = i + 1

        connections = {}
        for pair in options.schema:
            connections[str(pair[0]) + str(pair[1])], connections[str(pair[1]) + str(pair[0])] = S([pair[0], pair[1]],
                                                                                                   types, options)

        mid = time.time()

    labels = {}
    with open(options.file_labels_true, "r") as f:
        for id, line in enumerate(f, start=1):
            label = line.split()[0]
            if label != '-1':
                labels[id] = int(label)

    k = len(num_vertices_por_particao)

    def get_all_labels_por_particao():
        labels_por_particao = {str(i): {} for i in range(k)}
        for id in labels:
            labels_por_particao[str(types[id])][id] = labels[id]
        return labels_por_particao


    labels_por_particao = {str(i): {} for i in range(k)}
    for id in labels:
        labels_por_particao[str(types[id])][id] = labels[id]

    if options.particao_principal:
        for particao in range(1, k):
            del labels_por_particao[str(particao)]

    def split_test_train_accuracy():
        def split_test_train_sets():
            train = {str(i): {} for i in range(k)}
            test = {str(i): {} for i in range(k)}
            for id in labels:
                r = randint(1, 10)
                if r == 1:
                    train[str(types[id])][id] = labels[id]
                else:
                    test[str(types[id])][id] = labels[id]
            return train, test

        labels_por_particao_train, labels_por_particao_test = split_test_train_sets()
        y, multilabel_y = GNetMine(connections, num_vertices_por_particao, 100, labels=labels_por_particao_train)
        return get_accuracy(y, labels_por_particao_test, num_vertices_por_particao)

    def cross_validation_accuracy(cv=10):
        def split_cross_validation_sets():
            groups = [{str(i): {} for i in range(k)} for j in range(cv)]
            # for particao in labels_por_particao:

            for particao in labels_por_particao:
                for id in labels_por_particao[particao]:
                    r = randint(0, cv - 1)
                    groups[r][particao][id] = labels[id]
                return groups

        groups = split_cross_validation_sets()
        groups_accuracy = []
        for cross_group in range(cv):
            labels_por_particao_train = groups[cross_group]
            labels_por_particao_test = {str(i): {} for i in range(k)}
            for other_group in range(cv):
                if other_group != cross_group:
                    for particao in labels_por_particao_test:
                        labels_por_particao_test[particao].update(groups[other_group][particao])

            y, multilabel_y = GNetMine(connections, num_vertices_por_particao, 100, labels=labels_por_particao_train)
            groups_accuracy.append(get_accuracy(y, labels_por_particao_test, num_vertices_por_particao))

        accuracy = {str(i): 0 for i in range(k)}
        for group in range(cv):
            for particao in accuracy:
                accuracy[particao] = accuracy[particao] + groups_accuracy[group][particao]

        for particao in accuracy:
            accuracy[particao] = accuracy[particao]/cv

        return accuracy

    # accuracy = split_test_train_accuracy()
    accuracy = cross_validation_accuracy()

    print("\nAccuracy:\n")
    for particao in accuracy:
        if accuracy[particao] != 0:
            print("partição", particao, ": ", accuracy[particao])

    end = time.time()
    print("Time:\ngenerate S:", mid - start, "\tGNetMine:", end - mid)


if __name__ == "__main__":
    main()
