import os
from multiprocessing import set_start_method
set_start_method('spawn', force=True)

import warnings

import rioxarray as rxr
from rasterio.errors import RasterioIOError

from osgeo import gdal, osr

warnings.simplefilter('ignore')


def extract_bands(image_path):
    # Open just the bands that you want to process
    desired_bands = ["sur_refl1km"]
    # Notice that here, you get a single xarray object with just the bands that
    # you want to work with
    try:
        image_bands = rxr.open_rasterio(image_path, masked=True, variable=desired_bands).squeeze()
    except RasterioIOError:
        print(f"Error: Unable to open the file {image_path}")
        return False

    print("Opened:", image_path)

    bands = image_bands.sur_refl1km

    blue_band = image_bands.sur_refl1km[0]
    red_band = image_bands.sur_refl1km[1]
    nir_band = image_bands.sur_refl1km[2]

    return blue_band, red_band, nir_band

def get_geo_transform(h, v):
    # Specify raster location through geotransform array
    # (uperleftx, scalex, skewx, uperlefty, skewy, scaley)
    # Scale = size of one pixel in units of raster projection

    # GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
    # GT(1) w-e pixel resolution / pixel width.
    # GT(2) row rotation (typically zero).
    # GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
    # GT(4) column rotation (typically zero).
    # GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).

    # Basic parameters
    lat_0 = 60
    lon_0 = -180
    res_x = 0.01  # 0.02 for the 2km grid
    res_y = 0.01  # 0.02 for the 2km grid
    tile_xdim = 600  # 300 for the 2km grid
    tile_ydim = 600  # 300 for the 2km grid

    # Input information
    hid = int(h)  # 0 - 59
    vid = int(v)  # 0 - 19
    x = 0  # column/sample, 0-(tile_xdim-1)
    y = 0  # row/line, 0-(tile_ydim-1)

    # Output formula
    lat_ulcnr = lat_0 - (vid * tile_ydim + y) * res_y  # upper-left corner latitude
    lon_ulcnr = lon_0 + (hid * tile_xdim + x) * res_y  # upper-left corner longitude
    lat_cntr = lat_ulcnr - 0.5 * res_y  # center latitude
    lon_cntr = lon_ulcnr + 0.5 * res_x  # center longitude

    return [lon_ulcnr, res_x, 0.0, lat_ulcnr, 0.0, -res_y]


def get_projection():
    # Get raster projection
    epsg = 4326
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    dest_wkt = srs.ExportToWkt()

    return dest_wkt


def create_geotiffs(hdf_file, tile, yr, date, time, h, v, output_dir):
    nm_bands = ["blue", "red", "nir"]

    for bnd in nm_bands:
        raster_src = bnd + '_' + hdf_file[:-4] + '.tif'
        raster_dst = bnd + '_' + hdf_file[:-4] + '_proj' + '.tif'
        output_dir_b = fr'{output_dir}\geotiffs\{tile}\{yr}\{date}\{time}'
        os.makedirs(output_dir_b, exist_ok=True)  # creates directory for every band

        # Here you decide how much of the data you want to export.
        # A single layer vs a stacked / array
        # Export a single band to a geotiff
        raster_file_path = fr'{output_dir_b}\{raster_src}'
        if bnd == 'blue':
            blue_band.rio.to_raster(raster_file_path)
        if bnd == 'red':
            red_band.rio.to_raster(raster_file_path)
        if bnd == 'nir':
            nir_band.rio.to_raster(raster_file_path)

        geotiff_file_path = fr'{output_dir_b}\{raster_dst}'

        src_ds = gdal.Open(raster_file_path)
        format = "GTiff"
        driver = gdal.GetDriverByName(format)

        dst_ds = driver.CreateCopy(geotiff_file_path, src_ds, 0)
        dst_ds.SetGeoTransform(get_geo_transform(h, v))
        dst_ds.SetProjection(get_projection())

        dst_ds = None
        src_ds = None

        print('exported:', geotiff_file_path)


from datetime import datetime

def get_date_from_user():
    date_str = input("Please enter a date (YYYY-MM-DD or YYYY-MM-DD,YYYY-MM-DD): ")
    try:
        if "," in date_str:
            start_date, end_date = date_str.split(",")
            start_date = datetime.strptime(start_date.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_date.strip(), "%Y-%m-%d")
            return start_date.date(), end_date.date()
        else:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.date(), date.date()
    except ValueError:
        print("Invalid date format. Please try again.")
        return get_date_from_user()


# tile = 'h09v02'
# h = tile[1:3]
# v = tile[4:6]
#
# input_dir = fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2\maiac'
# output_dir = fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2'


# getting coords
print("Please select your tile:")
h = input('h (0-59) : ')
v = input('v (0-19) : ')
tile = f'h{h.zfill(2)}v{v.zfill(2)}'

# getting date
start_date, end_date = get_date_from_user()

start_julian = str(start_date.timetuple().tm_yday)
start_yr = str(start_date.year)

end_julian = str(end_date.timetuple().tm_yday)
end_yr = str(end_date.year)

# getting paths
input_dir = input('Please enter path to input directory with containing tiles\year\dates (maiac): ')
output_dir = input('Please enter path to export geotiff directory: ')

for yr in range(int(start_yr), int(end_yr)+1):
    input_dir_yr = fr'{input_dir}\{tile}\{yr}'
    for date in range(int(start_julian), int(end_julian)+1):
        date = str(date).zfill(3)
        input_dir_date = fr'{input_dir_yr}\{date}'
        hdf_files = os.listdir(input_dir_date)
        for hdf_file in hdf_files:
            time = hdf_file[19:23]

            hdf_path = fr'{input_dir_date}\{hdf_file}'

            bands = extract_bands(hdf_path)
            if bands:
                blue_band, red_band, nir_band = bands
            else:
                continue

            create_geotiffs(hdf_file, tile, yr, date, time, h, v, output_dir)
