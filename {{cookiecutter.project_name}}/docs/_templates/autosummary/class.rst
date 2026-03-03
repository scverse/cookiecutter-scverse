{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. add toctree option to make autodoc generate the pages

.. autoclass:: {{ fullname }}

{% block attributes %}
{% for item in attributes %}
{% if loop.first %}
Attributes table
~~~~~~~~~~~~~~~~

.. autosummary::
{% endif %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endblock %}

{% block methods %}
{% for item in methods if item != "__init__" %}
{% if loop.first %}
Methods table
~~~~~~~~~~~~~

.. autosummary::
{% endif %}
    ~{{ name }}.{{ item }}
{% endfor %}
{% endblock %}

{% block attributes_documentation %}
{% for item in attributes %}
{% if loop.first %}
Attributes
~~~~~~~~~~

{% endif %}
.. autoattribute:: {{ [fullname, item] | join(".") }}
{%- endfor %}
{% endblock %}

{% block methods_documentation %}
{% for item in methods if item != "__init__" %}
{% if loop.first %}
Methods
~~~~~~~
{% endif %}
.. automethod:: {{ [fullname, item] | join(".") }}
{%- endfor %}
{% endblock %}
