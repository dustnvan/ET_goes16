import os
import glob
import time
import sys
from multiprocessing import set_start_method
set_start_method('spawn', force=True)
import multiprocessing
from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import cv2

import warnings
import numpy.ma as ma
import xarray as xr
import rioxarray as rxr
from shapely.geometry import mapping, box
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

from osgeo import gdal, osr

warnings.simplefilter('ignore')

tile = 'h16v11'
yr = '2018'
day = '273'
h = 16
v = 11

dirinput = fr'C:\Users\carin\PROPOSTA_DISSERTACAO\Dataset\GOES16_ABI\{tile}\{yr}\{day}'

fils = os.listdir(dirinput)

for filenm in fils:
    image_path = fr'{dirinput}\{filenm}'
    # Open data with rioxarray
    image = rxr.open_rasterio(image_path, masked=True)
    image_1km = image[0]
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

    nm_bands = ["blue", "red", "nir"]

    for bnd in nm_bands:
        new_filenm = bnd + '_' + filenm + '.tif'
        new_filenmp = bnd + '_' + filenm + '_proj' + '.tif'
        save_path = fr'C:\Users\carin\PROPOSTA_DISSERTACAO\Dataset\images\GOES16_ABI\{tile}\{yr}\{day}'

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

        gt1 = [lon_ulcnr, 0.01, 0.0, lat_ulcnr, 0.0, -0.01]

        src_filename = fr'{save_path}\{new_filenm}'
        dst_filename = fr'{save_path}\{new_filenmp}'

        # Opens source dataset
        src_ds = gdal.Open(src_filename)
        format = "GTiff"
        driver = gdal.GetDriverByName(format)

        # Open destination dataset
        dst_ds = driver.CreateCopy(dst_filename, src_ds, 0)

        # Set location
        dst_ds.SetGeoTransform(gt1)

        # Get raster projection
        epsg = 4326
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        dest_wkt = srs.ExportToWkt()

        # Set projection
        dst_ds.SetProjection(dest_wkt)

        # Close files
        dst_ds = None
        src_ds = None