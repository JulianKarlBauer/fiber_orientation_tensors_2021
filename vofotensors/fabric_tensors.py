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

alpha_x_in_la0 = sp.sympify("4/3") * la0 - sp.sympify("2/3")

substitutions = {
    "planar_alpha_d": {
        alpha_z: alpha_x / sp.S(2) - sp.sympify("1/3"),
        d1: sp.sympify("1/140") * (-sp.S(15) * alpha_x - sp.S(6)),
        d2: sp.sympify("1/140") * (sp.S(15) * alpha_x - sp.S(6)),
        d3: z,
        d4: z,
        d5: z,
        d6: z,
        d8: -d7,
    },
    "planar_la0_d": {
        la1: 1 - la0,
        d1: sp.sympify("1/140") * (-sp.S(15) * alpha_x_in_la0 - sp.S(6)),
        d2: sp.sympify("1/140") * (sp.S(15) * alpha_x_in_la0 - sp.S(6)),
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


def dev2_transv_by_la0():
    half_reminder = (sp.S(1) - la0) / sp.S(2)
    N2 = np.array(
        [
            [la0, z, z],
            [z, half_reminder, z],
            [z, z, half_reminder],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_transv_x_by_la1():
    reminder = sp.S(1) - sp.S(2) * la1
    N2 = np.array(
        [
            [reminder, z, z],
            [z, la1, z],
            [z, z, la1],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_transv_z_by_la1():
    reminder = sp.S(1) - sp.S(2) * la1
    N2 = np.array(
        [
            [la1, z, z],
            [z, la1, z],
            [z, z, reminder],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_by_alpha_x():
    return alpha_x * A2_transv_x()


def dev2_by_alpha_y():
    return alpha_y * A2_transv_y()


def dev2_by_alpha_z():
    return alpha_z * A2_transv_z()


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


def dev2_by_alpha_x_alpha_z():
    return alpha_x * A2_transv_x() + alpha_z * A2_transv_z()


def dev2_by_alpha_x_alpha_y_alpha_z():
    return dev2_by_alpha_x_alpha_z() + alpha_y * A2_transv_y()


def dev2_by_la0_la1():
    N2 = np.array(
        [
            [la0, z, z],
            [z, la1, z],
            [z, z, sp.S(1) - la0 - la1],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_by_la0_la1_la2():
    N2 = np.array(
        [
            [la0, z, z],
            [z, la1, z],
            [z, z, la2],
        ],
        dtype=object,
    )
    return N2 - A2_iso()


def dev2_planar_by_alpha_x():
    return np.array(
        sp.Matrix(dev2_by_alpha_x_alpha_z()).subs(substitutions["planar_alpha_d"])
    )


def dev2_planar_by_la_0():
    return np.array(sp.Matrix(dev2_by_la0_la1()).subs(substitutions["planar_la0_d"]))


dev2s_parametric = {
    "planar": {
        "alpha_x": dev2_planar_by_alpha_x(),
        "la_0": dev2_planar_by_la_0(),
    },
    "transv_isotropic": {
        "alpha_x": dev2_by_alpha_x(),
        "alpha_y": dev2_by_alpha_y(),
        "alpha_z": dev2_by_alpha_z(),
        "la0": dev2_transv_by_la0(),
        "la1_x": dev2_transv_x_by_la1(),
        "la1_z": dev2_transv_z_by_la1(),
    },
    "orthotropic": {
        "la0_la1": dev2_by_la0_la1(),
        "la0_la1_la2": dev2_by_la0_la1_la2(),
        "a2_b2": dev2_by_a2_b2(),
        "a2_c2": dev2_by_a2_c2(),
        "alpha_x_alpha_z": dev2_by_alpha_x_alpha_z(),
        "alpha_x_alpha_y_alpha_z": dev2_by_alpha_x_alpha_y_alpha_z(),
    },
}

N2s_parametric = copy.deepcopy(dev2s_parametric)
map_nested(dictionary=N2s_parametric, transformation=dev2_to_N2)


