import time
import json
import os


time_format = '%Y-%m-%d %H:%M:%S'


def get_time():
    return time.strftime(time_format, time.localtime(time.time()))


def get_json_content(file_name):
    with open(file_name, encoding='utf-8') as json_file:
        json_content = json.load(json_file)
        return json_content


def set_json_content(file_name, json_content):
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(json_content, json_file, indent=4, ensure_ascii=False)


def get_dirs_and_files(path):
    children = os.listdir(path)
    dirs = [child for child in children if os.path.isdir(os.path.join(path, child))]
    files = [child for child in children if os.path.isfile(os.path.join(path, child))]
    return dirs, files


def get_dirs(path):
    children = os.listdir(path)
    dirs = [child for child in children if os.path.isdir(os.path.join(path, child))]
    return dirs


def get_files(path):
    children = os.listdir(path)
    files = [child for child in children if os.path.isfile(os.path.join(path, child))]
    return files
