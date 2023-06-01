import os
import glob
import time
import sys
from multiprocessing import set_start_method
set_start_method('spawn', force=True)
import multiprocessing

def imgcontrast(imgrgb):
    import cv2
    import numpy as np
    alpha = 7  # Contrast control (1.0-3.0)
    beta = 35  # Brightness control (0-100)
    enhanced_img = cv2.convertScaleAbs(imgrgb, alpha=alpha, beta=beta)

    return enhanced_img


import os
from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import cv2
#GRS80 ellipsoid,
subset_position_surf1km = 0
subset_position_surf500 = 2
subset_position_QA = 1

tile = 'h14v05'
yr = '2018'

for day in range(126, 131):

    day = str(day).zfill(3)
    threshold_refl_max = 1

    dirinput = fr'Y:\datasets\images\goes\goes16\geonexl2\maiac\{tile}\{yr}\{day}'

    #filenm = 'GO16_ABI12B_20181911515_GLBG_h20v10_02.hdf'

    fils=os.listdir(dirinput)

    for filenm in fils:
        input_hdf_path=fr'{dirinput}\{filenm}'
        src = gdal.Open(input_hdf_path)

        band_ds = src.GetSubDatasets()
        checkband=False
        for i, band in enumerate(band_ds):
            print(band)
            if "sur_refl_500m" in band[0]:
                checkband=True

        if checkband:
            src = gdal.Open(input_hdf_path)

            # 500 m
            # band_ds = gdal.Open(src.GetSubDatasets()[2][0])
            # BAND2_red = band_ds.ReadAsArray()*0.0001
            # BAND2_red = np.where(BAND2_red < 0, 0, BAND2_red)
            # BAND2_red = np.where(BAND2_red > 0.5, 0.5, BAND2_red)
            # BAND2_red = cv2.resize(BAND2_red, dsize=(600, 600), interpolation=cv2.INTER_NEAREST)

            band_ds = gdal.Open(src.GetSubDatasets()[0][0])  # 1km
            BANDS_1km = band_ds.ReadAsArray() * 0.0001
            BANDS_1km = np.where(BANDS_1km < 0, 0, BANDS_1km)
            BANDS_1km = np.where(BANDS_1km > threshold_refl_max, threshold_refl_max, BANDS_1km)

            sr_raw = np.zeros((600, 600, 4))
            for xo in range(0, 4):
                for io in range(0, 600):
                    for jo in range(0, 600):
                        sr_raw[io, jo, xo] = BANDS_1km[xo, io, jo]

            BANDS_1km = sr_raw.copy()

            BAND1_blue = BANDS_1km[:,:,0]
            BAND2_red = BANDS_1km[:, :, 1]
            BAND3_nir = BANDS_1km[:, :, 2]
            #BAND5_nir16 = BANDS_1km[:, :, 3]

            # QA
            band_ds = gdal.Open(src.GetSubDatasets()[subset_position_QA][0])
            QA_array = band_ds.ReadAsArray()
            clear_pixel = np.where(np.bitwise_and(QA_array.astype(np.int16), 0b0000000000000001) > 0, 1, 0)  # clear pixel
            water_pixel = np.where(np.bitwise_and(QA_array.astype(np.int16), 0b0000000000001000) > 0, 1, 0)  # water pixel

            for xo in range(0, 4):
                #sr_raw[:, :, xo] = np.where(clear_pixel == 0, 0, sr_raw[:, :, xo])
                sr_raw[:, :, xo] = np.where(water_pixel == 1, sr_raw[:, :, xo], 0)


            output_ = fr'Y:\datasets\images\goes\goes16\geonexl2\browser\{tile}\{yr}\{day}'
            os.makedirs(output_, exist_ok=True)
            output_png = fr'{output_}\{filenm.replace(".hdf", ".tif")}'

            arr = (BANDS_1km * 255).astype(np.uint8)

            plt.ioff()
            fig = plt.figure()
            fig.set_size_inches(8.5, 6.5)
            R = (BAND2_red * 255).astype(np.uint8)
            # G = (BAND3_nir * 255).astype(np.uint8)
            G = (0.45 * BAND2_red) + (0.1 * BAND3_nir) + (0.45 * BAND1_blue)
            G = (G * 255).astype(np.uint8)
            B = (BAND1_blue * 255).astype(np.uint8)

            imgrgb = np.dstack((R, G, B))

            imgrgb = imgcontrast(imgrgb)

            plt.imshow(imgrgb)
            plt.xticks([])
            plt.yticks([])
            plt.title(filenm.split("_")[2][-4:])

            plt.savefig(output_png, bbox_inches='tight', dpi=150)
            plt.close()
