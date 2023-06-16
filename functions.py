# converting timezones
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

def convert_to_local_time(utc_time_str, latitude, longitude):
    # Parse the input UTC time string and extract hours and minutes
    hours = int(utc_time_str[:2])
    minutes = int(utc_time_str[2:])

    # Create a TimezoneFinder object
    tf = TimezoneFinder()

    # Get the timezone based on the provided coordinates
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

    if timezone_str is None:
        return "Unable to determine the timezone for the given coordinates."

    # Get the current UTC time
    utc_now = datetime.utcnow()

    # Set the hours and minutes to the current UTC time
    utc_time = utc_now.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    # Get the timezone object
    timezone = pytz.timezone(timezone_str)

    # Specify that the input time is in UTC
    utc_time = pytz.utc.localize(utc_time)

    # Convert UTC time to local time
    local_time = utc_time.astimezone(timezone)

    # Format the local time as a string in the same format as the input
    local_time_str = local_time.strftime('%H%M')

    return local_time_str

utc_time = '1623'
latitude = 35
longitude = -95

local_time = convert_to_local_time(utc_time, latitude, longitude)
print(local_time)










# Finding Pixel
def find_pixel(geotiff_path):
    # Open the GeoTIFF file
    dataset = gdal.Open(geotiff_path)

    # Get the geotransform (georeferencing information)
    geotransform = dataset.GetGeoTransform()
    band = dataset.GetRasterBand(1)  # Assuming it's the first (and only) band
        # Read the band as a NumPy array
    band_array = band.ReadAsArray()
    print(band_array)
    # Extract the necessary values from the geotransform
    origin_x = geotransform[0]  # top-left x coordinate
    origin_y = geotransform[3]  # top-left y coordinate
    pixel_width = geotransform[1]  # width of a pixel
    pixel_height = geotransform[5]  # height of a pixel

    print("Origin X:", origin_x)
    print("Origin Y:", origin_y)
    print("Pixel Width:", pixel_width)
    print("Pixel Height:", pixel_height)

    print()

    # Define the target coordinate
    target_x = -96
    target_y = 36

    # Convert the spatial coordinates to pixel coordinates
    pixel_x = int((target_x - origin_x) / pixel_width)
    pixel_y = int((target_y - origin_y) / pixel_height)

    # Print the row and column indices
    print("Row:", pixel_y)
    print("Column:", pixel_x)


# Get the reflectance
def get_reflectance_value(geotiff_path, y, x):
    dataset = gdal.Open(geotiff_path)

    band = dataset.GetRasterBand(1)  # Assuming it's the first (and only) band
    # Read the band as a NumPy array
    band_array = band.ReadAsArray()

    return band_array[y][x]



import numpy as np
# calculating SAVI and NDVI
def get_savi_band(nir, red):
    soil_factor = .5

    savi_band = ((1 + soil_factor) * (nir - red)) / (nir + red + soil_factor)
    return savi_band

# calculate savi from landsat bands and export geotiff
# make mask
def calculate_ndvi(nir, red):
    ndvi = (nir - red) / (nir + red)
    return ndvi


from osgeo import gdal

# Function to calculate SAVI
def calculate_savi(nir, red):
    soil_factor = 0.5
    savi_band = ((1 + soil_factor) * (nir - red)) / (nir + red + soil_factor)
    return savi_band

def export_geotiff(src_dataset, output_path):
    # Get the geotransform from the NIR dataset
    geotransform = src_dataset.GetGeoTransform()

    # Create the output GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    output_dataset = driver.Create(output_path, nir_dataset.RasterXSize, nir_dataset.RasterYSize, 1, gdal.GDT_Float32)

    # Set the geotransform and projection
    output_dataset.SetGeoTransform(geotransform)
    output_dataset.SetProjection(nir_dataset.GetProjection())

    # Write the SAVI band to the output GeoTIFF
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(savi_band)

    # Flush data to disk and close the output GeoTIFF
    output_band.FlushCache()
    output_dataset.FlushCache()
    output_dataset = None


# Paths to NIR and red GeoTIFF files
nir_path = r'C:\Users\dusti\Desktop\GCERlab\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\nir_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'
red_path = r'C:\Users\dusti\Desktop\GCERlab\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\red_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'

# Output path for the SAVI GeoTIFF
output_path = r'C:\Users\dusti\Desktop\GCERlab\ET_goes16\download_goes\datasets\images\goes\goes16\geonexl2\geotiffs\h14v04\2018\001\1600\savi_GO16_ABI12B_20180011600_GLBG_h14v04_02_proj.tif'

# Open NIR and red GeoTIFF files
nir_dataset = gdal.Open(nir_path)
red_dataset = gdal.Open(red_path)

# Read NIR and red bands as NumPy arrays
nir_band = nir_dataset.GetRasterBand(1).ReadAsArray()
red_band = red_dataset.GetRasterBand(1).ReadAsArray()

print(nir_band)
print(red_band)
# Calculate SAVI
savi_band = calculate_savi(nir_band, red_band)
export_geotiff(nir_dataset, output_path)

print("SAVI Band:", savi_band)

