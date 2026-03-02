{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. add toctree option to make autodoc generate the pages

.. autoclass:: {{ objname }}

{% set methods = methods | select("ne", "__init__") | list %}

{% block attributes %}
{% if attributes %}
Attributes table
~~~~~~~~~~~~~~~~

.. autosummary::
{% for item in attributes %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block methods %}
{% if methods %}
Methods table
~~~~~~~~~~~~~

.. autosummary::
{% for item in methods %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block attributes_documentation %}
{% if attributes %}
Attributes
~~~~~~~~~~

{% for item in attributes %}

.. autoattribute:: {{ [objname, item] | join(".") }}
{%- endfor %}

{% endif %}
{% endblock %}

{% block methods_documentation %}
{% if methods %}
Methods
~~~~~~~

{% for item in methods %}

.. automethod:: {{ [objname, item] | join(".") }}
{%- endfor %}

{% endif %}
{% endblock %}
