from collections.abc import Callable, Iterable
from typing import Any, TypeVar

import numpy as np
from anndata import AnnData

MuData = TypeVar("MuData")
SpatialData = TypeVar("SpatialData")

ScverseDataStructures = AnnData | MuData | SpatialData


def basic_preproc(adata: AnnData) -> int:
    """Run a basic preprocessing on the AnnData object.

    Parameters
    ----------
    adata
        The AnnData object to preprocess.

    Returns
    -------
    Some integer value.
    """
    print("Implement a preprocessing function here.")
    return 0


def elaborate_example(
    items: Iterable[ScverseDataStructures],
    transform: Callable[[Any], str],
    *,  # functions after the asterix are keyword-only arguments
    layer_key: str | None = None,
    # Only specify defaults and types in the signature, not the docstring!
    mudata_mod: str | None = "rna",
    sdata_table_key: str | None = "table1",
    max_items: int = 100,
) -> list[str]:
    r"""A method with a more complex docstring.

    This is where you add more details.
    Try to support general container classes such as Sequence, Mapping, or Collection
    where possible to ensure that your functions can be widely used.

    Data science means there’s lots of math too:

    ..  math::

        x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}

    Parameters
    ----------
    items
        AnnData, MuData, or SpatialData objects to process.
    transform
        Function to transform each item to string.
    layer_key
        Optional layer key to access matrix to apply transformation on.
    mudata_mod
        Optional MuData modality key to apply transformation on.
    sdata_table_key
        Optional SpatialData table key to apply transformation on.

    Returns
    -------
    List of transformed string items.

    Examples
    --------
    >>> elaborate_example(
    ...     [adata, mudata, spatial_data],
    ...     lambda vals: f"Statistics: mean={vals.mean():.2f}, max={vals.max():.2f}",
    ...     {"var_key": "CD45", "modality": "rna", "min_value": 0.1},
    ... )
    ['Statistics: mean=1.24, max=8.75', 'Statistics: mean=0.86, max=5.42']
    """
    result: list[Any] = []

    for item in items:
        if isinstance(item, AnnData):
            matrix = item.X if not layer_key else item.layers[layer_key]
        elif isinstance(item, MuData):
            matrix = item.mod[mudata_mod].X if not layer_key else item.mod[mudata_mod].layers[layer_key]
        elif isinstance(item, SpatialData):
            matrix = item.tables[sdata_table_key].X if not layer_key else item.tables[sdata_table_key].layers[layer_key]
        else:
            msg = f"Item {item} must be of type AnnData, MuData, or SpatialData but is {item.__class__}."
            raise ValueError(msg)
        if not isinstance(matrix, np.ndarray):
            msg = f"Item {item} matrix is not a Numpy matrix but of type {matrix.__class__}"
            raise ValueError(msg)

        result.append(transform(matrix.flatten()))

        if len(result) >= max_items:
            break

    return result
