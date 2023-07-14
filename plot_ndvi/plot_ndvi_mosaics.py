from osgeo import gdal
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os


def julian_to_date(julian_date):
    base_date = datetime(year=2023, month=1, day=1)  # Set the base date as January 1, 2023
    target_date = base_date + timedelta(days=julian_date-1)
    return target_date.strftime('%Y-%m-%d')


median_mosaic_dir = r'D:\dustin\goes\geonex_l2\median_composite'
plot_dir = os.path.join(median_mosaic_dir, 'NDVI_plots')
os.makedirs(plot_dir, exist_ok=True)

date = input('Enter julian date start and end YYYYDDD YYYYDDD: ')
date = date.split(' ')
start_date = datetime.strptime(date[0], '%Y%j')
end_date = datetime.strptime(date[1], '%Y%j')

current_date = start_date
while current_date <= end_date:
    current_yr = str(current_date.year)
    current_julian = current_date.strftime('%j')

    dataset = gdal.Open(os.path.join(median_mosaic_dir, current_yr, current_julian, f'median_composite_ndvi_GO16_ABI12B_{current_yr}{current_julian}_GLBG_02_proj.tif'))

    dataArr = dataset.ReadAsArray()
    # Plot each row as a line
    plt.imshow(dataArr, cmap='viridis')
    plt.colorbar()
    plt.title(f'NDVI {julian_to_date(int(current_julian))}')

    file_name = f'ndvi_plot_{current_yr}{current_julian}'
    plt.savefig(os.path.join(plot_dir, file_name))
    plt.clf()

    print('saved:', file_name)
    current_date += timedelta(days=1)
