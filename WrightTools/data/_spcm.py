"""SPCM."""


# --- import --------------------------------------------------------------------------------------


import os
import collections
import warnings

import numpy as np

from ._data import Data
from .. import exceptions as wt_exceptions


# --- define --------------------------------------------------------------------------------------


__all__ = ["from_spcm"]


# --- from function -------------------------------------------------------------------------------


def from_spcm(filepath, name=None, *, delimiter=",", parent=None, verbose=True):
    """Create a data object from Becker & Hickl `spcm`__ software.  Must be exported as
    an ASCII (.asc) file.  If file format is exported as "ASCII with Setup", setup parameters are
    added to the ``attrs`` dictionary of the returned ``Data`` object

    __ http://www.becker-hickl.com/software/spcm.htm

    Parameters
    ----------
    filepath : string
        Path to SPC-130 .asc file.
    name : string (optional)
        Name to give to the created data object. If None, filename is used.
        Default is None.
    delimiter : string (optional)
        The string used to separate values. Default is ','.
    parent : WrightTools.Collection (optional)
        Collection to place new data object within. Default is None.
    verbose : boolean (optional)
        Toggle talkback. Default is True.

    Returns
    -------
    WrightTools.data.Data object
    """
    # check filepath
    if not filepath.endswith("asc"):
        wt_exceptions.WrongFileTypeWarning.warn(filepath, "asc")
    # parse name
    if not name:
        name = os.path.basename("filepath").split(".")[0]
    # create headers dictionary
    headers = collections.OrderedDict()
    header_lines = 0
    with open(filepath) as f:
        while True:
            line = f.readline().strip()
            header_lines += 1
            if len(line) == 0:
                break
            else:
                key, value = line.split(":", 1)
                if key.strip() == "Revision":
                    headers["resolution"] = int(value.strip(" bits ADC"))
                else:
                    headers[key.strip()] = value.strip()
        line = f.readline().strip()
        while "_BEGIN" in line:
            header_lines += 1
            section = line.split("_BEGIN")[0]
            while True:
                line = f.readline().strip()
                header_lines += 1
                if section + "_END" in line:
                    break
                if section == "SYS_PARA":
                    use_type = {
                        "B": lambda b: int(b) == 1,
                        "C": str,  # e.g. #SP [SP_OVERFL,C,N]
                        "F": float,
                        "I": int,
                        "L": int,  # e.g. #DI [DI_MAXCNT,L,128]
                        "S": str,
                        "U": int,  # unsigned int?
                    }
                    item = line[line.find("[") + 1 : line.find("]")].split(",")
                    key = item[0]
                    value = use_type[item[1]](item[2])
                    headers[key] = value
                else:
                    splitted = line.split()
                    value = splitted[-1][1:-1].split(",")
                    key = " ".join(splitted[:-1])
                    headers[key] = value
            line = f.readline().strip()
            if "END" in line:
                header_lines += 1
                break
    # initialize data object
    kwargs = {"name": name, "kind": "spcm", "source": filepath, **headers}
    if parent:
        data = parent.create_data(**kwargs)
    else:
        data = Data(**kwargs)
    # import data
    arr = np.genfromtxt(
        filepath, skip_header=(header_lines + 1), skip_footer=1, delimiter=delimiter, unpack=True
    )
    # unexpected delimiter handler
    if np.any(np.isnan(arr)):
        # delimiter warning dictionary
        delim_dict = {",": "comma", " ": "space", "\t": "tab", ";": "semicolon", ":": "colon"}
        warnings.warn("file is not %s-delimited! Trying other delimiters." % delim_dict[delimiter])
        for delimiter in delim_dict.keys():
            arr = np.genfromtxt(
                filepath,
                skip_header=header_lines + 1,
                skip_footer=1,
                delimiter=delimiter,
                unpack=True,
            )
            if not np.any(np.isnan(arr)):
                print("file is %s-delimited." % delim_dict[delimiter])
                break
        else:
            error = """Unable to load data file.
                       Data object not created!
                       Please check that your file is formatted properly."""
            raise RuntimeError(error)
    # construct data
    data.create_variable(name="time", values=arr[0], units="ns")
    data.create_channel(name="counts", values=arr[1])
    data.transform("time")
    # finish
    if verbose:
        print("data created at {0}".format(data.fullpath))
        print("  kind: {0}".format(data.kind))
        print("  range: {0} to {1} (ns)".format(data.time[0], data.time[-1]))
        print("  size: {0}".format(data.size))
        if "SP_COL_T" in data.attrs.keys():
            print("  collection time:  {0} sec".format(data.attrs["SP_COL_T"]))
    return data
