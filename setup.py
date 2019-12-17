# -*- coding: UTF-8 -*-
from setuptools import setup
from datetime import date

import snakemake_grass

__author__ = "Michel Wortmann"
__copyright__ = "Copyright %s, " % date.today().year + __author__

requirements = [
    "snakemake>=5.0.0"
]

classifiers = [
    "Development Status :: 1 - Alpha",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Topic :: Reproduceability",
]

with open("README.rst", "r") as fp:
    long_description = fp.read()

setup(name="snakemake_grass",
      version=snakemake_grass.__version__,
      author=snakemake_grass.__author__,
      author_email=snakemake_grass.__email__,
      url=snakemake_grass.__url__,
      py_modules=["snakemake_grass"],
      install_requires=requirements,
      description="Snakemake - GRASS GIS interface",
      long_description=long_description,
      license=snakemake_grass.__license__,
      classifiers=classifiers,
      python_requires=">=3.5",
      )
