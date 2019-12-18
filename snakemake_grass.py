"""Snakemake GRASS interface."""
import os
import os.path as osp

from snakemake.io import ancient, directory, expand

__version__ = '0.1'
__author__ = "Michel Wortmann"
__email__ = "wortmann@pik-potsdam.de"
__license__ = "MIT"
__url__ = "https://github.com/mwort/snakemake_grass"


class GrassLocation:
    """Representation of a GRASS location with exec method.

    The GRASS location will be created if needed if ``location_file``
    or ``epsg`` is given, otherwise it has to exist already.

    :param database: Path to grass database directory
    :param location_name: Location name
    :param default_mapset: Mapset to use when none is specified
    :param epsg: EPSG code to create the location from
    :param location_file: Georeferenced file to base location on, takes
        precedence over epsg.
    """

    def __init__(self, database, location_name, dafault_mapset='PERMANENT',
                 epsg=None, location_file=None):
        self.database = database
        self.location_name = location_name
        self.default_mapset = dafault_mapset
        self.epsg = epsg
        self.location_file = location_file
        return

    def _first_or_raise(self, *args):
        for a in args:
            if a is not None:
                return a
        raise AttributeError(args)

    @property
    def location_path(self):
        """Path to location directory."""
        return osp.join(self.database, self.location_name)

    @property
    def location(self):
        """File representation of the location used in input/output.
        """
        return osp.join(self.location_path, 'PERMANENT', 'PROJ_INFO')

    def mapset_path(self, name=None):
        """Path to mapset directory.

        If no ``name`` is given, fall back to ``default_mapset``.
        """
        ms_name = self._first_or_raise(name, self.default_mapset)
        return osp.join(self.location_path, ms_name)

    def mapset(self, name=None, output=True):
        """File representation of a mapset.

        If no ``name`` is given, fall back to ``default_mapset``.
        If used as input, warnings can be suppressed by
        setting ``output=False``.
        """
        pth = osp.join(self.mapset_path(name), 'WIND')
        return pth if output else ancient(pth)

    def map_mapset(self, name):
        """Return map name and mapset from ``name@mapset``.

        If no @mapset provided, return ``default_mapset``.
        """
        nm = name.split('@')
        ms = (nm[1] if len(nm) == 2
              else self._first_or_raise(self.default_mapset))
        return nm[0], ms

    def vector(self, name, output=True):
        """File representation of a vector map.

        If used as input, warnings can be suppressed by
        setting ``output=False``.
        """
        nm, ms = self.map_mapset(name)
        path = osp.join(self.location_path, ms, 'vector', nm)
        return directory(path) if output else path

    def vectors(self, namespattern, output=True, **kwargs):
        """Representation of several vector maps.

        :param namespattern: Either a list/tuple/dict as input to
            ``vector`` or an expand pattern with variables provided
            as ``kwargs``.
        :returns: list or dict if dict was given.
        """
        if type(namespattern) is str:
            exp = expand(self.vector(namespattern, output=False), **kwargs)
            return directory(exp) if output else exp
        elif type(namespattern) in [list, tuple]:
            return [self.vector(r, output=output) for r in namespattern]
        elif type(namespattern) is dict:
            return {k: self.vector(v, output=output)
                    for k, v in namespattern.items()}
        else:
            raise ValueError('Expected str, tuple, list or dict, got: %r'
                             % namespattern)

    def raster(self, name):
        """File representation of a raster map.
        """
        nm, ms = self.map_mapset(name)
        return osp.join(self.location_path, ms, 'cellhd', nm)

    def rasters(self, namespattern, **kwargs):
        """Representation of several raster maps.

        :param namespattern: Either a list/tuple/dict as input to
            ``raster`` or an expand pattern with variables provided
            as ``kwargs``.
        :returns: list or dict if dict was given.
        """
        if type(namespattern) is str:
            return expand(self.raster(namespattern), **kwargs)
        elif type(namespattern) in [list, tuple]:
            return [self.raster(r) for r in namespattern]
        elif type(namespattern) is dict:
            return {k: self.raster(v) for k, v in namespattern.items()}
        else:
            raise ValueError('Expected str, tuple, list or dict, got: %r'
                             % namespattern)

    def clean_output(self, paths='{output}'):
        """Explicitly clean output remnants and empty dirs.

        This is automatically done in `__call__/exec` but can be
        switched off with `clean=False` if called multiple times.
        :param paths: Map file representation.
        """
        cleanf = ('snakemake_grass.clean_output("%s", "%s")'
                  % (self.location_path, paths))
        return "python -c 'import snakemake_grass; %s'; " % cleanf

    def exec(self, command, mapset=None, clean=True, *args, **kwargs):
        """Exec grass with snakemake creating location/mapset as needed.

        :param command: Any statement executed in grass. More parts or
            keyword arguements can be parsed as ``args/kwargs``. This
            may be a grass command, a shell command/script or a python
            script via ``python script.py``.
        :param mapset: Which mapset to execute the command in. Will be
            created if it doesnt exists (careful with region settings,
            it's best to set a default region in PERMANENT using
            `g.region -s`). Defaults to ``default_mapset``.
        :param clean: Dont clean empty dirs and map remnants. Useful
            for disabling if calling ``exec`` multiple times in a shell
            block. The second call would clean the output of the first.
        """
        command += ' '+' '.join(map(str, args))
        for k, v in kwargs.items():
            command += ' %s=%s' % (k, ','.join(v) if type(v) is list else v)

        variables = "GRASS_OVERWRITE=1 "
        cf = self.clean_output() if clean else ""
        # check if location needs to be created
        if self.location_file or self.epsg:
            cloc = self.location_file or ('EPSG:%s' % self.epsg)
            clocation = ("test ! -d {0} && grass -e -c {1} {0}; "
                         .format(self.location_path, cloc))
        else:
            clocation = ''
        # check if mapset needs to be created
        ms_path = self.mapset_path(mapset)
        cmapset = "`test ! -d {0} && echo -c` ".format(ms_path) + ms_path
        gcmd = "grass {0} --exec {1} ; ".format(cmapset, command)
        return cf+clocation+variables+gcmd

    def __call__(self, *args, **kwargs):
        """Alias for :meth:`.exec`."""
        return self.exec(*args, **kwargs)


def path_to_map(path, mapset=True):
    """Turn a Snakemake GRASS DB path into a GRASS map name.
    """
    name = "$(basename %s)" % path
    ms = "@$(basename $(dirname $(dirname %s)))" % path if mapset else ''
    return name + ms


def input_to_map(index=None):
    """Turn snakemake {input} keyword to a valid map name@mapset again.

    :param index: May be an int or str depending on the type of the input,
        i.e. list or dict.
    """
    if index is not None:
        index = '[%s]' % index if type(index) is int else '.%s' % index
    return path_to_map('{input%s}' % (index or ''))


def output_to_map(index=None):
    """Turn snakemake {output} keyword to a valid map name again.

    :param index: May be an int or str depending on the type of the output,
        i.e. list or dict.
    """
    if index is not None:
        index = '[%s]' % index if type(index) is int else '.%s' % index
    return path_to_map('{output%s}' % (index or ''), mapset=False)


def clean_output(pathtolocation, output_paths):
    """Removes GRASS components from location using paths to judge what to do.

    This function performs cleaning that snakemake does not and to allow grass
    to create locations, mapsets, rasters and vectors. This includes:
    - remove empty location, mapset and raster directories created by snakemake
    - drop tables of vectors (only with the same name)
    - remove all ancillary raster files
    """
    grass = GrassLocation(osp.dirname(pathtolocation),
                          osp.basename(pathtolocation))
    paths = output_paths.split() if type(output_paths) is str else output_paths

    for p in paths:
        # only consider paths in location
        if osp.realpath(p).startswith(osp.realpath(pathtolocation)):
            # clean empty dirs
            info = {'name': osp.basename(p)}
            pd = p
            for k in ['type', 'mapset', 'location']:
                pd = osp.dirname(pd)
                if osp.exists(pd) and not os.listdir(pd):
                    os.rmdir(pd)
                info[k] = osp.basename(pd)
            # remove raster and vector resources
            if grass.raster('{name}@{mapset}'.format(**info)) == p:
                clean_raster(p)
            elif grass.vector('{name}@{mapset}'.format(**info)) == p:
                clean_vector(p)
    return


def clean_vector(path):
    """Remove vector without using grass as snakemake partially removes it."""
    import shutil

    try:
        shutil.rmtree(path)
    except (OSError, IOError):
        pass
    name = osp.basename(path)
    ms_path = osp.dirname(osp.dirname(path))
    sqlitedb = osp.join(ms_path, 'sqlite', 'sqlite.db')
    if osp.exists(sqlitedb):
        import sqlite3
        with sqlite3.connect(sqlitedb) as con:
            con.cursor().execute("DROP TABLE IF EXISTS %s;" % name)
    return


def clean_raster(path):
    """Remove raster without using grass as snakemake partially removes it."""
    name = osp.basename(path)
    ms_path = osp.dirname(osp.dirname(path))
    for d in "cats cell cell_misc colr fcell hist".split():
        try:
            os.remove(osp.join(ms_path, d, name))
        except (OSError, IOError):
            pass
    return
