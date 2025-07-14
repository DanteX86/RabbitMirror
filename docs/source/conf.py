# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('../../'))

project = 'RabbitMirror'
copyright = '2023, RabbitMirror Team'
author = 'RabbitMirror Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.githubpages',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

# MyST Parser configuration
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
    "linkify",
    "strikethrough",
    "table",
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# RTD Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom CSS
html_css_files = [
    'custom.css',
]

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Options for autosummary ------------------------------------------------
autosummary_generate = True

# -- Options for napoleon (Google/NumPy style docstrings) -------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'click': ('https://click.palletsprojects.com/en/8.1.x/', None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Options for coverage extension -----------------------------------------
coverage_show_missing_items = True

# -- Options for sphinx_autodoc_typehints -----------------------------------
typehints_fully_qualified = False
always_document_param_types = False
typehints_document_rtype = True
typehints_use_signature = True
typehints_use_signature_return = True

# -- Custom configuration ---------------------------------------------------
# Source file suffixes
source_suffix = {
    '.rst': None,
    '.md': None,
}

# Master document
master_doc = 'index'

# Version info
version = release
today_fmt = '%B %d, %Y'

# Language
language = 'en'

# Pygments style
pygments_style = 'sphinx'

# HTML title
html_title = f'{project} v{release}'

# HTML short title
html_short_title = project

# HTML logo
# html_logo = '_static/logo.png'

# HTML favicon
# html_favicon = '_static/favicon.ico'

# HTML sidebar
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

# HTML additional pages
html_additional_pages = {}

# HTML domain indices
html_domain_indices = True

# HTML use index
html_use_index = True

# HTML split index
html_split_index = False

# HTML show source link
html_show_sourcelink = True

# HTML show sphinx
html_show_sphinx = True

# HTML show copyright
html_show_copyright = True

# HTML file suffix
html_file_suffix = None

# HTML link suffix
html_link_suffix = None

# HTML translator class
html_translator_class = None

# HTML search language
html_search_language = 'en'

# HTML search options
html_search_options = {'type': 'default'}

# HTML search scorer
html_search_scorer = 'scorer.js'

# HTML output encoding
html_output_encoding = 'utf-8'

# HTML compact lists
html_compact_lists = True

# HTML secnumber suffix
html_secnumber_suffix = '. '

# HTML add permalinks
html_add_permalinks = '¶'

# HTML use smart quotes
html_use_smartypants = True

# HTML use opensearch
html_use_opensearch = ''

# HTML file suffix
htmlhelp_basename = 'RabbitMirrordoc'

# Latex elements
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Latex documents
latex_documents = [
    (master_doc, 'RabbitMirror.tex', 'RabbitMirror Documentation',
     'RabbitMirror Team', 'manual'),
]

# Latex logo
# latex_logo = None

# Latex use parts
latex_use_parts = False

# Latex show pagerefs
latex_show_pagerefs = False

# Latex show urls
latex_show_urls = False

# Latex appendices
latex_appendices = []

# Latex domain indices
latex_domain_indices = True

# Manual pages
man_pages = [
    (master_doc, 'rabbitmirror', 'RabbitMirror Documentation',
     [author], 1)
]

# Texinfo documents
texinfo_documents = [
    (master_doc, 'RabbitMirror', 'RabbitMirror Documentation',
     author, 'RabbitMirror', 'YouTube Watch History Analysis Tool.',
     'Miscellaneous'),
]

# Epub title
epub_title = project

# Epub author
epub_author = author

# Epub publisher
epub_publisher = author

# Epub copyright
epub_copyright = copyright

# Epub identifier
epub_identifier = ''

# Epub scheme
epub_scheme = ''

# Epub uid
epub_uid = ''

# Epub cover
epub_cover = ()

# Epub pre files
epub_pre_files = []

# Epub post files
epub_post_files = []

# Epub exclude files
epub_exclude_files = ['search.html']

# Epub tocdepth
epub_tocdepth = 3

# Epub tocdup
epub_tocdup = True

# Epub tocscope
epub_tocscope = 'default'

# Epub fix images
epub_fix_images = False

# Epub max image width
epub_max_image_width = 0

# Epub show urls
epub_show_urls = 'inline'

# Epub use index
epub_use_index = True
