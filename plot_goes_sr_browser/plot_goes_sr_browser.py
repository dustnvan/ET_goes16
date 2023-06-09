from multiprocessing import set_start_method

set_start_method('spawn', force=True)


def img_contrast(imgrgb):
    import cv2
    import numpy as np
    alpha = 7  # Contrast control (1.0-3.0)
    beta = 35  # Brightness control (0-100)
    enhanced_img = cv2.convertScaleAbs(imgrgb, alpha=alpha, beta=beta)

    return enhanced_img


def process_bands_1km(src):
    band_ds = gdal.Open(src.GetSubDatasets()[0][0])  # 1km
    BANDS_1km = band_ds.ReadAsArray() * 0.0001  # scaling down the values in the matrix by a factor of 0.0001
    # normalizing data between 0 & 1
    BANDS_1km = np.where(BANDS_1km < 0, 0, BANDS_1km)
    BANDS_1km = np.where(BANDS_1km > 1, 1, BANDS_1km)
    BANDS_1km = BANDS_1km.transpose((1, 2, 0))  # reshapes BANDS_1km from (4, 600, 600) to (600, 600, 4)
    return BANDS_1km


def set_output(path):
    os.makedirs(path, exist_ok=True)
    return fr'{path}\{hdf_file.replace(".hdf", ".tif")}'


def rgb_plot(red_band, blue_band, nir_band):
    # prepare the red, green, and blue channel arrays (R, G, and B) for creating an RGB image plot
    plt.ioff()
    fig = plt.figure()
    fig.set_size_inches(8.5, 6.5)
    R = (red_band * 255).astype(np.uint8)
    # G = (BAND3_nir * 255).astype(np.uint8)
    G = (0.45 * red_band) + (0.1 * nir_band) + (0.45 * blue_band)
    G = (G * 255).astype(np.uint8)
    B = (blue_band * 255).astype(np.uint8)

    imgrgb = np.dstack((R, G, B))

    imgrgb = img_contrast(imgrgb)

    plt.imshow(imgrgb)
    plt.yticks([])
    plt.xticks([])
    plt.title(hdf_file.split("_")[2][-4:])

    plt.savefig(output_png, bbox_inches='tight', dpi=150)
    plt.close()


import os
from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np

# GRS80 ellipsoid,
subset_position_surf1km = 0
subset_position_surf500 = 2
subset_position_QA = 1

tile = 'h09v02'
yr = '2018'

for day in range(1, 2):

    day = str(day).zfill(3)

    # dirinput = fr'Y:\datasets\images\goes\goes16\geonexl2\maiac\{tile}\{yr}\{day}'
    dirinput = fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2\maiac\{tile}\{yr}\{day}'

    hdf_files = os.listdir(dirinput)

    # finds and opens ABI12B hdf files
    for hdf_file in hdf_files:
        input_hdf_path = fr'{dirinput}\{hdf_file}'
        src = gdal.Open(input_hdf_path)

        # band_ds = src.GetSubDatasets()
        # for i, band in enumerate(band_ds):
        #     print(band)

        # 500 m
        # band_ds = gdal.Open(src.GetSubDatasets()[2][0])
        # BAND2_red = band_ds.ReadAsArray()*0.0001
        # BAND2_red = np.where(BAND2_red < 0, 0, BAND2_red)
        # BAND2_red = np.where(BAND2_red > 0.5, 0.5, BAND2_red)
        # BAND2_red = cv2.resize(BAND2_red, dsize=(600, 600), interpolation=cv2.INTER_NEAREST)

        BANDS_1km = process_bands_1km(src)

        BAND1_blue = BANDS_1km[:, :, 0]
        BAND2_red = BANDS_1km[:, :, 1]
        BAND3_nir = BANDS_1km[:, :, 2]
        # BAND5_nir16 = BANDS_1km[:, :, 3]

        # QA
        band_ds = gdal.Open(src.GetSubDatasets()[subset_position_QA][0])
        QA_array = band_ds.ReadAsArray()
        clear_pixel = np.where(np.bitwise_and(QA_array.astype(np.int16), 0b0000000000000001) > 0, 1, 0)  # clear pixel
        water_pixel = np.where(np.bitwise_and(QA_array.astype(np.int16), 0b0000000000001000) > 0, 1, 0)  # water pixel
        sr_raw = BANDS_1km.copy()

        for xo in range(0, 4):
            # sr_raw[:, :, xo] = np.where(clear_pixel == 0, 0, sr_raw[:, :, xo])
            sr_raw[:, :, xo] = np.where(water_pixel == 1, sr_raw[:, :, xo], 0)

        # giving filepath for output
        # output_ = fr'Y:\datasets\images\goes\goes16\geonexl2\browser\{tile}\{yr}\{day}'

        output_png = set_output(fr'C:\Users\dusti\Desktop\GCERlab\GCERLAB_Dustin\download_goes\datasets\images\goes\goes16\geonexl2\browser\{tile}\{yr}\{day}')

        arr = (BANDS_1km * 255).astype(np.uint8)  # scaling values for png image pixel values

        rgb_plot(BAND1_blue, BAND2_red, BAND3_nir)

        print("created: ", output_png)
