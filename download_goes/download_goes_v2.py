import requests
import time
import os

# checks if website is running
def make_request(url, stream=False, timeout=None):
    retry_delay = 1

    while True:
        try:
            response = requests.get(url, stream=stream, timeout=timeout)
            if response.status_code == 200:
                return response
            else:
                print(f"Website is not available. Pausing script... {retry_delay} seconds")
                time.sleep(retry_delay)  # Pause for 60 seconds before checking again

        except requests.ConnectionError:
            print(f"Website is not available. Pausing script... {retry_delay} seconds")
            time.sleep(retry_delay)  # Pause for 60 seconds before checking again

        retry_delay *= 2


# finds the URLS of the hdf file downloads
def get_hdf(url_base):
    hdf_list = []
    url = make_request(url_base)
    htmltext = url.text

    for line in htmltext.split('\n'):
        if 'href="/geonex' in line:
            line_hdf = line.split('href="')[1]
            if 'hdf' in line_hdf and 'ABI12B' in line_hdf:
                line_hdf1 = "https://data.nas.nasa.gov" + line_hdf.split(".hdf")[0] + ".hdf"
                hdf_list.append(line_hdf1)
    return hdf_list


# downloads hdf file
def download_file(url, hdf):
    # NOTE the stream=True parameter below
    with make_request(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(hdf, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
            print('downloaded:', hdf)


if __name__ == '__main__':
    basiclink = 'https://data.nas.nasa.gov/geonex/geonexdata/GOES16/GEONEX-L2/MAIAC'
    output_dir = r'Z:\dustin\goes\geonex_l2\data_raw'

    date = input('Enter julian date start and end YYYYDDD YYYYDDD: ')
    date = date.split(' ')

    start_date = int(date[0])
    end_date = int(date[1])

    tile = input('Choose a tile (h14v03 h14v04 h15v03 h15v04): ')

    current_date = start_date
    while current_date <= end_date:
        current_yr = str(current_date)[0:4]
        current_julian = str(current_date)[4:7]

        dir_dst = os.path.join(output_dir, tile, current_yr, current_julian)
        os.makedirs(dir_dst, exist_ok=True)

        # getting hdf file urls
        url_base = f'{basiclink}/{tile}/{current_yr}/{current_julian}/'
        hdf_list = get_hdf(url_base)  # contains all the links for hdf downloads in the day

        # creating hdf file path and linking it to its URL
        for hdf_file in hdf_list:
            hdf_path = os.path.join(dir_dst, os.path.basename(hdf_file))
            if not os.path.exists(hdf_path):
                # downloads file
                download_file(hdf_file, hdf_path)
            else:
                print(hdf_path, 'already exists')

        current_date += 1



