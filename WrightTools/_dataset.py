"""Dataset base class."""


# --- import --------------------------------------------------------------------------------------


import posixpath
import collections
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import h5py

from . import kit as wt_kit


# --- class ---------------------------------------------------------------------------------------


class Dataset(h5py.Dataset):
    """Array-like data container."""

    instances = {}
    class_name = 'Dataset'

    def __getitem__(self, index):
        if not hasattr(index, '__iter__'):
            index = [index]
        index = wt_kit.valid_index(index, self.shape)
        return super().__getitem__(index)

    def __iadd__(self, value):
        def f(dataset, s, value):
            if hasattr(value, 'shape'):
                dataset[s] += value[wt_kit.valid_index(s, value.shape)]
            else:
                dataset[s] += value
        self.chunkwise(f, value=value)
        return self

    def __imul__(self, value):
        def f(dataset, s, value):
            if hasattr(value, 'shape'):
                dataset[s] *= value[wt_kit.valid_index(s, value.shape)]
            else:
                dataset[s] *= value
        self.chunkwise(f, value=value)
        return self

    def __ipow__(self, value):
        def f(dataset, s, value):
            if hasattr(value, 'shape'):
                dataset[s] **= value[wt_kit.valid_index(s, value.shape)]
            else:
                dataset[s] **= value
        self.chunkwise(f, value=value)
        return self

    def __isub__(self, value):
        def f(dataset, s, value):
            if hasattr(value, 'shape'):
                dataset[s] -= value[wt_kit.valid_index(s, value.shape)]
            else:
                dataset[s] -= value
        self.chunkwise(f, value=value)
        return self

    def __itruediv__(self, value):
        def f(dataset, s, value):
            if hasattr(value, 'shape'):
                dataset[s] /= value[wt_kit.valid_index(s, value.shape)]
            else:
                dataset[s] /= value
        self.chunkwise(f, value=value)
        return self

    def __new__(cls, parent, id, **kwargs):
        """New object formation handler."""
        fullpath = parent.fullpath + h5py.h5i.get_name(id).decode()
        if fullpath in cls.instances.keys():
            return cls.instances[fullpath]
        else:
            instance = super(Dataset, cls).__new__(cls)
            cls.__init__(instance, parent, id, **kwargs)
            cls.instances[fullpath] = instance
            return instance

    def __repr__(self):
        return '<WrightTools.{0} \'{1}\' at {2}>'.format(self.class_name, self.natural_name,
                                                         self.fullpath)

    def __setitem__(self, index, value):
        self._clear_array_attributes_cache()
        return super().__setitem__(index, value)

    def _clear_array_attributes_cache(self):
        if 'max' in self.attrs.keys():
            del self.attrs['max']
        if 'min' in self.attrs.keys():
            del self.attrs['min']

    @property
    def fullpath(self):
        """Full path: file and internal structure."""
        return self.parent.fullpath + posixpath.sep + self.natural_name

    @property
    def natural_name(self):
        """Natural name of the dataset. May be different from name."""
        try:
            assert self._natural_name is not None
        except (AssertionError, AttributeError):
            self._natural_name = self.attrs['name']
        finally:
            return self._natural_name

    @natural_name.setter
    def natural_name(self, value):
        self.attrs['name'] = value
        self._natural_name = None

    @property
    def parent(self):
        """Parent."""
        return self._parent

    @property
    def units(self):
        """Units."""
        if 'units' in self.attrs.keys():
            return self.attrs['units'].decode()

    @units.setter
    def units(self, value):
        """Set units."""
        if value is None:
            if 'units' in self.attrs.keys():
                self.attrs.pop('units')
        else:
            self.attrs['units'] = value.encode()

    def chunkwise(self, func, *args, **kwargs):
        """Execute a function for each chunk in the dataset.

        Order of excecution is not guaranteed.

        Parameters
        ----------
        func : function
            Function to execute. First two arguments must be dataset,
            slices.
        args (optional)
            Additional (unchanging) arguments passed to func.
        kwargs (optional)
            Additional (unchanging) keyword arguments passed to func.

        Returns
        -------
        collections OrderedDict
            Dictionary of index: function output. Index is to lowest corner
            of each chunk.
        """
        out = collections.OrderedDict()
        for s in self.slices():
            key = tuple(sss.start for sss in s)
            out[key] = func(self, s, *args, **kwargs)
        self._clear_array_attributes_cache()
        return out

    def clip(self, min=None, max=None, replace=np.nan):
        """Clip values outside of a defined range.

        Parameters
        ----------
        min : number (optional)
            New channel minimum. Default is None.
        max : number (optional)
            New channel maximum. Default is None.
        replace : number or 'value' (optional)
            Replace behavior. Default is nan.
        """
        if max is None:
            max = self.max()
        if min is None:
            min = self.min()

        def f(dataset, s, min, max, replace):
            arr = dataset[s]
            if replace == 'value':
                dataset[s] = np.clip(arr, min, max)
            else:
                arr[arr < min] = replace
                arr[arr > max] = replace
                dataset[s] = arr

        self.chunkwise(f, min=min, max=max, replace=replace)

    def log(self, base=np.e, floor=None):
        """Take the log of the entire dataset.

        Parameters
        ----------
        base : number (optional)
            Base of log. Default is e.
        floor : number (optional)
            Clip values below floor after log. Default is None.
        """
        def f(dataset, s, base, floor):
            arr = dataset[s]
            arr = np.log(arr)
            if base != np.e:
                arr /= np.log(base)
            if floor is not None:
                arr[arr < floor] = floor
            dataset[s] = arr
        self.chunkwise(f, base=base, floor=floor)

    def log10(self, floor=None):
        """Take the log base 10 of the entire dataset.

        Parameters
        ----------
        floor : number (optional)
            Clip values below floor after log. Default is None.
        """
        def f(dataset, s, floor):
            arr = dataset[s]
            arr = np.log10(arr)
            if floor is not None:
                arr[arr < floor] = floor
            dataset[s] = arr
        self.chunkwise(f, floor=floor)

    def log2(self, floor=None):
        """Take the log base 2 of the entire dataset.

        Parameters
        ----------
        floor : number (optional)
            Clip values below floor after log. Default is None.
        """
        def f(dataset, s, floor):
            arr = dataset[s]
            arr = np.log2(arr)
            if floor is not None:
                arr[arr < floor] = floor
            dataset[s] = arr
        self.chunkwise(f, floor=floor)

    def max(self):
        """Maximum, ignorning nans."""
        if 'max' not in self.attrs.keys():
            def f(dataset, s):
                return np.nanmax(dataset[s])
            self.attrs['max'] = max(self.chunkwise(f).values())
        return self.attrs['max']

    def min(self):
        """Minimum, ignoring nans."""
        if 'min' not in self.attrs.keys():
            def f(dataset, s):
                return np.nanmin(dataset[s])
            self.attrs['min'] = min(self.chunkwise(f).values())
        return self.attrs['min']

    def slices(self):
        """Returns a generator yielding tuple of slice objects.

        Order is not guaranteed.
        """
        if self.chunks is None:
            yield tuple(slice(None, s) for s in self.shape)
        else:
            ceilings = tuple(-(-s // c) for s, c in zip(self.shape, self.chunks))
            for idx in np.ndindex(ceilings):  # could also use itertools.product
                out = []
                for i, c, s in zip(idx, self.chunks, self.shape):
                    start = i * c
                    stop = min(start + c, s + 1)
                    out.append(slice(start, stop, 1))
                yield tuple(out)

    def symmetric_root(self, root=2):
        def f(dataset, s, root):
            dataset[s] = np.sign(dataset[s]) * (np.abs(dataset[s]) ** (1 / root))
        self.chunkwise(f, root=root)
