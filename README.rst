Snakemake - GRASS GIS interface
===============================
*Create reproducible and scaleable GRASS workflows*

:Author: Michel Wortmannn <wortmann@pik-potsdam.de>
:Version: **v0.1**

Requirements
------------
- `GRASS 7 <https://grass.osgeo.org/download/software/>`_
- `Snakemake <https://snakemake.readthedocs.io>`_
- tested with Bash


Rationale
---------
`Snakemake <https://snakemake.readthedocs.io>`_ is a great way to create
**reproducible, scaleable and portable** computational workflows based on input
and output file tracking. This presents a challenge for the database approach
of `GRASS <https://grass.osgeo.org>`_. This Python module provides an interface
between the two.


Docs and examples
-----------------
`API docs <https://github.com/mwort/snakemake_grass/docs/api>``

Here is a quick example Snakefile::
  from snakemake_grass import GrassLocation
  
  grass_ll = GrassLocation('grassdb', 'lonlat', epsg=4326)

  rule new_raster:
      output: grass.raster('new_raster')
      shell: grass_ll('r.mapcalc', exp='new_raster=123')

Instead of ``r.mapcalc``, it may be more common to actually run an entire
Bash/Python script but any one command will work. For more examples, see
:doc:`tests/Snakefile`.


Tests
-----
Tests are provided in a :doc:`tests/Snakefile:Snakefile` and are run in the
``tests/`` directory like this::
  $ snakemake -j 3 all
  $ snakemake clean
