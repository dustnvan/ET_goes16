import os
import glob
import re

# Define the path to the geotiff directory which contains all tiles
geotiff_directory = "Z:\dustin\goes\geonex_l2\geotiffs"
numOfTiles = len(os.listdir(geotiff_directory))

geotiff_files = glob.glob(os.path.join(geotiff_directory, "**/*proj.tif"), recursive=True)  # list of fullpaths to geotiff files

# Step 1: Iterate over each file
hashm = {}
for file_path in geotiff_files:
    band_substring = os.path.basename(file_path).split("_")[0]  # getting the band from the geotiff file name
    time_substring = os.path.basename(file_path).split("_")[3]  # getting the time from the geotiff file name

    substring_gen = band_substring + time_substring

    # Step 3: Create dictionary with substrings as keys and corresponding file paths as values
    if substring_gen in hashm:
        hashm[band_substring + time_substring].append(file_path)
    else:
        hashm[band_substring + time_substring] = [file_path]

print('hashmap created')

# Step 4: Check if the four tiles have that time
for key, value in hashm.items():
    if len(value) == numOfTiles:
        # Step 5: Perform the desired action with the four file paths

        # making new file path from Z:\dustin\goes\geonex_l2\geotiffs\h14v03\2018\001\1415
        mosaic_path = re.sub(r'h\d+v\d+', '', value[0])
        mosaic_path= mosaic_path.replace("geotiffs", "mosaic")
        mosaic_path = mosaic_path.replace("savi", "mosaic_savi")
        mosaic_path = mosaic_path.replace("ndvi", "mosaic_ndvi")
        mosaic_path = mosaic_path.replace("red", "mosaic_red")
        mosaic_path = mosaic_path.replace("blue", "mosaic_blue")
        mosaic_path = mosaic_path.replace("nir", "mosaic_nir")

        os.makedirs(os.path.dirname(mosaic_path), exist_ok=True)

        command = "gdalwarp -overwrite -wo COLOR_CORRECTION=YES " + ' '.join(value) + " " + mosaic_path

        os.system(command)

        print('exported: ', os.path.basename(mosaic_path))
        # Step 6: Remove or mark the processed files to avoid repeating the action
        for file_path in value:
            geotiff_files.remove(file_path)
