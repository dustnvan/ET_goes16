from osgeo import gdal
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def find_pixel_reflectance(mosaic_path, lat, lon):
    if not os.path.exists(mosaic_path):
        return
    # Open the GeoTIFF file
    dataset = gdal.Open(mosaic_path)

    # Get the geotransform (georeferencing information)
    transform = dataset.GetGeoTransform()

    # Extract the pixel size in the X and Y direction
    pixel_width = transform[1]
    pixel_height = transform[5]

    # Calculate the column (X) and row (Y) indices based on the latitude and longitude
    col = int((lon - transform[0]) / pixel_width)
    row = int((lat - transform[3]) / pixel_height)

    band = dataset.GetRasterBand(1)  # Assuming it's the first (and only) band
    # Read the band as a NumPy array
    band_array = band.ReadAsArray()

    return band_array[row][col]

def get_latlon(crop):
    corn = (32.9773165, -91.2361683)  # 32.9773165°N 91.2361683°W
    cotton = (32.9701765, -91.2541966)  # 32.9701765°N 91.2541966°W
    soybeans = (33.0022170, -91.2512514)  # 33.0022170°N 91.2512514°W

    if crop == 'corn': return corn
    if crop == 'cotton': return cotton
    if crop == 'soybeans': return soybeans

def get_arr(crop):
    if crop == 'corn': return corn_refl
    if crop == 'cotton': return cotton_refl
    if crop == 'soybeans': return soybeans_refl

# Plotting NDVI for 2018
start_date = '2018001'
end_date = '2018365'
start_date = datetime.strptime(start_date, '%Y%j')
end_date = datetime.strptime(end_date, '%Y%j')

crops = ['corn', 'cotton', 'soybeans']

corn_refl = []
cotton_refl = []
soybeans_refl = []

median_mosaic_dir = r'D:\dustin\goes\geonex_l2\median_composite'

current_date = start_date
while current_date <= end_date:
    current_yr = str(current_date.year)
    current_julian = current_date.strftime('%j')

    input_path = os.path.join(median_mosaic_dir, current_yr, current_julian, f'median_composite_ndvi_GO16_ABI12B_{current_yr}{current_julian}_GLBG_02_proj.tif')
    for crop in crops:
        lat, lon = get_latlon(crop)
        px_refl = find_pixel_reflectance(input_path, lat, lon)
        get_arr(crop).append(px_refl)




    current_date += timedelta(days=1)


year = str(start_date.year)
output_dir = os.path.join(median_mosaic_dir, 'ndvi_crops')
os.makedirs(output_dir, exist_ok=True)

for crop in crops:
    crop_arr = get_arr(crop)
    plt.scatter(range(len(crop_arr)), crop_arr)

    plt.title(f'NDVI {crop.capitalize()} {year}')


    file_name = f'ndvi_{crop}_{year}'
    plt.savefig(os.path.join(output_dir, file_name))
    plt.clf()

    print('saved:', file_name)
