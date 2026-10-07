# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "esis-jet-paper"
copyright = "2026, Roy T. Smart, Charles C. Kankelborg, Jacob D. Parker, Dana W. Longcope"
author = "Roy T. Smart, Charles C. Kankelborg, Jacob D. Parker, Dana W. Longcope"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.viewcode",
]
autosummary_generate = True
autosummary_imported_members = True
autosummary_ignore_module_all = False
autodoc_typehints = "description"

graphviz_output_format = "png"
inheritance_graph_attrs = {"rankdir": "TB"}

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_static_path = ["_static"]

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/esis-mission/esis-jet-paper",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
}

# https://github.com/readthedocs/readthedocs.org/issues/2569
master_doc = "index"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pylatex": ("https://jeltef.github.io/PyLaTeX/current/", None),
    "aastex": ("https://aastex.readthedocs.io/en/latest/", None),
    "named_arrays": ("https://named-arrays.readthedocs.io/en/latest/", None),
    "optika": ("https://optika.readthedocs.io/en/latest/", None),
    "esis": ("https://esis-mission.github.io/esis/", None),
}
