import inspect
import os

import numpy as np

from models import args
from models.timing import Timing
import scipy.sparse as sp
import time


# the main algorithm;
# S: PA, AP, PC, CP, PT, TP, AC, CA
# ij: A, P, C, T;
def GNetMine(S, num_vertices_por_particao, label, options, t=100, a=0.1, l=0.2):
    k = len(num_vertices_por_particao)
    # label the items
    y = {str(n): [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in range(k)}
    for x in label:
        for i in label[x]:
            y[x][label[x][i] - 1][i - 1, 0] = 1

    others = {str(i): [str(i) + str(j) for j in range(k) if j != i and str(i) + str(j) in S] for i in range(k)}

    # iterate until converge
    old_f = y
    for _ in range(t):
        new_f = {str(n): [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in range(k)}
        for fi in old_f:
            for j, fk in enumerate(old_f[fi]):
                sf = sum([S[i] * old_f[i[1]][j] for i in others[fi]])
                new_f[fi][j] = (l * sf + 2 * l * fk + a * y[fi][j]) \
                               / (len(others[fi]) * l + 2 * l + a)
        old_f = new_f
        # print new_f

    # decide the labels
    f = {i: [j.tolist() for j in old_f[i]] for i in old_f}
    out = {str(n): np.zeros(num_vertices_por_particao[n]) for n in range(k)}
    for fi in f:
        for i in range(len(f[fi][0])):
            out[fi][i] = np.argmax([f[fi][j][i] for j in range(k)]) + 1

    # print [out[i].tolist() for i in out]
    return out


def S(particoes, types, options):
    offset = [sum(options.vertices[0: particoes[i]]) for i in range(len(particoes))]
    matrix = np.zeros((options.vertices[particoes[0]], options.vertices[particoes[1]]), dtype=int)
    with open(options.input, "r") as f:
        for line in f:
            entry = [int(j) for j in line.split()]
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


# get existing labels
def get_label():
    author, paper = {}, {}
    with open("./data/author_label.txt", "r") as f1:
        for line in f1:
            a, l = [int(i) for i in line.split()]
            author[a] = l
    with open("./data/paper_label.txt", "r") as f2:
        for line in f2:
            p, l = [int(i) for i in line.split()]
            paper[p] = l

    def get_num(filename):
        out = []
        with open(filename, "r") as f:
            for line in f:
                out.append(int(line))
        return out

    train_author = get_num("./data/trainId_author.txt")
    train_paper = get_num("./data/trainId_paper.txt")
    test_author = get_num("./data/testId_author.txt")
    test_paper = get_num("./data/testId_paper.txt")

    return {"0": {a: author[a] for a in train_author}, \
            "1": {p: paper[p] for p in train_paper}}, \
           {"0": {a: author[a] for a in test_author}, \
            "1": {p: paper[p] for p in test_paper}}


# generate results
def get_accuracy(result, label):
    label["2"] = {}
    with open("./data/conf_label.txt", "r") as f:
        for line in f:
            l = [int(i) for i in line.split()]
            label["2"][l[0]] = l[1]

    out = {"0": [], "1": [], "2": []}
    for i in label:
        for j in label[i]:
            if result[i][j - 1] == label[i][j]:
                out[i].append(1.0)
            else:
                out[i].append(0.0)
    print(
        "\nAccuracy:\n", "author:", sum(out["0"]) / len(out["0"]), \
        "\tpaper:", sum(out["1"]) / len(out["1"]), \
        "\tconf:", sum(out["2"]) / len(out["2"]), "\n")


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

        PA, AP = S([1, 0], types, options)
        PC, CP = S([1, 2], types, options)
        PT, TP = S([1, 3], types, options)
        mid = time.time()

    train_label, test_label = get_label()
    r = GNetMine({"10": PA, "01": AP, "12": PC, "21": CP, "13": PT, "31": TP, \
                  }, num_vertices_por_particao, train_label, options, 100)
    get_accuracy(r, test_label)
    end = time.time()

    print("Time:\ngenerate S:", mid - start, "\tGNetMine:", end - mid)


if __name__ == "__main__":
    main()
