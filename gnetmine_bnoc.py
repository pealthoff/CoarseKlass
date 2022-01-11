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
    # label the items
    k = len(num_vertices_por_particao)
    y = {n: [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in num_vertices_por_particao}
    for x in label:
        for i in label[x]:
            y[x][label[x][i] - 1][i - 1, 0] = 1

    others = {i: [i + j for j in num_vertices_por_particao if j != i and i + j in S] for i in num_vertices_por_particao}

    # iterate until converge
    old_f = y
    for _ in range(t):
        new_f = {n: [np.zeros((num_vertices_por_particao[n], 1)) for _ in range(k)] for n in num_vertices_por_particao}
        for fi in old_f:
            for j, fk in enumerate(old_f[fi]):
                sf = sum([S[i] * old_f[i[1]][j] for i in others[fi]])
                new_f[fi][j] = (l * sf + 2 * l * fk + a * y[fi][j]) \
                               / (len(others[fi]) * l + 2 * l + a)
        old_f = new_f
        # print new_f

    # decide the labels
    f = {i: [j.tolist() for j in old_f[i]] for i in old_f}
    out = {n: np.zeros(num_vertices_por_particao[n]) for n in num_vertices_por_particao}
    for fi in f:
        for i in range(len(f[fi][0])):
            out[fi][i] = np.argmax([f[fi][j][i] for j in range(k)]) + 1

    # print [out[i].tolist() for i in out]
    return out


# calculate S using files
def S(filenames, m, t=[0]):
    matrices = []
    for i, filename in enumerate(filenames):
        matrix = np.zeros((m[i], m[i + 1]), dtype=int)
        with open(filename, "r") as f:
            for line in f:
                entry = [int(j) for j in line.split()]
                matrix[entry[0 + t[i]] - 1][entry[1 - t[i]] - 1] = entry[2]
        matrices.append(sp.csc_matrix(matrix))

    R = matrices[0]
    for i in matrices[1:]:
        R *= i

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
        num_vertices = options.vertices
        
        start = time.time()
        PA, AP = S(["./data/PA.txt"], [num_vertices[1], num_vertices[0]])
        PC, CP = S(["./data/PC.txt"], [num_vertices[1], num_vertices[2]])
        PT, TP = S(["./data/PT.txt"], [num_vertices[1], num_vertices[3]])
        AC, CA = S(["./data/PA.txt", "./data/PC.txt"], [num_vertices[0], num_vertices[1], num_vertices[2]], [1, 0])
        mid = time.time()

    train_label, test_label = get_label()
    r = GNetMine({"10": PA, "01": AP, "12": PC, "21": CP, "13": PT, "31": TP, \
                  "02": AC, "20": CA}, {"0": num_vertices[0], "1": num_vertices[1], "2": num_vertices[2], "3": num_vertices[3]}, train_label, options, 10)
    get_accuracy(r, test_label)
    end = time.time()

    print("Time:\ngenerate S:", mid - start, "\tGNetMine:", end - mid)


if __name__ == "__main__":
    main()