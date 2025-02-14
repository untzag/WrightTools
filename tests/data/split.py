#! /usr/bin/env python3
"""test split"""


# --- import --------------------------------------------------------------------------------------


import numpy as np

import WrightTools as wt
from WrightTools import datasets

import pathlib

# --- test ----------------------------------------------------------------------------------------

here = pathlib.Path(__file__).parent


def test_split():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    exprs = a.axis_expressions
    split = a.split(0, [19700], units="wn")
    assert exprs == a.axis_expressions
    assert exprs == split[0].axis_expressions
    assert len(split) == 2
    print(split[0].shape)
    assert split[0].shape == (14, 11, 11)
    assert split[1].shape == (21, 11, 11)
    assert a.units == split[0].units
    a.close()
    split.close()


def test_split_edge():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split(0, [20800], units="wn")
    assert len(split) == 2
    assert split[0].shape == (35, 11, 11)
    assert split[1].shape == ()
    a.close()
    split.close()


def test_split_multiple():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split(0, [20605, 19705], units="wn")
    assert len(split) == 3
    assert split[2].shape == (2, 11, 11)
    assert split[1].shape == (18, 11, 11)
    assert split[0].shape == (15, 11, 11)
    a.close()
    split.close()


def test_split_close():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split(0, [19705, 19702], units="wn")
    assert len(split) == 3
    assert split[0].shape == (15, 11, 11)
    assert split[1].shape == ()
    assert split[2].shape == (20, 11, 11)
    a.close()
    split.close()


def test_split_units():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split(0, [507], units="nm")
    assert len(split) == 2
    assert split[0].shape == (20, 11, 11)
    assert split[1].shape == (15, 11, 11)
    a.close()
    split.close()


def test_split_axis_name():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split("w2", [1555])
    split.print_tree()
    assert len(split) == 2
    assert split[1].shape == (35, 10, 11)
    assert split[0].shape == (35, 11)
    assert split[0].axis_expressions == ("wm", "w1")
    a.close()
    split.close()


def test_split_constant():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split(1, [1555])
    split.print_tree()
    assert len(split) == 2
    assert split[0].shape == (35, 11)
    a.close()
    split.close()


def test_split_parent():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    parent = wt.Collection()
    split = a.split(1, [1500], parent=parent)
    assert "split" in parent
    assert split.filepath == parent.filepath
    assert len(split) == 2
    a.close()
    parent.close()


def test_split_expression():
    p = datasets.PyCMDS.wm_w2_w1_000
    a = wt.data.from_PyCMDS(p)
    split = a.split("w1+w2", 3150, units="wn")
    assert len(split) == 2
    assert split[0].shape == (35, 10, 10)
    assert split[1].shape == (35, 11, 11)
    a.close()
    split.close()


def test_split_hole():
    data = wt.Data()
    data.create_variable("x", np.linspace(-5, 5, 100)[:, None])
    data.create_variable("y", np.linspace(-5, 5, 100)[None, :])
    data.create_variable("z", np.exp(-data.x[:] ** 2) * np.exp(-data.y[:] ** 2))
    split = data.split("z", 0.5)
    assert len(split) == 2
    assert split[0].shape == (100, 100)
    assert split[1].shape == (16, 16)
    data.close()
    split.close()


def test_split_constants():
    d = wt.Data()
    d.create_variable("x", np.linspace(0, 10, 11)[:, None])
    d.create_variable("y", np.linspace(0, 10, 11)[None, :])
    d.create_channel("z", d.x[:] * d.y[:])
    d.transform("x", "y")
    split = d.split("x-y", [-0.1, 0.1, 9.9])
    assert len(split) == 4
    assert split[0].constant_expressions == ()
    assert split[1].constant_expressions == ("x-y",)
    assert split[1].constants[0].value == 0
    assert split[1].constants[0].std == 0
    assert split[1].constants[0].shape == (11, 11)
    assert split[2].constant_expressions == ()
    assert split[3].constant_expressions == ("x", "y", "x-y")
    d.close()
    split.close()


def test_autotune():
    p = here / "test_data" / "autotune.data"
    data = wt.data.from_PyCMDS(str(p))
    data.transform("w2", "w2_BBO")
    split = data.split("w2_BBO", [42])
    split.close()
    data.transform("w2_BBO", "w2")
    split = data.split("w2_BBO", [42, 41.5])
    split.close()
    data.close()


if __name__ == "__main__":
    test_split()
    test_split_edge()
    test_split_multiple()
    test_split_close()
    test_split_units()
    test_split_axis_name()
    test_split_constant()
    test_split_parent()
    test_split_expression()
    test_split_hole()
    test_split_constants()
    test_autotune()
