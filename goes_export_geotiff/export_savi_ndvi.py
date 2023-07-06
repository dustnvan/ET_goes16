from osgeo import gdal
import numpy as np
# calculating SAVI and NDVI

noDataVal = -28672
def calculate_ndvi(nir, red):
    valid_mask = np.where(nir!=noDataVal, True, False) & np.where(red!=noDataVal, True,False)
    ndvi_band = np.where(valid_mask, (nir - red) / (nir + red), np.nan)
    return ndvi_band

# Function to calculate SAVI
def calculate_savi(nir, red):
    soil_factor = 0.5
    valid_pixels = (nir > noDataVal) & (red > noDataVal)
    savi_band = np.where(valid_pixels,((1 + soil_factor) * (nir - red)) / (nir + red + soil_factor),np.nan)
    return savi_band

def export_geotiff(src_dataset, band, output_path):
    # Get the geotransform from the NIR dataset
    geotransform = src_dataset.GetGeoTransform()

    # Create the output GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    output_dataset = driver.Create(output_path, src_dataset.RasterXSize, src_dataset.RasterYSize, 1, gdal.GDT_Float32)

    # Set the geotransform and projection
    output_dataset.SetGeoTransform(geotransform)
    output_dataset.SetProjection(src_dataset.GetProjection())

    # Write the SAVI band to the output GeoTIFF
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(band)

    # Flush data to disk and close the output GeoTIFF
    output_band.FlushCache()
    output_dataset.FlushCache()
    output_dataset = None

def export_savi_ndvi(nir_path, red_path):
    savi_output_path = nir_path.replace("nir", "savi")
    ndvi_output_path = nir_path.replace("nir", "ndvi")

    # Open NIR and red GeoTIFF files
    nir_dataset = gdal.Open(nir_path)
    red_dataset = gdal.Open(red_path)

    # Read NIR and red bands as NumPy arrays
    nir_band = nir_dataset.GetRasterBand(1).ReadAsArray()
    red_band = red_dataset.GetRasterBand(1).ReadAsArray()

    savi_band = calculate_savi(nir_band, red_band)
    ndvi_band = calculate_ndvi(nir_band, red_band)

    export_geotiff(nir_dataset, savi_band, savi_output_path)
    export_geotiff(nir_dataset, ndvi_band, ndvi_output_path)

    print('exported', savi_output_path)
    print('exported', ndvi_output_path)


# Paths to NIR and red GeoTIFF files
# nir_path = r'C:\Users\dusti\Desktop\GCERlab\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\nir_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'
# red_path = r'C:\Users\dusti\Desktop\GCERlab\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\red_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'

# nir_path = r'C:\Users\dnv22\Desktop\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\nir_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'
# red_path= r'C:\Users\dnv22\Desktop\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\red_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'
# export_savi_ndvi(nir_path, red_path)