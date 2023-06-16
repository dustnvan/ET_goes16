import os.path
import requests
import h5py
import time


# checks if website is running
def website_check():
    retry_delay = 1

    url = 'https://data.nas.nasa.gov/geonex/data.php'
    while True:
        try:
            response = requests.head(url)
            if response.status_code == 200:
                return True
            else:
                print(f"Website is not available. Pausing script... {retry_delay} seconds")
                time.sleep(retry_delay)  # Pause for 60 seconds before checking again

        except requests.ConnectionError:
            print(f"Website is not available. Pausing script... {retry_delay} seconds")
            time.sleep(retry_delay)  # Pause for 60 seconds before checking again

        retry_delay *= 2

# finds the URLS of the hdf file downloads
def get_hdf(url_base):
    if website_check():
        hdf_list = []
        url = requests.get(url_base)
        htmltext = url.text

        for line in htmltext.split('\n'):
            if 'href="/geonex' in line:
                line_hdf = line.split('href="')[1]
                if 'hdf' in line_hdf and 'ABI12B' in line_hdf:
                    line_hdf1 = "https://data.nas.nasa.gov" + line_hdf.split(".hdf")[0] + ".hdf"
                    hdf_list.append(line_hdf1)
        return hdf_list


# downloads hdf file
def download_file(url, filename):
    if website_check():
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)


# checks for not downloaded or corrupt files
def check_hdf_file(file_path):
    try:
        # Open the HDF file in read-only mode
        with h5py.File(file_path, 'r') as file:
            # Access any dataset or group to ensure the file is readable
            _ = file['/']
            print("HDF file is valid and can be opened.")
            return 1
    except OSError as e:
        print("Error opening HDF file:", e)
        return 0
    except KeyError as e:
        print("HDF file is corrupt:", e)
        return 0


# does a file check and attempts to redownload if bad file
def redownload_hdf_files(url, filename):
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        if not check_hdf_file(filename):
            print("File not opening. Redownloading...")
            download_file(url, filename)
        else:
            return
        attempts += 1

    print("File cannot be downloaded. Skipping file.")


if __name__ == '__main__':
    # basiclink = 'https://data.nas.nasa.gov/geonex/geonexdata/GOES16/GEONEX-L1G/'
    # output_dir = 'C:\datasets\images\goes\goes16\geonexl1g'

    basiclink = 'https://data.nas.nasa.gov/geonex/geonexdata/GOES16/GEONEX-L2/MAIAC'
    # output_dir = 'Y:\datasets\images\goes\goes16\geonexl2\maiac'
    output_dir = 'datasets\images\goes\goes16\geonexl2\maiac'

    years_init = 2018
    years_end = 2019

    dates_init = 1
    dates_end = 365
    tiles = ['h14v04']  # Amazon 'h20v10', 'h21v10', 'h19v10','h20v09'  # MS h15v04 h14v04 h14v05 h15v05

    hdf_file_map = {}  # file name : download url

    for tile in tiles:
        for year in range(years_init, years_end+1):
            for day in range(dates_init, dates_end + 1):
                # Creating directories
                year = str(year).zfill(4)
                day = str(day).zfill(3)

                dir_yrdt = f'{output_dir}\\{tile}\\{year}\\{day}\\'
                os.makedirs(dir_yrdt, exist_ok=True)

                # getting hdf file urls
                url_base = f'{basiclink}/{tile}/{year}/{day}/'
                hdf_list = get_hdf(url_base)

                # creating hdf file name and linking it to its URL
                for hdf_file in hdf_list:
                    filename_save = rf'{dir_yrdt}\{os.path.basename(hdf_file)}'
                    if not os.path.exists(filename_save):
                        hdf_file_map[filename_save] = hdf_file
                        # filename_saves.append(filename_save)
                        # hdf_links.append(hdf_file)

                # downloads hdf file to its corresponding directory
                for filename, hdf_link in hdf_file_map.items():
                    download_file(hdf_link, filename)
                    print(f"downloaded: {hdf_link}")

    # checks for files not downloaded or corrupted
    # for filename, hdf_link in hdf_file_map.items():
    #     redownload_hdf_files(filename, hdf_link)

