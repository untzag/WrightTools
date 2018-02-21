"""Test dataset argmax method."""


# --- import --------------------------------------------------------------------------------------


import numpy as np

import WrightTools as wt
from WrightTools import datasets


# --- test ----------------------------------------------------------------------------------------


def test_JASCO_PbSe_batch_4_2012_02_21():
    p = wt.datasets.JASCO.PbSe_batch_4_2012_02_21
    data = wt.data.from_JASCO(p)
    assert data.signal.argmax() == (1250,)
    assert data['energy'].argmax() == (0,)
    data.close()


def test_PyCMDS_wm_w2_w1_000():
    p = wt.datasets.PyCMDS.wm_w2_w1_000
    data = wt.data.from_PyCMDS(p)
    assert data['wm'].argmax() == (34, 0, 0)
    assert data['w2'].argmax() == (0, 0, 0)
    assert data['w1'].argmax() == (0, 0, 10)
    assert data.signal_diff.argmax() == (14, 5, 5)
    assert data.signal_mean.argmax() == (14, 5, 5)
    data.close()
