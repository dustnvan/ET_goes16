import os
from multiprocessing import set_start_method
set_start_method('spawn', force=True)

import warnings

import rioxarray as rxr

from osgeo import gdal, osr

warnings.simplefilter('ignore')


def extract_bands(image_path):
    rxr.open_rasterio(image_path,
                      masked=True,
                      group="grid1km").squeeze()
    # Open just the bands that you want to process
    desired_bands = ["sur_refl1km"]
    # Notice that here, you get a single xarray object with just the bands that
    # you want to work with
    image_bands = rxr.open_rasterio(image_path, masked=True, variable=desired_bands).squeeze()
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
    hid = h  # 0 - 59
    vid = v  # 0 - 19
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

def export_bands(hdf_file, tile, yr, day, h, v):
    nm_bands = ["blue", "red", "nir"]

    for bnd in nm_bands:
        new_filenm = bnd + '_' + hdf_file + '.tif'
        new_filenmp = bnd + '_' + hdf_file + '_proj' + '.tif'
        # save_path = fr'C:\Users\carin\PROPOSTA_DISSERTACAO\Dataset\images\GOES16_ABI\{tile}\{yr}\{day}'
        save_path = fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2\maiac\{tile}\{yr}\{day}'

        os.chdir(save_path)

        # Here you decide how much of the data you want to export.
        # A single layer vs a stacked / array
        # Export a single band to a geotiff
        if bnd == 'blue':
            blue_band.rio.to_raster(new_filenm)
        if bnd == 'red':
            red_band.rio.to_raster(new_filenm)
        if bnd == 'nir':
            nir_band.rio.to_raster(new_filenm)

        src_filename = fr'{save_path}\{new_filenm}'
        dst_filename = fr'{save_path}\{new_filenmp}'

        src_ds = gdal.Open(src_filename)
        format = "GTiff"
        driver = gdal.GetDriverByName(format)

        dst_ds = driver.CreateCopy(dst_filename, src_ds, 0)
        dst_ds.SetGeoTransform(get_geo_transform(h, v))
        dst_ds.SetProjection(get_projection())

        dst_ds = None
        src_ds = None


# tile = 'h16v11'
# yr = '2018'
# day = '273'
# h = 16
# v = 11
#
# dirinput = fr'C:\Users\carin\PROPOSTA_DISSERTACAO\Dataset\GOES16_ABI\{tile}\{yr}\{day}'

tile = 'h09v02'
yr = '2018'
day = '001'
h = int(tile[1:3])
v = int(tile[4:6])

input_dir = fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2\maiac\{tile}\{yr}\{day}'

hdf_files = os.listdir(input_dir)

for hdf_file in hdf_files:
    image_path = fr'{input_dir}\{hdf_file}'
    blue_band, red_band, nir_band = extract_bands(image_path)
    export_bands(hdf_file, tile, yr, day, h, v)
