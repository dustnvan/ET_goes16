import glob

import rasterio
import numpy as np
import os
import re
from datetime import datetime, timedelta
def utc_time(local_time):
    # Get the current local time
    now = datetime.now()

    # Convert the input local time to a datetime object
    local_time_obj = datetime.strptime(local_time, "%H%M")

    # Calculate the time difference between local and UTC timezones
    utc_offset = now - datetime.utcnow()

    # Add the offset to the local time to get UTC time
    utc_time_obj = local_time_obj - utc_offset

    # Format the UTC time in military format (HHMM)
    utc_time_str = utc_time_obj.strftime("%H%M")

    return utc_time_str

mosaic_dir = r'Z:\dustin\goes\geonex_l2\mosaic'

geotiff_types = ['ndvi', 'red', 'blue', 'savi', 'nir']

def output_path(mosaic_path):
    # Z:\dustin\goes\geonex_l2\mosaic\2018\001\1415\mosaic_blue_GO16_ABI12B_20180011415_GLBG_02_proj
    time = os.path.basename(mosaic_path).split('_')[4][7:11]
    median_composite =mosaic_path.replace("mosaic", "median_composite")
    med_comp_path = re.sub(rf'\\{time}', '', median_composite, count=1)
    med_comp_path = re.sub(time, '', med_comp_path)

    os.makedirs(os.path.dirname(med_comp_path), exist_ok=True)
    return med_comp_path

date = input('Enter julian date start and end YYYYDDD YYYYDDD: ')
date = date.split(' ')
start_date = datetime.strptime(date[0], '%Y%j')
end_date = datetime.strptime(date[1], '%Y%j')

tiles = input('Select which tiles to merge (h14v03 h15v03 h14v04 h15v04) : ')
tiles = tiles.split(' ')
numOfTiles = len(tiles)

noDataVal = -28672

current_date = start_date
while current_date <= end_date:
    current_yr = str(current_date.year)
    current_julian = current_date.strftime('%j')

    day_path = os.path.join(mosaic_dir, current_yr, current_julian)

    for bnd in geotiff_types:
        print(f'Processing {bnd} mosaics for day {os.path.basename(day_path)}')
        mosaic_files = glob.glob(os.path.join(day_path, '**', f'mosaic_{bnd}*proj.tif'))

        # Open all GeoTIFF files and read the data into a NumPy array
        data_stack = []
        for file_path in mosaic_files:
            # only stacking times 9-3
            time = os.path.basename(file_path).split('_')[4][7:11]
            if utc_time('0900') <= time <= utc_time('1500'):
                with rasterio.open(file_path) as src:
                    data_stack.append(src.read(1))  # Read the first band

        # Stack the data along a new axis to create a 3D array
        data_stack = np.stack(data_stack, axis=0)

        # Convert noData to np.nan
        data_stack = np.where(data_stack <= noDataVal, np.nan, data_stack)

        # Perform median compositing along the time axis (axis=0)
        median_composite = np.nanmedian(data_stack, axis=0)

        output_p = output_path(mosaic_files[0])
        # Save the resulting median composite as a new GeoTIFF file
        with rasterio.open(mosaic_files[0]) as src:
            profile = src.profile.copy()
            profile.update(count=1, dtype=rasterio.float32,
                           nodata=np.nan)  # Update metadata for a single-band output

            with rasterio.open(output_p, 'w', **profile) as dst:
                # Write the median composite data
                dst.write(median_composite, 1)

        print("Median compositing completed. Result saved to:", output_p)

    current_date += timedelta(days=1)












