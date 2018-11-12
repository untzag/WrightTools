"""Test axis unit conversion."""


# --- import --------------------------------------------------------------------------------------


import numpy as np

import WrightTools as wt
from WrightTools import datasets


# --- define --------------------------------------------------------------------------------------


def test_convert_variables():
    p = datasets.KENT.LDS821_TRSF
    ignore = ["d1", "d2", "wm"]
    data = wt.data.from_KENT(p, ignore=ignore)
    data.w2.convert("meV", convert_variables=True)
    assert data.w2.units == "meV"
    assert data["w2"].units == "meV"
    data.close()


def test_exception():
    p = datasets.PyCMDS.w1_000
    data = wt.data.from_PyCMDS(p)
    try:
        data.w1.convert("fs")
    except wt.exceptions.UnitsError:
        assert True
    else:
        assert False
    assert data.w1.units == "wn"
    assert data["w1"].units == "nm"
    data.close()


def test_w1_wa():
    p = datasets.PyCMDS.w1_wa_000
    data = wt.data.from_PyCMDS(p)
    assert data.wa.units == "wn"
    data.wa.convert("eV")
    assert data.wa.units == "eV"
    assert np.isclose(data.wa.max(), 1.5802564757220569)
    assert np.isclose(data.wa.min(), 0.6726385958618104)
    assert data["wa"].units == "nm"
    data.close()


def test_wigner():
    p = datasets.COLORS.v2p2_WL_wigner
    data = wt.data.from_COLORS(p)
    data.d1.convert("ns")
    assert data.d1.units == "ns"
    assert data["d1"].units == "fs"
    data.close()


# --- run -----------------------------------------------------------------------------------------


if __name__ == "__main__":
    test_convert_variables()
    test_exception()
    test_w1_wa()
    test_wigner()
