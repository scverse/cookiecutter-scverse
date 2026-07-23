from collections.abc import Callable, Iterable

import numpy as np
from anndata import AnnData


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
    items: Iterable[AnnData],
    transform: Callable[[np.ndarray], str],
    *,  # arguments after the asterisk are keyword-only
    layer_key: str | None = None,
    # Only specify defaults and types in the signature, not the docstring!
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
        AnnData objects to process.
    transform
        Function to transform each item to string.
    layer_key
        Optional layer key to access matrix to apply transformation on.
    max_items
        Maximum number of items to process.

    Returns
    -------
    List of transformed string items.

    Examples
    --------
    >>> elaborate_example(
    ...     [adata],
    ...     lambda vals: f"Statistics: mean={vals.mean():.2f}, max={vals.max():.2f}",
    ... )
    ['Statistics: mean=1.24, max=8.75']
    """
    result: list[str] = []

    for item in items:
        matrix = item.layers[layer_key]
        if not isinstance(matrix, np.ndarray):
            msg = f"Item {item} matrix is not a NumPy array but of type {matrix.__class__}."
            raise ValueError(msg)

        result.append(transform(matrix.flatten()))  # type: ignore[attr-defined]

        if len(result) >= max_items:
            break

    return result
