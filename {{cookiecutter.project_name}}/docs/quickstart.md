# Quickstart

{{ cookiecutter.project_name }} works on {class}`~anndata.AnnData` objects: {mod}`{{ cookiecutter.package_name }}.pp` preprocesses them, {mod}`{{ cookiecutter.package_name }}.tl` computes on them and {mod}`{{ cookiecutter.package_name }}.pl` plots them.

```python
import numpy as np
from anndata import AnnData

import {{ cookiecutter.package_name }}

adata = AnnData(np.random.normal(size=(20, 10)))

{{ cookiecutter.package_name }}.pp.basic_preproc(adata)
{{ cookiecutter.package_name }}.tl.basic_tool(adata)
{{ cookiecutter.package_name }}.pl.basic_plot(adata)
```

The {doc}`tutorials <notebooks/example>` go into more detail and the {doc}`API reference <api>` lists every function.
