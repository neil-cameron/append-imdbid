import argparse
import json
import os
from urllib.request import urlopen

import config
import examples

parser = argparse.ArgumentParser()

# Arguments
parser.add_argument(
    "path",
    nargs="+",
    type=str,
    help="A full or relative path to a file, several files, a directory, or several directories of items to append the IMDBID and year to",
)

args = parser.parse_args()

# Parse arguments
list_of_paths = []
if args.path:
    [list_of_paths.append(individual_path) for individual_path in args.path]


# Test data
list_of_paths = examples.examples
ignore_filenames = examples.ignore_filenames

api_key = config.authorization
url = f"http://www.omdbapi.com/?apikey={api_key}&type=movie&"


def get_movie_data(url, title):
    no_space_title = title.replace(" ", "%20")
    all_data_byte_string = urlopen(url + f"t={no_space_title}").read()
    all_data = json.loads(all_data_byte_string.decode("utf-8"))
    return all_data


def process_title(title):
    try:
        data_dict = get_movie_data(url, title)
        t = data_dict["Title"]
        y = data_dict["Year"]
        imdbid = data_dict["imdbID"]
        new_title = f"{t} ({y}) [imdbid-{imdbid}]"
        return new_title
    except:
        return title


# Test
# for title in examples:
#     process_title(title)


def rename_file(dir_path, file_name):
    if not file_name in ignore_filenames:
        if not file_name.startswith("."):
            file_name_root, file_extension = os.path.splitext(file_name)
            new_name = process_title(file_name_root)
            new_name_plus_ext = new_name + file_extension.lower()

            file_path_old_name = os.path.join(dir_path, file_name)
            file_path_new_name = os.path.join(dir_path, new_name_plus_ext)
            os.rename(file_path_old_name, file_path_new_name)


def rename_dir(dir_path, dir_name, dirs_to_rename):
    if not dir_name.startswith("."):
        print(dir_path)
        print(dir_name)
        new_name = process_title(dir_name)
        print(new_name)
        dir_path_old_name = os.path.join(dir_path, dir_name)
        dir_path_new_name = os.path.join(dir_path, new_name)
        dirs_to_rename.append((dir_path_old_name, dir_path_new_name))


def rename_dirs_and_files(path_to_process):
    dirs_to_rename = []  # This list is processed after the files are done
    if os.path.isdir(path_to_process):  # Directory
        for dir_path, dir_names, file_names in os.walk(path_to_process):
            for file_name in file_names:
                rename_file(dir_path, file_name)
            for dir_name in dir_names:
                rename_dir(dir_path, dir_name, dirs_to_rename)

        # Rename the root folder too
        root_dir_path = os.path.dirname(path_to_process)
        root_dir_name = os.path.basename(os.path.normpath(path_to_process))
        rename_dir(root_dir_path, root_dir_name, dirs_to_rename)
    else:  # File
        dir_path, file_name = os.path.split(path_to_process)
        rename_file(dir_path, file_name)

    # Rename the directories last
    for dir_tuple in dirs_to_rename:
        os.rename(dir_tuple[0], dir_tuple[1])


# Test
# test_dir = "/Users/neil/Downloads/Renaming Test Folder"
# rename_dirs_and_files(test_dir)


# Run the script
for individual_path in list_of_paths:
    rename_dirs_and_files(individual_path)
