import os
from multiprocessing import set_start_method
set_start_method('spawn', force=True)

import warnings

from osgeo import gdal, osr

import rioxarray as rxr
from rasterio.errors import RasterioIOError

from datetime import datetime, timedelta

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
    geotiff_file_paths = []

    for bnd in nm_bands:
        raster_src = bnd + '_' + hdf_file[:-4] + '.tif'
        raster_dst = bnd + '_' + hdf_file[:-4] + '_proj' + '.tif'

        output_dir_b = os.path.join(output_dir, 'geotiffs', tile, str(yr), date, time)

        os.makedirs(output_dir_b, exist_ok=True)  # creates directory for every band

        # Here you decide how much of the data you want to export.
        # A single layer vs a stacked / array
        # Export a single band to a geotiff
        raster_file_path = os.path.join(output_dir_b, raster_src)
        if bnd == 'blue':
            blue_band.rio.to_raster(raster_file_path)
        if bnd == 'red':
            red_band.rio.to_raster(raster_file_path)
        if bnd == 'nir':
            nir_band.rio.to_raster(raster_file_path)

        geotiff_file_path = os.path.join(output_dir_b, raster_dst)

        src_ds = gdal.Open(raster_file_path)
        format = "GTiff"
        driver = gdal.GetDriverByName(format)

        dst_ds = driver.CreateCopy(geotiff_file_path, src_ds, 0)
        dst_ds.SetGeoTransform(get_geo_transform(h, v))
        dst_ds.SetProjection(get_projection())

        dst_ds = None
        src_ds = None

        geotiff_file_paths.append(geotiff_file_path)

        print('exported:', geotiff_file_path)

    return geotiff_file_paths

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


from export_savi_ndvi import export_savi_ndvi

date = input('Enter julian date start and end YYYYDDD YYYYDDD: ')
date = date.split(' ')

start_date = datetime.strptime(date[0], '%Y%j')
end_date = datetime.strptime(date[1], '%Y%j')

# getting paths
input_dir = r'Z:\dustin\goes\geonex_l2\data_raw'
output_dir = os.path.dirname(input_dir)

tile = input('Choose a tile (h14v03 h14v04 h15v03 h15v04): ')
h = tile[1:3]
v = tile[4:6]

current_date = start_date

while current_date <= end_date:
    current_yr = str(current_date.year)
    current_julian = current_date.strftime('%j')

    input_dir_yr = os.path.join(input_dir, tile, current_yr)  # input_dir\tile\year

    input_dir_date = os.path.join(input_dir_yr, current_julian)  # input_dir\tile\yr\day
    hdf_files = os.listdir(input_dir_date)
    for hdf_file in hdf_files:
        if (hdf_file.endswith('.hdf') and 'ABI12B' in hdf_file):
            spilt_file = hdf_file.split('_')
            time = spilt_file[2][7:11]

            hdf_path = os.path.join(input_dir_date, hdf_file)  # input_dir\tile\yr\day\{.hdf file}
            bands = extract_bands(hdf_path)
            if bands:
                blue_band, red_band, nir_band = bands
            else:
                continue

            blue_geo_path, red_geo_path, nir_geo_path = create_geotiffs(hdf_file, tile, current_yr, current_julian, time, h, v,
                                                                        output_dir)

            export_savi_ndvi(nir_geo_path, red_geo_path)

    current_date += timedelta(days=1)


# for yr in range(int(start_yr), int(end_yr)+1):
#     h = tile[1:3]
#     v = tile[4:6]
#
#     input_dir_yr = os.path.join(input_dir, tile, str(yr))  # input_dir\tile\year
#
#     for date in range(int(start_julian), int(end_julian)+1):
#         date = str(date).zfill(3)
#         input_dir_date = os.path.join(input_dir_yr, date)  # input_dir\tile\yr\day
#         hdf_files = os.listdir(input_dir_date)
#
#         for hdf_file in hdf_files:
#             if (hdf_file.endswith('.hdf') and 'ABI12B' in hdf_file):
#                 spilt_file = hdf_file.split('_')
#                 time = spilt_file[2][7:11]
#
#                 hdf_path = os.path.join(input_dir_date, hdf_file)  # input_dir\tile\yr\day\{.hdf file}
#                 bands = extract_bands(hdf_path)
#                 if bands:
#                     blue_band, red_band, nir_band = bands
#                 else:
#                     continue
#
#                 blue_geo_path, red_geo_path, nir_geo_path = create_geotiffs(hdf_file, tile, yr, date, time, h, v, output_dir)
#
#                 export_savi_ndvi(nir_geo_path, red_geo_path)