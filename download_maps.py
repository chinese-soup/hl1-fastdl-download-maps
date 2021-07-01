#!/usr/bin/env python3

import argparse
import urllib.request

import sys
import requests
import os

from pathlib import Path

class Main():
    def __init__(self, args):
        super(Main, self).__init__()
        self.url = args.fastdl_url
        self.map_list_filename = args.map_list
        self.output_dir = args.output_dir

        self.rq = requests.session()
        self.rq.headers = {"User-Agent": "Valve/Steam HTTP Client 1.0 (70)"} # We are a Half-Life client ;)

        if self.url[-1] == "/":
            self.url = self.url[:-1]
            print(f"Info: Removed trailing slash from self.url! URL is now: {self.url}")

        if self.output_dir[-1] == "/":
            self.output_dir = self.output_dir[:-1] # TODO: Change to Pathlib stuff
            print(f"Info: Removed trailing slash from self.output_dir! Output dir is now: {self.output_dir}")

        if not os.path.exists(self.output_dir):
            print(f"Info created directory {self.output_dir}")
            os.makedirs(self.output_dir)

        self.main()

    def main(self):
        map_list_dirty = self.load_map_list()
        map_list = self.clean_up_list(map_list_dirty)

        for n, map_name in enumerate(map_list):
            print(f"======= START: {n+1}/{len(map_list)} - Map name: {map_name} =====")

            resfile_req_obj = self.download_res_file(map_name)
            if resfile_req_obj is not None:
                self.create_dir(f"{self.output_dir}/maps/") # TOOD: This has to be dynamic
                with open(Path(f"{self.output_dir}/maps/{map_name}.res"), "w") as f:
                    print("Writing res file.")
                    f.write(resfile_req_obj.text)

                paths_to_resources = self.parse_res_file(resfile_req_obj.text)
                if paths_to_resources != []:
                    for x, res_path in enumerate(paths_to_resources):
                        print(f"Info: Attempting to download {res_path} - {x+1}/{len(paths_to_resources)}")
                        result = self.download_file(res_path)
                        if result is False:
                            print("==== Download failed, file already exists.")
                        elif result is None:
                            print("==== Download failed.")
                        else:
                            print("==== Download successful.")
            else:
                print("Info: Res file download not found. Gonna attempt to just grab the .bsp")

            print(f"Info: Attempting to download BSP: maps{map_name}.bsp")
            result = self.download_file(f"maps/{map_name}.bsp")
            if result is False:
                print("==== Download failed, file already exists.")
            elif result is None:
                print("==== Download failed.")
            else:
                print("==== Download successful.")

            print(f"\n======= DONE: {n+1}/{len(map_list)} - Map name: {map_name} =======\n")

    @staticmethod
    def create_dir(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def GET(self, relative_path):
        print(f"GETting {self.url}/{relative_path}")
        return self.rq.get(f"{self.url}/{relative_path}")

    def download_file(self, relative_path):
        # First create a directory structure if it doesn't exist

        path_no_filename = f"{self.output_dir}/{os.path.dirname(relative_path)}"
        path_no_filename_Path_obj = Path(path_no_filename)

        filename = os.path.basename(relative_path)

        full_path_final = f"{path_no_filename}/{filename}"

        if not path_no_filename_Path_obj.exists():
            print(f"====== Creating dir {self.output_dir}/{os.path.dirname(relative_path)}")
            path_no_filename_Path_obj.mkdir(parents=True, exist_ok=True)
        else:
            pass # Directory structure already exists

        if Path(full_path_final).exists():
            print(f"====== Info: This file already exists: {full_path_final}")
            return False
        try:
            urllib.request.urlretrieve(f"{self.url}/{relative_path}", full_path_final)
        except urllib.request.HTTPError as e:
            if e.code == 404:
                print(f"====== Info: Failed to download file. Does not exist on server: {e.code}")
            else:
                print(f"====== Info: Failed to download file, unknown error: {e}.")
            return
        except BaseException as e:
            print(f"====== Info: Failed to download file {e}.")
            return

        if Path(full_path_final).exists():
            return True

    def load_map_list(self):
        with open(self.map_list_filename) as f:
            return f.read().splitlines()

    def clean_up_list(self, map_list_dirty):
        return [x.replace(".bsp", "") for x in map_list_dirty]

    def download_res_file(self, map_name):
        resfile_req = self.GET(f"maps/{map_name}.res")

        if resfile_req.status_code == 200:
            return resfile_req

        elif resfile_req.status_code == 404:
            print(f"Error grabbing /maps/{map_name}.res, not found. Map probably doesn't have res file, skipping.")
            return

        else:
            print(f"Error grabbing /maps/{map_name}.res, status code: {resfile_req.status_code}")
            return

    def parse_res_file(self, resfile_str):
        print("Parsing downloaded res file.")
        path_lines = []

        for line in resfile_str.splitlines():
            if line.startswith("//") or len(line) == 0 or len(line) == 1:
                pass
            else:
                path_lines.append(line.strip())

        return path_lines


class Arguments(argparse.ArgumentParser):
    def __init__(self):
        super(Arguments, self).__init__(description="Download .bsp files with all the resources (based on .res files) from a FastDL server based on a text file list")

        # self.add_argument("start_ts", type=int)

        self.add_argument("--fastdl-url", type=str,
                          help="Specify a base FastDL url (WITH gamemode folder name!) for downloading")

        self.add_argument("--map-list", type=str, default="saved-maps.txt",
                          help="Specify a filename of a newlined list of maps (and their resources) you wish to download (1 map per line) (default: %(default)s)")

        self.add_argument("--output-dir", type=str,
                          help="Specify a base directory in which the downloaded directory structure will be saved to (default: %(default)s)", default="downloaded_maps/")

if __name__ == "__main__":
    arguments_parser = Arguments()
    args = arguments_parser.parse_args()
    if not args.fastdl_url:
        print("You need to provide a FastDL base URL, e.g. ./download_maps.py --fast-dl-url http://127.0.0.1/")
        sys.exit(1)

    print(f"{args}")
    Main(args)