
snakemake_grass module
**********************

Snakemake GRASS interface.

**class snakemake_grass.GrassLocation(database, location_name, dafault_mapset='PERMANENT', epsg=None, location_file=None)**

   Bases: ``object``

   Representation of a GRASS location.

   **clean_output(paths='{output}')**

   **exec(command, mapset=None, clean=True, *args, **kwargs)**

      Exec grass with snakemake creating location/mapset as needed.

   **property location**

   **property location_path**

   **map_mapset(name)**

   **mapset(name=None, output=True)**

   **mapset_path(name=None)**

   **raster(name)**

   **rasters(namespattern, **kwargs)**

   **vector(name, output=True)**

   **vectors(namespattern, output=True, **kwargs)**

**snakemake_grass.clean_output(pathtolocation, output_paths)**

   Removes GRASS components from location using paths to judge what to do.

   This function performs cleaning that snakemake does not and to allow grass
   to create locations, mapsets, rasters and vectors. This includes:
   - remove empty location, mapset and raster directories created by snakemake
   - drop tables of vectors (only with the same name)
   - remove all ancillary raster files

**snakemake_grass.clean_raster(path)**

**snakemake_grass.clean_vector(path)**

   Remove vector without using grass as snakemake partially removes it.
