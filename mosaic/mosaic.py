import os
import glob
import re
from datetime import datetime, timedelta
def retrieve_geotiffs(geotiff_dir, tiles, year, date):
    print('Retrieving geotiff files')
    geotiff_files = []
    for tile in tiles:
        tile.strip()
        geotiff_files.extend(glob.glob(os.path.join(geotiff_dir, tile, year, date, '**', '*proj.tif')))   # list of fullpaths to geotiff files
        print(f'Found geotiffs for tile {tile}')
        print(os.path.join(geotiff_dir, tile, year, date))

    print(geotiff_files)
    return geotiff_files  # list of full paths to every geotiff file in all tiles


# this is for knowing which times from every tile we can merge
def band_time_hashm(geotiff_files):
    hashm = {}
    for file_path in geotiff_files:
        # From every tile, we want to grab the tiles with matching band and exact time
        band_substring = os.path.basename(file_path).split("_")[0]  # getting the band from the geotiff file name
        time_substring = os.path.basename(file_path).split("_")[3]  # getting the time from the geotiff file name

        substring_gen = band_substring + time_substring

        # Hashmap hasm['band+time'] = path to every geotiff file with that band and time
        if substring_gen in hashm:
            hashm[band_substring + time_substring].append(file_path)
        else:
            hashm[band_substring + time_substring] = [file_path]

    print('hashmap created')
    return hashm

def change_path(geotiff_path):
    # Converting geotiffs\{tile}\{year}\{date}\{clocktime}\{band}_GO16_ABI12B_{time}_GLBG_{tile}_proj.tif
    # to mosaic\{year}\{date}\{clocktime}\mosaic_{band}_GO16_ABI12B_{time}_GLBG_{tile}_proj.tif

    replacements = {
        "geotiffs": "mosaic",
        "savi": "mosaic_savi",
        "ndvi": "mosaic_ndvi",
        "red": "mosaic_red",
        "blue": "mosaic_blue",
        "nir": "mosaic_nir"
    }

    mosaic_path = re.sub(r"\\h\d{2}v\d{2}", "", geotiff_path, count=1)
    mosaic_path = re.sub(r"h\d{2}v\d{2}_", "", mosaic_path)

    for old, new in replacements.items():
        mosaic_path = mosaic_path.replace(old, new)

    return mosaic_path

def merge_geotiffs(geotiff_files, numTiles):
    hashmap = band_time_hashm(geotiff_files)

    for key, geotiff_paths in hashmap.items():

        # Makes sure that we only merge geotiff files that can be found in every tile at that time
        # Some tiles have certain times that others don't
        if len(geotiff_paths) == numTiles:
            mosaic_path = change_path(geotiff_paths[0])
            os.makedirs(os.path.dirname(mosaic_path), exist_ok=True)

            command = "gdalwarp -overwrite -wo COLOR_CORRECTION=YES " + ' '.join(geotiff_paths) + " " + mosaic_path
            os.system(command)

            print('exported: ', mosaic_path)

            # finish by emptying key and removing the geotiffs we just merged
            hashmap[key] = []


# Define the path to the geotiff directory which contains all tiles
geotiff_directory = "Z:\dustin\goes\geonex_l2\geotiffs"

date = input('Enter julian date start and end YYYYDDD YYYYDDD: ')
date = date.split(' ')
start_date = datetime.strptime(date[0], '%Y%j')
end_date = datetime.strptime(date[1], '%Y%j')

tiles = input('Select which tiles to merge (h14v03 h15v03 h14v04 h15v04) : ')
tiles = tiles.split(' ')
numOfTiles = len(tiles)

current_date = start_date
while current_date <= end_date:
    current_yr = str(current_date.year)
    current_julian = current_date.strftime('%j')

    geotiff_files = retrieve_geotiffs(geotiff_directory, tiles, current_yr, current_julian)
    merge_geotiffs(geotiff_files, numOfTiles)
    current_date += timedelta(days=1)



