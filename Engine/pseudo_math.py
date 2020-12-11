from math import log, exp


def sigmoid(x):
    return 1 / (1 + exp(-x))


def inverse_sigmoid(x):
    return -log(1 / x - 1)
