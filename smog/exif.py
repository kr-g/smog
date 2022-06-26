import os
import time

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from .gps import get_lat_lon


def exif_tags(file_path):
    img = Image.open(file_path)

    raw_data = img._getexif()

    tag_data = {}
    missing_tag = []

    try:
        for k, v in raw_data.items():
            t = TAGS.get(k, None)
            if t:
                tag_data[t] = v
            else:
                missing_tag.append(k)
    except Exception as ex:
        print("exif", file_path, ex)

    return raw_data, tag_data, missing_tag


def parse_exif_date(d):
    tm = time.strptime(d, "%Y:%m:%d %H:%M:%S")
    return tm


def get_original_date_time(tag_data):
    return parse_exif_date(tag_data["DateTimeOriginal"])


def get_date_time(tag_data):
    return parse_exif_date(tag_data["DateTime"])


def get_gps_info(tag_data):
    gps_raw = tag_data.get("GPSInfo", None)
    if gps_raw:
        gps_data = {}
        for t in gps_raw:
            idx = GPSTAGS.get(t, t)
            gps_data[idx] = gps_raw[t]
        return gps_raw, gps_data

    return gps_raw


if __name__ == "__main__":
    fnam = os.path.expanduser("~/media-repo/2022/06/20220605/DSC00026.JPG")
    raw_data, tag_data, missing_tag = exif_tags(fnam)
    for k, v in tag_data.items():
        print(k, v)
