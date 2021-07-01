# hl1-fastdl-download-maps
This simple script downloads GoldSrc maps specified in a text file from a FastDL server you specify.

FastDL servers are used in-game to download maps and other resources faster.

The script **is resources aware** and if a `.res` file exists for the map on the FastDL server, 
the `.res file` and all resources in it, get downloaded as well, while keeping the correct directory structure.

You can get a FastDL server's URL simply from the console after connecting to a server with FastDL, the in-game console will print:
```Using http://127.0.0.1/ as primary download location``` 
or
```Saved http://127.0.0.1/maps/map_name.bsp to disk```
where "http://hostname/" is the URL.

An example map list with the correct format (one map per line)
is available in the **[saved-maps.txt](saved-maps.txt)** file.


# Usage
```
usage: download_maps.py [-h] [--fastdl-url FASTDL_URL] [--map-list MAP_LIST]
                        [--output-dir OUTPUT_DIR]

Download .bsp files with all the resources (based on .res files) from a FastDL
server based on a text file list

optional arguments:
  -h, --help            show this help message and exit
  --fastdl-url FASTDL_URL
                        Specify a base FastDL url (WITH gamemode folder name!)
                        for downloading
  --map-list MAP_LIST   Specify a filename of a newlined list of maps (and
                        their resources) you wish to download (1 map per line)
                        (default: saved-maps.txt)
  --output-dir OUTPUT_DIR
                        Specify a base directory in which the downloaded
                        directory structure will be saved to (default:
                        downloaded_maps/)
```

# Known bugs
* The script doesn't check if the file was actually downloaded in its entirety (it only checks if the file exists), because I'm lazy
* Script is non-portable (path splits are basically hardcoded), working on Linux/Unix only.
* and a lot more, probably, that I already forgot.

# Requirements
* Python 3.6+ *(3.5 if you remove F-strings)*

## Libraries
### External
* [requests](https://github.com/psf/requests)
### Standard
* urllib3, argparse