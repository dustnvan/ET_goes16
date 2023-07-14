# Evapotranspiration Estimation
This repository contains multiple scripts with the goal of getting the necessary parameters (Normalized Difference Vegetation Index) to remotely calculate evapotranspiration at crop fields.

### download_goes
- automatically downloads satellite images from GOES-16, a geostationary satellite that captures images every 15 minutes
- [Geonex data portal](https://data.nas.nasa.gov/geonex/geonexdata/GOES16/GEONEX-L2/MAIAC/)
- We focused on **h14v03 h15v03 h14v04 h15v04** regions as you can see [here](https://www.nasa.gov/sites/default/files/thumbnails/image/globalgrid_v3.png)
### goes_export_geotiff
- Once we have these raster files, we export single-band GeoTIFFs with the red or nir bands.
- With this formula NDVI = (NIR - R) / (NIR + R) we are able to now see the NDVI at each pixel of our satellite image
### mosaic
  - A mosaic is a combination of satellite images. So instead of four separate pictures of each region, this script combines them into one picture.
  - Here's a good illustration: <br /> ![Mosaic Example](https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/GUID-BCA5B031-B811-424B-9F54-BAB2224FBAD0-web.gif)
  - In this step, we also combined every mosaic from a given day by using median compositing. This process finds the corresponding pixels of the images on a given day and calculates the median between those pixel reflectance values. We chose to ignore the images outside the times 9 am - 3 pm when calculating the median because the images weren't as useful without sunlight.

###plot_ndvi 
- Includes a script to plot NDVI to easily view NDVI values of a given day
- There is also a plot that can, given coordinates inside the mosaic, will plot the NDVI of that location for every given day the year that the satellite images were captured.
