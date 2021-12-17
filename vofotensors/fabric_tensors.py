#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import sympy as sp
import copy
from vofotensors.numbers import z, half
from vofotensors.abc import (
    alpha,
    alpha_1,
    alpha_2,
    alpha_3,
    la1,
    la2,
    la3,
    rho,
    rho_1,
    rho_2,
    rho_3,
    d1,
    d2,
    d3,
    d4,
    d5,
    d6,
    d7,
    d8,
    d9,
)
from collections import defaultdict


def map_nested(dictionary, transformation):
    # https://stackoverflow.com/a/49897410/8935243
    for each in dictionary:
        if type(dictionary[each]) == dict:
            map_nested(dictionary[each], transformation)
        else:
            dictionary[each] = transformation(dictionary[each])


################################################
# Parametrizations

alpha_1_in_la1 = sp.sympify("4/3") * la1 - sp.sympify("2/3")

substitutions = {
    "planar_alpha_d": {
        alpha_3: alpha_1 / sp.S(2) - sp.sympify("1/3"),
        d1: sp.sympify("1/140") * (-sp.S(15) * alpha_1 - sp.S(6)),
        d2: sp.sympify("1/140") * (sp.S(15) * alpha_1 - sp.S(6)),
        d3: z,
        d4: z,
        d5: z,
        d6: z,
        d8: -d7,
    },
    "planar_la1_d": {
        la2: 1 - la1,
        d1: sp.sympify("1/140") * (-sp.S(15) * alpha_1_in_la1 - sp.S(6)),
        d2: sp.sympify("1/140") * (sp.S(15) * alpha_1_in_la1 - sp.S(6)),
        d3: z,
        d4: z,
        d5: z,
        d6: z,
        d8: -d7,
    },
}


##################
# N2


def A2_iso():
    return sp.S(1) / sp.S(3) * sb.to_numpy(sb.get_I2())


def A2_transv_x():
    return np.array(
        [
            [sp.S(1), z, z],
            [z, -half, z],
            [z, z, -half],
        ],
        dtype=object,
    )


def A2_transv_y():
    return np.array(
        [
            [-half, z, z],
            [z, sp.S(1), z],
            [z, z, -half],
        ],
        dtype=object,
    )


def A2_transv_z():
    return np.array(
        [
            [-half, z, z],
            [z, -half, z],
            [z, z, sp.S(1)],
        ],
        dtype=object,
    )


def dev2_to_N2(dev2):
    return A2_iso() + dev2


def dev2_transv_by_la1():
    half_reminder = (sp.S(1) - la1) / sp.S(2)
    N2 = np.array(
        [
            [la1, z, z],
            [z, half_reminder, z],
            [z, z, half_reminder],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_transv_x_by_la2():
    reminder = sp.S(1) - sp.S(2) * la2
    N2 = np.array(
        [
            [reminder, z, z],
            [z, la2, z],
            [z, z, la2],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_transv_z_by_la2():
    reminder = sp.S(1) - sp.S(2) * la2
    N2 = np.array(
        [
            [la2, z, z],
            [z, la2, z],
            [z, z, reminder],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_by_alpha_1():
    return alpha_1 * A2_transv_x()


def dev2_by_alpha_2():
    return alpha_2 * A2_transv_y()


def dev2_by_alpha_3():
    return alpha_3 * A2_transv_z()


def dev2_by_a2_b2():
    return np.array(
        [
            [a2, z, z],
            [z, b2, z],
            [z, z, -(a2 + b2)],
        ],
        dtype=object,
    )


def dev2_by_a2_c2():
    return np.array(
        [
            [a2, z, z],
            [z, -(a2 + c2), z],
            [z, z, c2],
        ],
        dtype=object,
    )


def dev2_by_alpha_1_alpha_3():
    return alpha_1 * A2_transv_x() + alpha_3 * A2_transv_z()


def dev2_by_alpha_1_alpha_2_alpha_3():
    return dev2_by_alpha_1_alpha_3() + alpha_2 * A2_transv_y()


def dev2_by_la1_la2():
    N2 = np.array(
        [
            [la1, z, z],
            [z, la2, z],
            [z, z, sp.S(1) - la1 - la2],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_by_la1_la2_la3():
    N2 = np.array(
        [
            [la1, z, z],
            [z, la2, z],
            [z, z, la3],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_planar_by_alpha_1():
    return np.array(
        sp.Matrix(dev2_by_alpha_1_alpha_3()).subs(substitutions["planar_alpha_d"])
    )


def dev2_planar_by_la_0():
    return np.array(sp.Matrix(dev2_by_la1_la2()).subs(substitutions["planar_la1_d"]))


dev2s_parametric = {
    "planar": {
        "alpha_1": dev2_planar_by_alpha_1(),
        "la_0": dev2_planar_by_la_0(),
    },
    "transv_isotropic": {
        "alpha_1": dev2_by_alpha_1(),
        "alpha_2": dev2_by_alpha_2(),
        "alpha_3": dev2_by_alpha_3(),
        "la1": dev2_transv_by_la1(),
        "la2_x": dev2_transv_x_by_la2(),
        "la2_z": dev2_transv_z_by_la2(),
    },
    "orthotropic": {
        "la1_la2": dev2_by_la1_la2(),
        "la1_la2_la3": dev2_by_la1_la2_la3(),
        "a2_b2": dev2_by_a2_b2(),
        "a2_c2": dev2_by_a2_c2(),
        "alpha_1_alpha_3": dev2_by_alpha_1_alpha_3(),
        "alpha_1_alpha_2_alpha_3": dev2_by_alpha_1_alpha_2_alpha_3(),
    },
}

N2s_parametric = copy.deepcopy(dev2s_parametric)
map_nested(dictionary=N2s_parametric, transformation=dev2_to_N2)


