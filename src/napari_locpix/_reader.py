"""
Read in .csv and .parquet files

Modified from:
https://github.com/napari/cookiecutter-napari-plugin 
and
https://napari.org/stable/plugins/guides.html?#readers
"""

import polars as pl
import pyarrow as pq
import numpy as np
from typing import Union, Sequence, Callable, List
from ._datastruc import item, file_to_datastruc

PathLike = str
PathOrPaths = Union[PathLike, Sequence[PathLike]]

def napari_get_reader(path: PathOrPaths):
    """Get the relevant reader.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if (not path.endswith(".parquet")) and (not path.endswith(".csv")) :
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path

    

    # load file into numpy array
    if path.endwith(".csv"):
        datastruc = file_to_datastruc(path, "csv", )
    elif path.endwith(".parquet"):
        datastruc = file_to_datastruc(path, "parquet", )
    histo = datastruc.coord_to_histo()

    # display histogram in napari

    # also store the datastructure in a widget

    # widget should display:
    # file name
    # length
    # column names

    # writer can then access this when writing to .csv or .parquet

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {}

    layer_type = "image"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]
