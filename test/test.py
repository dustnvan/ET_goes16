import re

path = r'Z:\dustin\goes\geonex_l2\geotiffs\h14v04\2018\001\1400\blue_GO16_ABI12B_20180011400_GLBG_h14v04_02'

# Remove the first occurrence of the tile and extra backslashes
mosaic_path = re.sub(r"\\h\d{2}v\d{2}", "", path, count=1)
mosaic_path = re.sub(r"h\d{2}v\d{2}_", "", path)
mosaic_path= mosaic_path.replace("geotiffs", "mosaic")
mosaic_path = mosaic_path.replace("savi", "mosaic_savi")
mosaic_path = mosaic_path.replace("ndvi", "mosaic_ndvi")
mosaic_path = mosaic_path.replace("red", "mosaic_red")
mosaic_path = mosaic_path.replace("blue", "mosaic_blue")
mosaic_path = mosaic_path.replace("nir", "mosaic_nir")

print(mosaic_path)

value = [r'Z:\dustin\goes\geonex_l2\geotiffs\h14v04\2018\001\1400\blue_GO16_ABI12B_20180011400_GLBG_h14v04_02']

# mosaic_path = re.sub(r'h\d+v\d+', '', value[0])

#
# print(mosaic_path)