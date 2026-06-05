import tomllib
from pathlib import Path

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "hermpy"
copyright = "2026, Daragh M. Hollman"
author = "Daragh M. Hollman"

# Set release based on pyproject.toml
with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    release = tomllib.load(f)["project"]["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_gallery.gen_gallery",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = []
html_theme_options = {
    "logo": {
        "text": "hermpy",
        "image_light": "images/logo.png",
        "image_dark": "images/logo.png",
    },
    "github_url": "https://github.com/daraghhollman/hermpy",
    "navbar_align": "left",
}
html_context = {"default_mode": "light"}
html_sidebars = {
    # These pages have their sidebar removed, usually because it is empty.
    "getting_started": []
}

sphinx_gallery_conf = {
    "examples_dirs": "../src/examples",  # path to your example scripts
    "gallery_dirs": "generated_examples",  # path to where to save gallery generated output
    "filename_pattern": r"\.py",  # run all .py files
    "default_thumb_file": "./images/logo.png",
    "download_all_examples": False,
}
html_css_files.append("hide-download-prompt.css")
